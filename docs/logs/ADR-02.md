# ADR-02：架構轉向 JSON-params + 模板拼接 + 最小 schema 注入


| 欄位            | 值                                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Status        | Accepted                                                                                                                              |
| Date          | 2026-04-27                                                                                                                            |
| Supersedes    | ADR-01 §1.1（C4 L1 圖中 LLM 回傳 GraphQL string）、§2.1（Core Query Flow 假設 LLM 產 full GraphQL）、§3.1（流程描述）、§3.3（依賴清單缺 Pydantic 模型對 LLM 輸出的約束） |
| Superseded by | —                                                                                                                                     |


> ADR-01 假設 LLM 產 full GraphQL string；本文件記錄此假設被推翻、改為 LLM 產 JSON 參數 + Python 模板拼接的決策過程與後果。

---

## 1. Context

### 1.1 觸發點

ADR-01 寫定的流程是 `NL → LLM → GraphQL string → Execute → JSON`。Day 0 + Day 1 跑通後出現以下訊號：

1. **Schema fragment 注入炸 token** — 為了讓 LLM 知道 `stargazerCount` 不是 `stargazersCount`，要塞 ~200 行 GraphQL SDL；要支援 5 種 entity 就要塞 ~1000 行
2. **LLM 在重複勞動** — 每次都要產同樣的 `query { search(...) { nodes { ... on Repository { ... } } } }` 骨架，外層 GraphQL 形狀幾乎不變
3. **失敗模式集中在內層** — Break sweep 的 10 個失敗 case 沒有一個是「外層 GraphQL 結構錯」，全部是「內層 search query 字串錯」（gemma4 的 `stargazersCount`、Gemini 的 typo 自動修正、ambiguous 的 placeholder）

### 1.2 關鍵 insight（chat-01.log）

GitHub 的 search 是**雙層 DSL**：

```
外層 (GraphQL):     固定骨架，描述「我要回傳哪些欄位」
  └─ search(query: $q, type: $t, first: $n) {
       nodes { ... on Repository { 欄位列表 } }
     }

內層 (Search DSL):  變動內容，描述「我要篩選什麼」
  └─ "language:Rust topic:wasm stars:>1000 sort:stars-desc"
```

讓 LLM 產整段 GraphQL = 同時學兩個 DSL = 兩倍 token + 兩倍失敗面積。

### 1.3 評估設計問題（ambiguous queries）

NL 含模糊詞（"popular"、"active"、"small"）時，沒有單一正確的 search query。三種候選做法：

- **A. LLM 回 clarifying question**：打破 batch eval、ground truth 要 NLU 比對
- **B. LLM 同時產 query + flag 出自己做的假設**：可結構化評估、batch eval 不中斷
- **C. Refuse-to-guess**：UX 差、資訊量少於 B

採 B。

---

## 2. Decision

### 2.1 LLM output 改為結構化 JSON

LLM 不再產 GraphQL string，改產：

```json
{
  "search_query": "language:Python stars:>1000 sort:stars-desc",
  "type": "REPOSITORY",
  "first": 10,
  "assumptions": [
    {"term": "popular", "interpreted_as": "stars > 1000"}
  ]
}
```

四欄位約束：

- `search_query`：non-empty string；LLM 自帶 GitHub Search DSL 知識（**不注入 DSL 規則**）
- `type`：`Literal["DISCUSSION", "ISSUE", "REPOSITORY", "USER"]`（4 核心 SearchType，捨棄 3 個 ISSUE 變體）
- `first`：`int`，範圍 1–10（GitHub 上限是 100，take-home scope 不需要更多）
- `assumptions`：`list[{term, interpreted_as}]`，default `[]`；LLM 對 NL 模糊詞做的猜測必須結構化暴露

### 2.2 Python 端三層責任

```
LLM raw JSON → Pydantic SearchParams (validate) → fixed GraphQL template (render) → execute_graphql
```

- **Validate**：Pydantic model 強制 schema、`first` 範圍、`type` enum
- **Render**：固定 GraphQL template，用 GraphQL variables 而非字串拼接（避免 search_query 內含 quote 炸 query）
- **Execute**：`execute_graphql(query, token, variables=...)` — github.py 要支援 variables

### 2.3 注入內容（最小化原則）

**注入**：

- `SearchType` enum 4 核心值的描述（不是 SDL 原樣，是濃縮成 prompt 內 inline 文字）

**不注入**：

- `search()` field signature（template 已固定）
- `SearchResultItem` union（template 已固定 fragment）
- `SearchResultItemConnection`（template 已固定 selection set）
- 各 entity（Repository / User / ...）欄位定義（template 已固定）
- `SearchType` 三個 ISSUE 變體（ADVANCED / HYBRID / SEMANTIC）— 進階特性、30 cases 用不到、增加 LLM 選擇噪音
- **GitHub Search DSL 規則**（no OR、no parens、日期格式、qualifier 清單）— 注入會把任務從「NL→翻譯」降級為「LLM 抄規則」，扭曲對 LLM 真實 capability 的測試
- **type→entity 對照表**（type:USER 會回 Org、type:ISSUE 會回 PR）— 現階段不預先做假設；先觀察 V1 break-it 失敗模式，依結果決定是否補

### 2.4 Scope

只支援 `**search()`** 一個 top-level Query field。**不支援** Tier 1 其他 4 個（`repository`、`user`、`organization`、`viewer`）。完整論證見 material.md 對應段落。

### 2.5 已知不解的限制（README 用）

- **分頁**（"give me page 2"）：需要跨輪 cursor state 或 agent loop。當前 single-shot single-NL → single-query 架構結構性無法支援
- **GitHub Search 1000 筆硬上限**：任何「全部 X」類問題本質上不可解
- **GitHub Search 不支援 OR / parens**：`MIT or Apache licensed` 單次查不到
- **SearchType 沒有 `ORGANIZATION`**：「找 Anthropic 這個組織」要用 `type: USER`

---

## 3. Consequences

### 3.1 正面

- ✅ **LLM 任務面積縮小**：只填 4 個結構化欄位 vs 產整段 GraphQL
- ✅ **Token 用量降低**：prompt 不再需要 schema fragment（~1000 行 → ~50 行）
- ✅ **失敗面積結構化**：JSON 欄位驗證取代 GraphQL parse 驗證
- ✅ **三家 provider 共用同一條 prompt**（per-family slot 仍保留以利後續分歧）— per-family system prompt 結構不動
- ✅ **GraphQL injection 安全**：用 GraphQL variables 而非字串拼接，search_query 內含的引號不會炸 query
- ✅ **Eval 可同時量化兩種能力**：「會不會做 query」+「自不自覺自己在猜」（assumptions 欄位）

### 3.2 負面

- ❌ **不支援 lookup / traversal / mutation / aggregation** — 出 search 的 4 種根本不同 GitHub 查詢模式中只支援 1 種（Discovery）
- ❌ **不支援分頁** — 第二頁、跨頁聚合都做不到
- ❌ **OR 語意要 client-side union** — 單次 search 做不到
- ❌ **三個 ISSUE 變體（hybrid / semantic / advanced）暫時不支援** — `type` 限定 4 核心值

### 3.3 開放問題（依 break-it 結果決定）

- ⚠️ `type → entity` 對照表是否需要 — 依 V1 break-it 結果決定
- ⚠️ ISSUE 變體是否需要支援 — 依使用情境決定
- ⚠️ `assumptions` 的 schema 是否要更嚴格（例如限制 `term` 必須來自模糊詞白名單）— 依 eval 階段觀察決定
- ⚠️ Eval 30 cases 的 ambiguous bin 設計（之前提的 22+5+3 分布）— Part 2 階段才做、屆時再決

---

## 4. 實作影響範圍


| 檔案                       | 改動性質                                                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `src/gh_query/llm.py`    | 新增 `SearchParams` Pydantic model；改 `call_llm` 回傳 `SearchParams` 而非 `str`；JSON Schema 注入給 OpenAI/Gemini/Ollama 都要改 |
| `src/gh_query/prompt.py` | 改寫 V0 system prompt：要求 LLM 產 4 欄位 JSON；inline 列出 4 個 SearchType 值                                                 |
| `src/gh_query/github.py` | 新增 `build_search_graphql(params) -> (query, variables)`；`execute_graphql` 加 `variables` 參數                        |
| `src/gh_query/main.py`   | 流程改為 `call_llm → SearchParams → build_search_graphql → execute_graphql`                                           |
| `scripts/break_sweep.py` | call_llm 回傳型別變了，sweep 要記錄 SearchParams 而非 graphql string                                                          |


---

## 5. 不在本 ADR 涵蓋範圍

- 30 cases 的具體設計（Part 2 階段）
- Scorer 設計（Part 2 階段）
- per-family system prompt divergence（依 break-it 結果增量寫 ADR-03+）

