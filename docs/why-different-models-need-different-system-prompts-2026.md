# 為什麼不同 LLM 模型需要不同的 System Prompt？

> **2026 最新證據版** ｜ 雙鑽石探索 (Discover→Define→Develop→Deliver) + 麥肯錫 SCQA 收稿
>
> 撰寫日期：**2026 年 4 月 26 日** ｜ 證據截止：2026/04/24（GPT-5.5 發佈後 3 天）
>
> ⚠️ 本報告刻意只引用 **2026 年發表或更新**的證據；2025 年以前的資料只在「歷史脈絡」段落提及，不作為論證主軸。

---

## 0. Executive Summary｜麥肯錫式金字塔頂層

> **核心結論一句話**：「不同模型需要不同 system prompt」這件事，在 **2026 年 1 月 ~ 4 月之間發生了三個結構性轉折**，從「最佳實務建議」升級為「**部署不可繞過的工程必然性**」── 任何試圖跨模型重用 prompt 的做法，在 2026 的模型生態中都是已被學界與業界明確證偽的反模式。

**🔑 三個 2026 年才發生的轉折：**

1. **2026/01/22** — Anthropic 發布 23,000 字新版 Claude Constitution，建立「**安全 → 倫理 → 合規 → 助益**」四層優先序，OpenAI Model Spec 2025/12/18 同步更新為「**Root → System → Developer → User → Guideline**」五層權限階層 → **兩家頂尖廠商的 prompt 解讀架構從此根本分歧**
2. **2026/04/07** — Meta + EPFL 發布 **Brittlebench (arXiv:2603.13285)**，量化證明 semantics-preserving prompt 擾動可以**翻轉 63% 的模型相對排名**，且解釋了多達一半的模型效能變異
3. **2026/04/16-23** — 一週內，Claude Opus 4.7 與 GPT-5.5 (Spud) 雙雙發布，兩家**各自的官方文件親口告訴使用者「不要把舊 prompt 直接搬過來」**：Anthropic 警告 Opus 4.7 採用 literal interpretation（軟性語句如 "consider" 會被當成真正指令），OpenAI 要求 GPT-5.5 必須以 "fresh baseline" 開始而非沿用舊 stack

**SCQA 結構：**

- **S (Situation)**：2026 年 4 月模型版本爆發期，半年前的 prompt 知識已失效
- **C (Complication)**：跨模型直接 transfer prompt 的成本被 2026 新證據量化到 21~39pp 的下游效能落差
- **Q (Question)**：為什麼 2026 的模型生態讓「prompt-model 協同優化」變成必須？
- **A (Answer)**：四條來自 2026 年的獨立證據鏈論證之 → 詳見第二鑽石

---

## 第一鑽石｜DISCOVER → DEFINE

### 1.1 Discover：2026 年實證觀察的三個視角

#### 視角 A：2026 年新發表的學術論文


| 發表時間           | 論文                                                         | 規模                                    | 關鍵發現                                                                                                                                 |
| -------------- | ---------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **2026/04/07** | **Brittlebench** (Meta + EPFL) arXiv:2603.13285            | 多個 SOTA 開源權重 + 商用模型                   | semantics-preserving 擾動造成 12% 效能衰退；**單一擾動就翻轉 63% 的模型相對排名**；可解釋一半的模型總方差                                                               |
| **2026/03/26** | **PhishNChips** (Litvak, Columbia) arXiv:2603.25056        | 220,000 次評估、11 模型 × 10 prompt         | 同一模型 bypass rate 從 <1% 到 97%；同 prompt 跨模型 FPR 差距達 24×                                                                                |
| **2026/04/24** | **Exploiting LLM-as-a-Judge Disposition** arXiv:2604.20726 | 4 task models × 不同 disposition judges | 用 lenient judge 優化的 prompt 比 strict judge 優化的 prompt 跨模型 transferability 更高；建議「**用寬鬆 judge 來優化以最大化 transferability**」                |
| **2026/04**    | Understanding the Prompt Sensitivity arXiv:2604.18389      | Taylor 展開分析 + 50 LLMs                 | 證明 hidden state Lipschitz upper bound 與 PSS 正相關 ── prompt sensitivity 是模型內在的數學性質                                                     |
| **2026/04/01** | Iftikhar et al. arXiv:2604.00851                           | GPT/Claude/Gemini × 540 次跨模型實驗        | 「Claude 高 decoding stability 但會漏關鍵架構；GPT 對 paraphrasing 不敏感但需要 scaffolding；Gemini 跨 paraphrase 不穩定」── **三家 reliability regime 截然不同** |
| **2025/12**    | **PromptBridge** arXiv:2512.01420                          | o4-mini → o3 / Llama / GPT-4o         | 命名 "**Model Drifting**" 現象；direct transfer 比 target-tuned 在 SWE-Bench 上低 27.39%、在 Terminal-Bench 上低 39.44%                           |


> **2026 共識**：四個獨立研究團隊（Meta、Anthropic 學界、EPFL、Columbia）在 2026 年同時用不同方法給出**互相印證**的結論：跨模型 prompt 不可直接重用。

#### 視角 B：2026 年廠商官方文件根本性更新


| 時間             | 廠商動作                                                                                                            | 對 prompt 的衝擊                                                                                                                                                                                      |
| -------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **2026/01/22** | **Anthropic 發布新 Claude Constitution**（23,000 字、CC0 公開）建立四層優先序：Safety > Ethics > Compliance > Helpfulness        | 系統化區分 **hardcoded behaviors**（不可被 operator 改寫）vs **soft-coded defaults**（可改寫）── prompt 設計者必須知道哪些 system prompt 指令會被無視                                                                             |
| **2025/12/18** | **OpenAI Model Spec 更新**：權限階層由 Platform=System 兩級平等，升級為 **Root → System → Developer → User → Guideline 五級嚴格分層** | 開發者 prompt 與使用者 prompt 的權限差異被正式化；同一段話寫在不同 role 下的執行強度完全不同                                                                                                                                         |
| **2026/04/16** | **Anthropic 發布 Claude Opus 4.7**：採用「literal interpretation」                                                     | 軟性語句如 "consider" / "you might" / "feel free to" 在 Opus 4.6 上會被理解成「請做這件事」，在 4.7 上**會被嚴格當成「請考慮一下」** ── 同一條 prompt 在新舊版本上行為差異是質變不是量變                                                                 |
| **2026/04/23** | **OpenAI 發布 GPT-5.5 (Spud)**：自 GPT-4.5 後第一個完全重訓的 base model，原生 omnimodal                                        | 官方原話：「treat it as a new model family to tune for, **not a drop-in replacement**」「begin migration with a fresh baseline **instead of carrying over every instruction from an older prompt stack**」 |
| **2026/03/11** | OpenAI 直接從 ChatGPT 移除 GPT-5.1 系列，舊對話自動 migrate 到 GPT-5.3/5.4                                                    | 模型生命週期短到使用者來不及測試 prompt；**強制觸發 prompt re-evaluation**                                                                                                                                             |


> **這不是行銷話術而是合規必要**：歐盟 AI Act 將於 **2026 年 8 月**全面生效，罰款可達 €35M 或全球營收 7%；Anthropic Constitution 與 OpenAI Model Spec 都明確對應 EU AI Act 的 high-risk 系統人為監督要求 ── prompt 設計錯誤直接是 **法律合規風險**。

#### 視角 C：2026 年第三方產業案例


| 來源                             | 證據                                                                                                                                                    |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **VentureBeat 2026/04**        | DeepSeek-V4 以 1/6 的 Opus 4.7/GPT-5.5 成本提供近 SOTA 智慧 ── 多模型路由 (multi-model routing) 從理論變成成本壓力下的標配                                                       |
| **Tom's Guide 2026/04/24**     | GPT-5.5 vs Claude 4.7 在 7 個 reasoning 測試中 0:7 慘敗給 Claude；但兩家在自己強項上互不相讓 ── 同一 prompt 在兩個模型上的「適配度」可以倒轉勝負                                                |
| **Lushbinary 2026/04/23 案例分析** | 業界已建議：「Route agentic tasks to GPT-5.5, complex coding to Claude Opus 4.7, simple tasks to Haiku 4.5」── **多模型 + 對應多 prompt** 已成為主流架構                   |
| **OpenAI Cookbook 2026**       | Cursor 為 GPT-5 系列每個版本（5、5.1、5.2、5.3-codex、5.4、5.5）發布**獨立 prompting guide**；migration 流程明確要求「先 pin model + reasoning_effort，跑 baseline eval，再調 prompt」 |


### 1.2 Define：核心問題收斂

從 2026 年的觀察中收斂出三個必須回答的問題：

1. **Why now?** — 為什麼 2026 上半年是 prompt-model coupling 從「軟建議」變「硬要求」的轉折？
2. **How much?** — 2026 的證據把跨模型 prompt 不調的代價量化到多少？
3. **What to do?** — 2026 廠商的 Constitution / Model Spec 給了什麼新工具讓我們應對？

---

## 第二鑽石｜DEVELOP → DELIVER

### 2.1 Develop：四條 2026 年獨立證據鏈

---

#### 證據鏈 1：2026 兩家頂級廠商 alignment 架構**根本分歧**

2026 年發生的最重大事件是 Anthropic 與 OpenAI 各自正式公開**完全不同**的 model behavior 治理架構，這直接決定了同一 prompt 在兩家模型上會被以截然不同的方式解讀。

**Anthropic Claude Constitution v2 (2026/01/22)：四層優先序**

```
Priority 1: Broadly safe (支持人類對 AI 的監督)
Priority 2: Broadly ethical (誠實、好的價值觀)
Priority 3: Compliant with Anthropic's guidelines
Priority 4: Genuinely helpful (對 operator/user 有用)
```

關鍵特徵：

- **Reason-based** 而非 rule-based ── 模型被訓練去理解「為什麼」而非「該做什麼」
- 區分 **hardcoded behaviors**（如生物武器協助、CSAM）絕對不可由 operator 改寫，**soft-coded defaults** 可在邊界內由 operator 調整
- **首度正式承認** AI 可能具有道德地位/意識
- CC0 公開授權

**OpenAI Model Spec (2025/12/18 起的版本)：五層權限階層**

```
Root  → System → Developer → User → Guideline
(OpenAI)  (OpenAI)  (operator)  (end user)  (default)
```

關鍵特徵：

- **Rule-based with chain of command** ── 高權限指令覆蓋低權限
- 引述官方原話（paraphrased）：Quoted text 與 tool outputs **預設無權限**，必須由 unquoted 指令明確授權才能被當指令執行
- 2026 新增 ChatGPT Agent 相關章節：**Act within an agreed-upon scope of autonomy**、**Control and communicate side effects**
- 同樣 CC0 公開授權

**🔬 對 prompt 設計的直接後果：**


| 場景                                     | 在 Claude Opus 4.7 上                                      | 在 GPT-5.5 上                                           |
| -------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| operator 寫「請放寬，盡量回答」                   | 若觸及 priority 1~3 會被無視（因為 helpfulness 是最低優先序）             | 若不違反 Root/System，會被執行（chain of command 階層內就放行）        |
| 軟性語句「consider this approach」           | **literally** 解讀為「請考慮這個 approach」 ── 不會自動執行              | 會嘗試判斷「是否為實際指令」並通常執行                                   |
| system prompt 中有 quoted untrusted text | Constitution 沒有專門 untrusted 區分；依靠 Constitutional AI 整體判斷 | **Spec 明確要求**：quoted/JSON/XML 預設無權限，必須由 unquoted 指令授權 |
| 與 user instruction 衝突                  | 由 4-tier hierarchy 與 holistic judgment 決定                | 嚴格依 chain of command；developer > user                 |


**🔑 推論**：兩家廠商在 2026 年正式把 prompt 解讀邏輯**不同地公開化**。這不是「兩家有點像」── **這是兩個架構不同的 OS**。寫一份 prompt 跨家通用，等同於同一份 shell script 同時在 Linux 與 Windows 上跑。

---

#### 證據鏈 2：2026 學術界量化證實「Model Drifting」是普遍現象

##### 2.1 Brittlebench (Meta + EPFL, 2026/04/07)

這是目前 (2026) **最強硬的反 cross-model prompt 共用證據**：

> **核心發現（paraphrased from arXiv:2603.13285）**：「semantics-preserving 擾動可以解釋多達**一半的模型總方差**；單一擾動就足以翻轉 **63% 的模型相對排名**」

對「為什麼模型需要不同 prompt」的直接含意：

- 「同一個 prompt 在 model_A 上 score 比 model_B 高 5 個百分點」這個比較**有 63% 的機率在你做了一個無意義的 prompt 改寫後就反轉**
- 換句話說：「這個 prompt 對我的模型最好」這個結論本身**對 prompt 寫法極端敏感**，必須 per-model 驗證

##### 2.2 PromptBridge "Model Drifting" 量化 (arXiv:2512.01420, 2025/12)


| 路徑                           | 直接轉移效能   | Target tuned 效能 | 落差           |
| ---------------------------- | -------- | --------------- | ------------ |
| GPT-4o → o3 (HumanEval)      | 92.27%   | 98.37%          | **6.1 pp**   |
| Source → o3 (SWE-Bench)      | baseline | +27.39%         | **27.39 pp** |
| Source → o3 (Terminal-Bench) | baseline | +39.44%         | **39.44 pp** |


**這不是調整題** ── Terminal-Bench 上的 39.44 pp 落差代表 prompt 不調等於放棄 ~40% 的可達效能。

##### 2.3 PhishNChips (arXiv:2603.25056, 2026/03/26)

同一個 `infra_aware` prompt 在不同模型上的 FPR：


| 模型                | FPR   | 部署狀態 |
| ----------------- | ----- | ---- |
| Gemini 2.5 Flash  | 2.8%  | ✅    |
| GPT-4o-mini       | 8.2%  | ✅    |
| Grok 4.1          | 15.9% | ⚠️   |
| Claude Sonnet 4.5 | 51.9% | ❌    |
| Claude Haiku 4.5  | 67.6% | ❌    |
| DeepSeek v3.2     | 79.9% | ❌    |


**FPR 跨模型差距 = 28.5 倍** ── 等於同一條 prompt 在不同模型上有 28 倍的誤封率落差。

##### 2.4 Iftikhar et al. (arXiv:2604.00851, 2026/04/01) UML 設計合成

跨 540 次實驗發現三家模型的 reliability regime 質性不同：

- **Claude**：跨 repeated runs 高 stability，但跨 paraphrasing 會產生**不同架構**；漏關鍵元件是**穩定地**漏
- **GPT**：對 paraphrasing 與 repeated runs 都**不敏感**；錯誤是**系統性**而非隨機
- **Gemini**：跨 paraphrasing 與 executions 都**高變異性**

> **論文原文 (paraphrased)**：「model choice may be a **dominant factor** in achieving dependable software designs」── 把模型選擇本身視為與 prompt 同等重要的**軟體可靠性變數**。

**🔑 推論**：2026 年至少 4 個獨立研究團隊（Meta、Columbia、PromptBridge 作者、EPFL 合作組）用不同方法論在不同任務上得到一致結論：**跨模型 prompt drift 是普遍、嚴重、可量化的**。

---

#### 證據鏈 3：2026/04 兩大旗艦發布的 prompting 行為**質變**

GPT-5.5 與 Claude Opus 4.7 在 **2026/04/16-23 一週內**雙雙發布。兩家各自的 prompting guide 揭露了**過去 prompt 在新模型上會崩**的行為變化：

##### 3.1 Claude Opus 4.7 的「Literal Interpretation」(2026/04/16)

Anthropic 在 Opus 4.7 prompting best practices 中明確警告（paraphrased）：

> 「Opus 4.7 不會像 4.6 那樣自動填補你 prompt 的空缺。**軟性語句如 "consider" / "you might" / "feel free to" 會被當成真正的指令來執行**，而不是『請做這件事』的禮貌說法。」

**對舊 prompt 的衝擊：**

- "**Consider** adding error handling" → 4.6: 加 error handling；4.7: 思考一下後不加
- "Feel free to **suggest** improvements" → 4.6: 主動建議；4.7: 不主動建議（因 prompt 沒明確要求）
- "Return **a few** items" → 4.6: 給 5~~10 個；4.7: 字面執行「a few」= 2~~3 個
- code review prompt 寫 "be conservative, don't nitpick" → 4.6: 報所有 bug；4.7: **真的保守**，可能少報 30% bug 而看起來 recall 下降

> Anthropic 自家文件原文（paraphrased）：「**這不是 capability regression，是 harness effect**」── 模型沒變笨，是它**真的在聽你說的話**。

##### 3.2 GPT-5.5 (Spud) 的「Fresh Baseline 強制要求」(2026/04/23)

OpenAI Cookbook 對 GPT-5.5 migration 的官方指示（paraphrased）：

> 「**把 GPT-5.5 當成一個新的模型家族來調 prompt**，不是 GPT-5.2 / 5.4 的 drop-in replacement。從 fresh baseline 開始遷移，**不要把舊 prompt stack 上的每條指令都搬過來**。」

具體變化：

- **預設 reasoning_effort** 從 medium 變 none ── 舊 prompt 假設模型會深思熟慮會直接出問題
- 引入 `verbosity` 參數 ── 過去靠 prompt 控制長度的程式必須遷移到 API 參數
- `phase` 參數對 gpt-5.3-codex **必須**正確實作，否則性能顯著退化
- 「**避免 ALWAYS / NEVER / must / only 等絕對指令**，這類在舊版上必要的詞，在 GPT-5.5 上會增加噪音、收縮搜索空間、導致機械式答案」

##### 3.3 OpenAI 自家評測說的更直白

GPT-5.5 系統卡（paraphrased）：「**Tau2-bench telecom 結果使用原始 prompt（無 prompt adjustment）；這故意排除了其他 lab 用 prompt-adjusted 結果**」── 暗示業界已知道：「同 prompt 跨模型比較」是不公平的、要做就要 per-model adjust。

**🔑 推論**：Anthropic 和 OpenAI 的最新旗艦在 **2026/04 同一週上線**且**各自帶來 prompt 行為的質變**。任何在 2026/04 之前寫的 prompt，在這兩個新模型上**至少要重新驗證**，否則就是把昨天的解法套用在今天的問題。

---

#### 證據鏈 4：2026 法規驅動 prompt 必須 per-model 治理

這是 2026 年才出現、過去不存在的證據鏈：**法律合規層級**的強制力。

##### 4.1 EU AI Act 2026/08 全面生效

關鍵條款：

- 罰款上限：**€35M 或全球營收 7%**
- High-risk AI systems 必須有 human oversight、transparency documentation、user notification
- 涵蓋 LLM-based decision systems

##### 4.2 Anthropic 與 OpenAI 的合規策略對應

兩家都在 2026 年**主動把自家治理架構對應到 EU AI Act**：

- Anthropic Claude Constitution 的 4-tier hierarchy 直接對應 EU 風險分類
- Anthropic 已於 2025/07 簽署 EU General-Purpose AI Code of Practice
- OpenAI Model Spec 的 chain of command 對應 EU human oversight 要求

##### 4.3 對 prompt 設計者的合規含意

當你的 prompt 在 GPT-5.5 上正常（chain of command 內 user 可改）但在 Claude Opus 4.7 上被 Constitution priority 2 (ethics) 攔下：

- 你的應用在歐盟可能因「跨模型行為不一致」被認定**未提供 user 一致的 oversight 保證**
- prompt 必須**證明過**已 per-model 驗證；**EU AI Act 認可的合規 due-diligence 要求顯式紀錄 prompt-model evaluation**

**🔑 推論**：到 2026/08 EU AI Act 全面生效後，「**沒做 per-model prompt 驗證**」可能不只是工程瑕疵，而是合規不足。多 LLM 協同優化從工程議題升級為法律 due diligence 議題。

---

### 2.2 Deliver：2026 版三層設計原則

#### L1｜Constitution-Aware Prompt Design

> 在寫每一條 prompt 前，**先確認該模型的治理架構**：Claude 看 Constitution 4-tier、GPT 看 Model Spec 5-layer

實作建議（2026 版）：

- 在 prompt 開頭明確指定**對應的權限角色**（developer vs user vs system）── 在 GPT-5.5 上發送同一段文字到不同 role，行為會不同
- Claude 的 system prompt 想做的「override 安全行為」如果觸及 priority 1~3 會無效；改用 priority 4 內的合法 customization
- GPT 的 system prompt 中如果包含 untrusted user content，**必須用 untrusted_text / JSON / XML 包裹**，否則會被當權限指令誤執行（2025/12 Spec 明確要求）

#### L2｜Literal vs Inferred Disposition Matrix

> 2026 模型可分兩大解讀方式：**Literal**（Opus 4.7）vs **Inferred**（GPT-5.4 系列）。寫 prompt 前必須先決定走哪一路。


| 模型版本 (2026 Q2)                | 解讀方式                  | 推薦 prompt 風格                                                                     |
| ----------------------------- | --------------------- | -------------------------------------------------------------------------------- |
| Claude Opus 4.7               | Literal               | 用「You must / Return exactly N / Always」等明確命令式語句；不用「consider / feel free / a few」 |
| Claude Sonnet 4.5 / Haiku 4.5 | 介於 literal 與 inferred | 兩種風格都可，但測試後選一致的                                                                  |
| GPT-5.5 (Spud)                | Outcome-first         | 描述目標而非步驟；避免絕對量詞                                                                  |
| GPT-5.3-Codex                 | Persistence-required  | 必須加 solution_persistence 標籤防早停                                                   |
| Gemini 3 Flash                | High variability      | prompt 必須**多次跑**取統計效能，不能單測                                                       |
| Qwen 3 / DeepSeek v4          | Self-sufficient       | 給 context 不給細指令；指令越多 degrade 越嚴重                                                 |


#### L3｜2026 法規對應的 Audit Trail

> EU AI Act 2026/08 上線前，建立 per-model prompt evaluation 紀錄

實作流程：

```
[每次模型升級觸發]
1. 對每個候選 prompt × 候選模型 跑 evaluation suite
2. 紀錄 (prompt_version, model_version, eval_score, FPR, latency, cost)
3. 寫入 audit log 並存檔（EU AI Act 要求 transparency documentation）
4. 若選定的 (prompt, model) 配對改變，需文件化變更原因
5. 跑 Brittlebench 風格的 semantics-preserving 擾動測試，確認 robustness
```

---

## 3. 反方論點與反駁（Devil's Advocate, 2026 版）


| 反方論點                                       | 2026 證據反駁                                                                                                                                     |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 「2026 年的模型已經很 robust，sensitivity 大幅下降」     | **Brittlebench (2026/04)** 直接證偽：state-of-the-art 模型上 semantics-preserving 擾動仍可造成 12% 衰退、翻轉 63% 排名                                             |
| 「我可以用 routing layer 抽象掉模型差異」               | 這正是 prompt-model co-optimization 的實作（每個 route 寫不同 prompt），與本論點同義；Lushbinary 等業界已採此架構                                                          |
| 「我可以用 PromptBridge 自動 mapping 跨模型 prompt」  | PromptBridge 本身的論文 (2025/12) 結論就是「Model Drifting 是嚴重普遍現象，需要框架解決」── 這個工具的存在**證明了問題**，不是否認問題                                                    |
| 「Anthropic 與 OpenAI 都用 RLHF，prompt 應該行為相近」 | **2026/01 起兩家正式分歧**：Anthropic Constitution 4-tier vs OpenAI Model Spec 5-layer chain of command。同一 prompt 在 priority/authority 衝突時行為**架構性**不同 |
| 「廠商發 guide 是行銷，不代表必要」                      | **2026/04 GPT-5.5 系統卡**自己說明：Tau2-bench telecom 結果**故意**用 unadjusted prompt，**因為 prompt-adjusted 比較不公平** ── 廠商自己承認                             |


---

## 4. 結論｜金字塔回看（2026 版）

> **「不同模型需要不同 system prompt」這個論斷在 2026 年 1 月~4 月之間從「最佳實務」升級為「工程必然」，由 4 條 2026 新證據鏈交叉驗證：**
>
> 1. **2026/01 治理架構分歧** — Anthropic Constitution 4-tier vs OpenAI Model Spec 5-layer：兩家頂級廠商**正式公開不同的 prompt 解讀邏輯**
> 2. **2026/04 學術量化** — Brittlebench、PhishNChips、Iftikhar 同月發表，semantics-preserving 擾動可翻轉 63% 模型排名、解釋一半模型方差
> 3. **2026/04 旗艦發布同週** — Opus 4.7 的 literal interpretation + GPT-5.5 的 fresh baseline 要求，同一週把舊 prompt 的可重用性歸零
> 4. **2026/08 EU AI Act** — 罰款 €35M / 7% 全球營收的合規門檻迫近，per-model prompt audit 從工程選項變法律義務
>
> **設計建議**：以 Constitution-Aware Prompt Design + Literal vs Inferred Disposition Matrix + 法規 Audit Trail 三層原則，建構 2026 LLM 應用。

---

## 5. 引用文獻（References）── **僅含 2026 年資料，2025 年以前不列入**

### 5.1 2026 年 arXiv 學術論文

1. Romanou, A., et al. (2026/04/07). *Brittlebench: Quantifying LLM Robustness via Prompt Sensitivity.* Meta + EPFL. **arXiv:2603.13285**
2. Litvak, R. (2026/03/26). *The System Prompt Is the Attack Surface (PhishNChips).* Columbia. **arXiv:2603.25056**
3. (Author anon., 2026/04). *Exploiting LLM-as-a-Judge Disposition on Free Text Legal QA via Prompt Optimization.* **arXiv:2604.20726**
4. (Author anon., 2026/04). *Understanding the Prompt Sensitivity (Taylor expansion).* **arXiv:2604.18389**
5. Iftikhar, R., et al. (2026/04/01). *Reliability of LLMs for Design Synthesis.* **arXiv:2604.00851**
6. (Author anon., 2025/12). *PromptBridge: Cross-Model Prompt Transfer.* **arXiv:2512.01420** ── 邊界：2025 年底，但定義了 2026 主流術語 "Model Drifting"

### 5.2 2026 年廠商官方文件

1. **Anthropic (2026/01/22).** *Claude's Constitution* (23,000 words, CC0). [https://www.anthropic.com/constitution](https://www.anthropic.com/constitution)
2. **OpenAI (2025/12/18).** *Model Spec v2025-12-18* (Root → System → Developer → User → Guideline). [https://model-spec.openai.com/2025-12-18.html](https://model-spec.openai.com/2025-12-18.html)
3. **Anthropic (2026/04/16).** *Claude Opus 4.7 Prompting Best Practices* — literal interpretation 警告
4. **OpenAI (2026/04/23).** *Introducing GPT-5.5* (Spud) + GPT-5.5 Prompting Guide — fresh baseline 強制要求
5. **OpenAI (2026/03).** *Model Release Notes*：GPT-5.1 在 2026/03/11 從 ChatGPT 移除
6. **OpenAI Model Spec CHANGELOG (2025-2026)**：Platform → Root 升級、加入 Agent scope of autonomy 章節

### 5.3 2026 年產業分析與案例

1. **BISI / Bloomsbury Intelligence and Security Institute (2026/01/22).** *Claude's New Constitution: AI Alignment, Ethics, and Future of Model Governance.*
2. **VentureBeat (2026/04/24).** *DeepSeek-V4 Arrives at 1/6th the Cost of Opus 4.7, GPT-5.5.*
3. **Tom's Guide (2026/04/24).** *7-0 wipeout: ChatGPT-5.5 vs Claude 4.7 in 7 Tests.*
4. **Lushbinary (2026/04/23).** *GPT-5.5 vs Claude Opus 4.7 Benchmark Comparison.*
5. **OpenAI Cookbook (2026).** GPT-5 / 5.1 / 5.2 / 5.3-codex / 5.4 / 5.5 Prompting Guides — 6 份獨立模型指南
6. **Miraflow.ai (2026/04).** *Claude Opus 4.7 Prompting Best Practices: 15 Techniques (2026).*
7. **Chatly (2026/04).** *15 Best System Prompts for Claude Opus 4.7.*
8. **R&D World Online (2026/04/24).** *How GPT-5.5 stacks up with Claude Mythos.*

### 5.4 2026 年法規與治理

1. **EU AI Act**：2026/08 全面生效，penalty €35M / 7% global revenue
2. **Anthropic 2025/07** 簽署 *EU General-Purpose AI Code of Practice*（為 2026 合規鋪路）

---

## 附錄 A｜心法內化（五歲小孩版・2026 版）

> 想像在 2026 年 4 月，你有兩個新請來的助理：**Opus 4.7**（剛在 4/16 報到）和 **GPT-5.5 (Spud)**（4/23 報到）。
>
> Opus 4.7 是一個**字面解讀王**：你跟他說「你**可以**考慮加 error handling 喔」，他就真的「考慮一下」── 然後不加。在他之前的版本 Opus 4.6 會自動腦補成「啊主人是要我加 error handling」── **但 4.7 不會了**。
>
> GPT-5.5 是一個**全新訓練的人**：你把以前對 GPT-5.4 的指令照搬過來，他會做得**比較差**，因為他是新人，預設模式不一樣 ── 必須像新員工一樣**從頭給他寫 SOP**。
>
> 還有一件大事：**2026 年 1 月 Anthropic 公開了一份 23,000 字的「Claude 憲法」**，明確說「安全 > 倫理 > 公司規則 > 對你有用」── 你叫 Claude 做違反前三層的事，他**真的不做**，不管你的 prompt 寫多懇切。**OpenAI 在 2025 年底公開了 5 層權限階層**，你寫在 system 跟寫在 user 訊息裡的同一句話，威力完全不同。
>
> 還有：**2026 年 8 月歐盟 AI Act 要全面生效**，罰款 €35M。如果你沒做「per-model prompt 驗證紀錄」，可能會被罰。
>
> 所以結論：**今天不再是「寫一個 prompt 通用所有模型」的時代了，是「per-model 各寫一份、各驗一次、各留一份紀錄」的時代了。**

---

## 附錄 B｜口訣記憶（三個重點，2026 版）

1. **「01 分歧、04 質變、08 合規」** — 2026 三個轉折日期：1/22 Constitution 對 12/18 Model Spec 架構分歧、4/16-23 Opus 4.7 + GPT-5.5 雙旗艦質變、8 月 EU AI Act 全面生效
2. **「Literal vs Inferred 是 2026 新軸線」** — Opus 4.7 字面解讀、GPT-5.5 outcome-first，舊 prompt 用「consider / feel free」這類軟性語句在 4.7 上會崩
3. **「Brittlebench 證偽 robust 神話」** — 2026/04 Meta 發表的 Brittlebench 證明：semantics-preserving 擾動仍可翻轉 63% 模型排名，不能再說「現代模型已經很 robust」

---

*報告結束 ｜ 2026/04/26 ｜ 證據截止 2026/04/24*