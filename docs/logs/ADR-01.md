# ADR-01：初始架構與工程決策


| 欄位            | 值                          |
| ------------- | -------------------------- |
| Status        | Accepted                   |
| Date          | 2026-04-25                 |
| Supersedes    | 已刪除的 5 份 AI-generated 規格文件 |
| Superseded by | —                          |


> 這份 ADR 是動手前的對齊紀錄，取代被砍掉的 5 份規格文件（architecture-and-design / bdd-scenarios / module-specs-and-tests / project-brief-and-prd / project-structure）— 那些是 AI 一次產出、過度抽象、未經驗證、跟考題 scope 不對等。
>
> 這份只記真正影響 code 的決策，每條都附 WHY。後續決策變更以 ADR-02、ADR-03 ... 增量記錄，**不修改本文件**（保留歷史過程）。

---

## 0. 為什麼有這份文件

考題明確要求 README 反映「**human engineering logic**」 — 不是 AI 產的規格摘要，而是工程判斷與 trade-off。
這份 ADR-01 是 README 的素材庫，記錄動手前的對齊與動手中的 pivot。

---

## 1. Scope Pivot 紀錄（最有價值的段落 — 寫 README 用）

### Pivot 1：從 8 份規格文件 → 工作筆記

**原本做法**：讓 AI 產 PRD、Architecture、BDD、Module Spec、Project Structure、Model Selection Strategy 等 8 份文件，總計 80KB+。

**修正觸發**：意識到 take-home 的尺度不需要 SaaS 級 SDLC 文件，而且 AI 產的「決策」我自己無法 defend。

**修正後**：保留 EXAM_PROMPT、background、model-selection-strategy（待精簡），其他刪除。

**學到**：考題評的是「正確判斷 scope」，不是「文件齊全度」。

---

### Pivot 2：從 Agent loop → Single-shot

**原本想法**：JD 提到 "AI agents、agentic workflows、MCP、CrewAI"，所以建構 while loop + function calling 架構，理由是「總結 repo 星星」「翻所有貢獻者各有幾個 repo」這類 query 看起來需要多步呼叫。

**修正觸發**：

1. 重讀考題用詞：「converts it into **a** structured API request or database query」「**the** perfect, correct structured query」 — 全單數。
2. 意識到 GraphQL 的 nested selection 本來就能在一發查到看似多步的問題：

```graphql
{
  repository(owner: "X", name: "Y") {
    collaborators(first: 100) {
      nodes {
        login
        repositories { totalCount }
      }
    }
  }
}
```

考題選 GraphQL 而非 REST，正是因為 single-shot 夠用。

**Due diligence（保留紀錄）**：實際在 Ollama 上驗證 `gemma4:e4b` **原生支援 function calling**（`tool_calls` 欄位有正常回傳）— Gemma 4 改進了過去 Gemma 系列無 tool use 的弱點。但**有意識選擇不用** — capability 存在 ≠ 該用。

**學到**：被 JD 釣走 = 沒抓到考題重點。JD 描述的是「考過後做的工作」，考題就是考題。

---

### Pivot 3：從引入 SDK → raw httpx

**原本想法**：用 `openai` SDK 跑 OpenAI + NVIDIA NIM（OpenAI-compat），用 `google-genai` SDK 跑 Gemini。

**修正觸發**：意識到 structured output 強約束（`json_schema` / `responseSchema`）是 **API 層特性，不是 SDK 層** — raw HTTP 一樣拿得到。

**修正後**：所有 provider 用 `httpx.post()` 直接打。三個 provider × ~30 行 = 90 行。

**好處**：

- 請求 body 100% 透明，可在 README 直接展示三家 API 差異。
- 少三個依賴。
- 部分 Part 2 的多模型分析價值就在「三家 API 形狀的差異」 — 用 SDK 會抹平這個差異。

---

## 2. 架構決策

### 2.1 流程

```
NL input → build_prompt() → HTTP call to LLM → parse JSON → execute_graphql() → JSON to stdout
```

一條線，無 loop、無 retry、無 fallback。LLM 失敗就 fail fast 印錯誤。

### 2.2 檔案結構（扁平 5 檔）

```
src/gh_query/
├── __init__.py
├── main.py          # Typer CLI 入口
├── llm.py           # call_openai / call_gemini / call_ollama
├── github.py        # execute_graphql(query) -> dict
├── prompt.py        # build_prompt(nl) + schema fragments
└── scorer.py        # GraphQL AST normalize + 比對

eval/
├── test_cases.json  # 30 cases
├── run_eval.py
└── results/

tests/
├── test_scorer.py
└── test_prompt.py

.env.example
.gitignore
pyproject.toml
README.md
```

### 2.3 為什麼不用 Clean Architecture / Protocol / Layer

- 3 個 provider、不會動態切換 — `if model.startswith("gpt"):` 就夠用。
- Take-home 規模塞四層 abstraction 是 over-engineering，面試官第一反應會是「做小事像做大事」。
- 抽象成本（Protocol、Router、依賴注入）不會在這個 scope 內回收。

---

## 3. 技術選擇

### 3.1 Provider × Model


| Slot        | Model                           | API endpoint                                 | 為什麼                                                                                                                                          |
| ----------- | ------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Closed #1   | `gpt-5.4-mini`                  | OpenAI `/v1/chat/completions`                | 已 curl 驗證可用；strict json_schema 在 sampling layer 硬約束。                                                                                         |
| Closed #2   | `gemini-3.1-flash-lite-preview` | Google `:generateContent`                    | 已 curl 驗證；3.1 是 Google 下一代。**選 -preview 而非 stable 2.5**，因為 `gemini-2.5-flash-lite` 已宣布 2026-07-22 停用 — 走 deprecated stable 的風險大於 preview 不穩。 |
| Open-weight | `gemma4:e4b` (Ollama 本機)        | `http://localhost:11434/v1/chat/completions` | 真正的 open-weight，本機跑無 cloud 依賴。已驗證可用 + 支援 tool calling（雖然不用）。                                                                                 |


### 3.2 Open-weight 為什麼選 Ollama 不選 NVIDIA NIM

NIM 上的 DeepSeek V4 Flash 是「open weights, served via closed managed API」。考題要 "open-weight"，嚴格解釋下 NIM 不算（user 沒持有 weights、沒控制 inference 環境）。Ollama 本機跑無爭議。

副效果：少接一個 provider，code 更乾淨。

### 3.3 依賴清單

```toml
[project.dependencies]
httpx                # HTTP client，取代所有 LLM SDK
pydantic             # 結果型別驗證
pydantic-settings    # .env loading
typer                # CLI framework
graphql-core         # AST parsing (scorer 用)

[dev]
pytest
```

刻意不引入：`openai`、`google-genai`、`gql`、`pytest-httpx`（測試先用真 API 跑小 case）。

---

## 4. Prompt 設計（待動工驗證）

### 4.1 System prompt 結構

1. **Role + task**：「You are a GitHub GraphQL query generator...」
2. **Schema fragment**：依 NL 的 entity 類型注入（repository / issue / pull_request / user / organization），每段約 20 個常用欄位。
3. **Output constraint**：「Respond ONLY with `{"query": "<graphql>"}`. No explanation. No markdown.」

### 4.2 Entity detection（簡單 keyword match）


| Entity       | Keywords                               |
| ------------ | -------------------------------------- |
| repository   | repo, repository, star, fork, language |
| issue        | issue, bug, open, closed, label        |
| pull_request | PR, pull request, merge, review        |
| user         | user, developer, contributor, follower |
| organization | org, organization, team, member        |
| fallback     | （以上都不中 → 注入全部 5 段 schema）              |


Fallback 多花 token 換覆蓋率。如果動手後發現 token 太多再優化。

---

## 5. Scoring（Part 2 用）

### 5.1 三檔分數


| 分數  | 條件                                              |
| --- | ----------------------------------------------- |
| 1.0 | AST normalize 後 exact match（field 排序、空白都標準化）    |
| 0.5 | 同 root entity + 同 operation，但 selection set 有缺漏 |
| 0.0 | parse error / 不同 entity / 不同 operation          |


### 5.2 為什麼三檔不是連續 0~1

- 連續分數需要定義 partial 的權重（每個欄位幾分？），這個本身就是另一場辯論。
- Take-home scope 內，三檔已經足夠分辨「對 / 部分對 / 錯」。
- README 可以承認這個簡化選擇 + 解釋為什麼足夠。

### 5.3 85% accuracy 怎麼算

`score == 1.0` 的數量 / 總數。0.5 不算對。考題的 threshold 是嚴格 binary。

---

## 6. 實作順序（建議節奏）


| 階段        | 步驟                                    | 驗證                                                 |
| --------- | ------------------------------------- | -------------------------------------------------- |
| **Day 0** | 骨架（pyproject.toml、.env、.gitignore、目錄） | 能 `python -m gh_query --help`                      |
|           | `github.py` execute_graphql()         | hardcoded query 跑通真 API                            |
|           | `llm.py` `call_openai()`              | 一個寫死 NL → 印出合法 GraphQL                             |
|           | `main.py` 串起來                         | `gh-query "stars of torvalds/linux"` 跑通            |
| **Day 1** | `prompt.py` 抽出 + schema fragments     | 5 種 entity 各跑一個                                    |
|           | `call_gemini()` + `call_ollama()`     | 同 prompt 三家都產出 GraphQL                             |
|           | "Break It" 階段                         | 手動測 5-10 個 adversarial case，記下失敗模式                 |
|           | "Harden & Fix" 階段                     | 針對最關鍵的失敗修 prompt 或加前置檢查                            |
| **Day 2** | `scorer.py`                           | unit test 過 6 個基本 case                             |
|           | `eval/test_cases.json` × 30           | 含 multi-field、filter、pagination、typo、非英文、ambiguous |
|           | `eval/run_eval.py`                    | 三個 model × 30 case 跑完輸出 results/*.json             |
|           | 迭代 prompt                             | 三個 model 都過 0.85                                   |
|           | README                                | 親手寫，不複製這份 ADR-01，但可引用其中的決策                         |


---

## 7. README 必寫段落 checklist

寫 README 時**必須親手寫**（不是貼 ADR-01）：

- 為什麼選 GitHub GraphQL 不選 REST — nested selection 取消 multi-step 需求
- 為什麼 raw HTTP 不用 SDK — API 層 vs SDK 層的關係 + 多模型差異分析的價值
- 為什麼 Gemini 選 `-preview` — `gemini-2.5-flash-lite` 2026-07-22 停用，deprecation > preview 風險
- 為什麼 open-weight 選本機 Ollama — 嚴格定義 vs NIM-served 的爭議
- 為什麼 Single-shot 不用 agent loop — 考題單數用詞 + GraphQL nested 能力 + 我親自驗證 gemma4 有 tool use 但選擇不用
- "Break It" 真實踩到的 5+ 失敗 case 與分析
- 哪些 case 沒修，為什麼**根本上**難解（考題明確要求）
- 三個 model 的 accuracy 比較 + initial wrong patterns
- Eval design：ground truth 怎麼定、scorer 為什麼三檔、85% 怎麼計算

---

## 8. 安全紀錄

- 對話中曾誤貼真 `OPENAI_API_KEY` / `GOOGLE_API_KEY` 進終端機。
- User 確認：個人機器、無 git 追蹤、不需 rotate。
- 仍應確保 `.env` 在 `.gitignore`，且 commit 前 `git status` 檢查。

---

## 9. 待動手後可能要修正的假設

這些是現在拍腦袋的決定，動工後可能要改：

- Schema fragment 大小（20 欄位是猜的，可能要看 token 數調整）
- Fallback 是否真的要注入全部 5 段（也許保守 3 段就夠）
- Scorer 三檔是否足夠（也許 partial 還要再分）
- 30 cases 的分布（現在的草稿分類可能跑下去就要重整）

**這份 ADR-01 是工作紀錄，後續決策變更以 ADR-02、ADR-03 ... 增量記錄，不修改本文件。**