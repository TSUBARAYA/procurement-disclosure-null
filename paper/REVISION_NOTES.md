# 论文实质性大修：修改说明与实证核验清单

**论文**：Testing the Transparency–Competition Premise: Evidence from EU Public Procurement
（原题：Does Transparency Increase Competition? Three Designs, Two Independent Sources, and 326,718 Contracts）
**交付文件**：`Does_Transparency_Increase_Competition.docx` / `.pdf`（46 页，7 表 5 图，公式与文献完整）
**源文件**：`transparency_and_competition.md`
**修订轮次**：第一轮（九模块大修指令）+ 第二轮（作者反馈的 4 项实质矛盾 + 2 项细节，见第五节）

---

## 一、七个模块的修改内容

### 模块一：标题、摘要与引言

**标题**改为 *Testing the Transparency–Competition Premise: Evidence from EU Public
Procurement*——问句标题撑不起识别能力（三个设计识别的都是制度组合），改为"检验前提"的表述。

**摘要重写**，按指令五要素组织（研究问题与理论动机 → 三种设计及各自识别对象 → 主要实证结果 →
关键识别假设与局限 → 结论），并落实两条硬性要求：
- 必写句已逐字写入：*"The designs identify the effect of a procedural bundle, not of
  disclosure alone."*
- 统计表述规范化：主估计写作 "positive but statistically **indistinguishable from
  zero**"，并明示区间双向容许（"exclude neither a competitive gain of one to two
  percentage points nor its absence"）；替代规格写明"family-wise significant only under a
  linear specification with contract-type controls, insignificant under a quadratic one"，
  不单独强调显著结果。
- 删除了旧摘要的数字堆砌（删去 252 cells、1.30M、+0.47pp 首阶段细节等，移入正文），保留论证
  必需的最少数字（+0.82/0.234、+1.4~2.8、+7.40/0.095、1.6%）。

**引言按五步框架重写**：(1) 透明度与竞争的理论关系；(2) 为什么透明度不自动转化为竞争
（披露改变信息，不改变投标池结构、买方偏好、合谋风险）；(3) 欧盟改革的实际制度内容；
(4) 研究问题、三设计、贡献；(5) 识别限制与研究范围。四个概念在全篇首次同时定义并区分：
transparency（理论概念）/ disclosure（披露机制）/ e-procurement（电子采购机制）/
procedural bundle（实际研究的制度组合）。"披露而缺乏问责"的解释改用审慎表述：*"Our
estimates are consistent with the interpretation that mandatory disclosure, stripped of
the accountability machinery..."*，并紧跟 "We state that as an interpretation, not an
identification"。引言同时明确：三设计识别的不是同一参数，两个时序设计共享识别变异，
"the program really offers two independent legs, not three"。

### 模块二：Table 3（v3.0）一致性核查

核查结论（详见核验清单 V1）：
- v3.0 点估计 +3.37 与 CI [−3.69, +7.12] 出自同一次运行（`results_v3.json`，252 cells），
  但区间**不以点估计为中心**（中点 +1.72）；区间结构（mean/n_cells/share_negative=0.25）
  显示它总结 8 个 group-time ATT cell 的分布（cell 均值 +2.42，2/8 为负），不是围绕点估计的
  Wald 区间。同表 v4.0、v6.0 及论文其余全部表格的 CI 均为对称 Wald 区间且与 SE 自洽。
- 本地无 `run_v3.py` 与 cell 级明细，**无法验证区间构造**（经验分位数还是 percentile
  bootstrap 均无记录），也无法重算。按指令"无法访问原始代码 → 保留原始数值并明确标记"处理：
  Table 3 表注完整披露不一致事实、两种可能构造、标记待核验，并说明结论（区间跨零）对构造
  不敏感；6.2 正文加提示段。**未为对称化而修改任何数值。**

### 模块三：Running variable 内生性分析

- **5.1 新增独立小节** "The running variable may respond to the outcome: a
  mechanical-bias discussion"：三环论证（single/multi 定价机制差异 → 价格楔子跨线再排序 →
  估计值操纵渠道开放），全部用论文自有数据：折扣差 0.65pp（6.61% vs 5.96%）换算的相对价格
  楔子 0.7%、阈值处密度约 8,800 份/每 1% 宽度、**量级核算：最多约 60 份合同跨线、机械偏差
  约 0.02pp，比 SE 0.70 小一个半数量级**；并报告反向证据（band 内 single 授标价中位数反而
  低 0.4%）。小节按指令明确划定："内生性风险的存在不等于已证明估计有偏；折扣率跳跃是待解释
  的诊断而非已识别的因果效应，也不证明设计失效。"
- **6.4 重写**：−1.76pp 折扣率跳跃给出三种解读（制度效应 / 样本选择 / 跑动变量内生诊断），
  明确不采用第一种，指出第三种"对识别最重要"——授标价与估计值关系跨线不连续正是 5.1 机械
  渠道的宏观痕迹，但不宣称设计失效；结论收窄到原表述（价格数据中没有能挽救竞争故事的福利
  红利）。
- **7.3 调整报告顺序**：estimated-value 替代跑动变量从第二响应**提升为第一响应**（直接回应
  5.1 内生性），完整报告样本筛选链（95.4% populated → 311,778；ratio∈[0.5,2.0] → 165,498；
  值空间窗口 → n=135,444）、CI [−0.02, +4.62]、与主估计 +0.82 的差异及三个候选来源
  （样本选择/排序变量/区间更宽），明示"不反转定性读法"。新增一段说明 **discount rate 为何
  不进任何控制集**（与授标价机械联系 + 其自身跳跃正是被诊断的对象）："No specification in
  this paper includes it."

### 模块四：TED 选择性披露

- **2.2 后新增 2.3 节**（原 2.3 顺延为 2.4）：披露规则的法律依据——Art. 50 的 TED 公布义务只
  覆盖阈值以上；**以下无 EU 级强制义务**，其出现是"国家透明度法/自愿公布/EU 资助项目/选择
  适用 EU 程序"的混合，明确写道 "It would therefore be wrong to describe the
  below-threshold side of the sample as uniformly voluntary"。随后系统讨论四个指定问题
  （非随机披露选择；披露概率与竞争/行政能力相关；两侧可比性；对连续性假设的影响），写入
  必写句：*"If voluntary publication below the threshold is correlated with competition,
  the continuity assumption fails."* 并明确能检验什么（可见样本内 balance、donut）与不能
  检验什么（未披露合同的一切），承认"这是一项披露而非已被稳健性检验消除的局限"。
- **5.1 识别假设段**同步加入两大事前已声明威胁（可见性选择 + 机械排序）及其各自的回应与
  未回答部分。

### 模块五：不显著结果与 Donut RD 的解释

- 全文清除 "wrong sign / wrong way / the sign the policy premise excludes / running
  against the policy premise" 等把正向不显著估计当作反向证据的表述（共 6 处，含引言、6.1、
  6.2、7.2、7.3、结论），统一改为 "positive but statistically indistinguishable from
  zero" + 区间双向容许的表述；6.1 明确写入："an interval that spans zero is evidence
  about neither direction"。
- **Donut 降级**：7.3 写入指定句式 "The donut estimates are treated as diagnostics of the
  potentially contaminated threshold neighborhood, rather than as the paper's primary
  findings"，并给出三条理由（未预注册 / 仅线性+有效控制集下显著 / 作用是展示操纵的影响而非
  替代主估计）。摘要与结论同步（"diagnostics of the contaminated neighborhood rather
  than as findings"）。
- **结论重写**为两半结构 + 第三条：(1) 主规格无可区分于零的竞争效应估计（不拒绝零 ≠ 证明
  零，MDE≈2pp 明示）；(2) 替代规格有更大正向估计但带模型/样本/识别敏感性，无一识别披露
  本身；(3) 现有证据既不足以证明改革提升竞争，也不足以证明其无效；(4) 新增 "The results
  point to what should be tested next" 段——需要能分离 transparency / e-procurement /
  procedural apparatus 的变异。结论的 "What this paper does not say" 段同步改写（CI 区间
  双向引述、删除 "moves away from a competitive gain" 类判断）。

### 模块六：SME 梯度与理论模型

- **6.3 新增 reporting-artifact 段**：三个指定渠道（各国 SME 字段缺失率差异；数字化高的国家
  填报机制更完善；SME 定义按国别规则且是买方自报），指出 +33.40pp 可能混合真实参与差异与
  报告行为差异，当前按"上界倾向的关联"读；within-country 估计对前两个渠道部分免疫。
- **SME 缺失稳健性**：本地无 country-year 级 SME 缺失统计（详见核验清单 V3），**未执行、
  未编造**；文中声明为待完成任务并指向核验清单。
- **第 4 节模型补全**：第一阶段进入条件明确三个变量的经济含义并逐一区分——*k_i* 履约成本
  （完成合同的私人成本，中标后发生，在利润表达式内扣除）、*p_i* 合同价格（买方支付额、
  投标工具、对投标方是收入而非成本）、*c* 进入成本（是否中标都支付的固定支出）；说明披露
  干预只动 *c*，不动 *k_i* 与 *δ*；新增假设条件段（独立私有值、进入成本固定同质、δ 组内
  固定、无合谋）与适用范围声明。H1 与 H2 均按要求标注 **"This is a heuristic conjecture,
  not a formally derived comparative static"**，并说明为何不求解完整进入博弈。

### 模块七：预注册声明、研究记录与安慰剂检验

- **第 8 节**加入指定句 "We acknowledge that a self-hosted GitHub hash provides
  tamper-resistance but not third-party certification"，并区分四件事：哈希的完整性验证 /
  第三方独立登记与时间认证 / 事前确定的方案 / 事后检验；明示不宣称第三方认证，并指出记录
  提供的是"可检查的年表"。
- **删除 "after a referee asked"**：因无法确认作者是否收到过早期草稿外部反馈（不得虚构），
  改为完全基于论文内部证据的动机表述——"added by the authors after the main results and
  after the density test had documented manipulation at the cutoff; the motivation is
  internal to the paper's own diagnostics"。
- **安慰剂检验**：核查发现原始运行（`results_v6.json`）中 70%/120%/130% 三个 cutoff 的
  tau=0、p=NaN——**从未产生估计**（旧正文 "Placebo cutoffs at 70 and 80% ... produce no
  jump" 暗示 70% 也有效，不实）。已实际执行（脚本 `analysis/run_placebo_extra.py`，结果
  `materials/results/review4_placebo_extra.json`）：在 ±20% 主窗口内，70%/130% 无对照侧
  样本、120% 仅有 86 份 above 侧合同——**结构上不可执行**，不是零结果。7.3 改为如实报告：
  仅 80% 有可用估计（−0.05, p=0.146），其余三个标记待补（需全量 TED 提取），并说明需要
  什么材料。

### 模块八：全篇统一检查

- 五类指定矛盾逐项排查通过：摘要承认 bundle↔结论不宣称披露独立效应；主结果不显著↔结论不
  宣布政策无效；正文承认替代规格敏感↔摘要不只强调显著结果；方法宣称完成的检验↔结果部分
  有对应数字（placebo 状态已对齐）；事前预注册↔事后调整已明确分层。
- 保留全部数据来源、样本定义、设计、公式、图表、参考文献；无一处为重组逻辑而删除既有
  结果。
- 论文数字口径与此前各轮修订保持一致（带宽容差统一后的 n=326,718 体系未受本轮影响）。

---

## 二、实证核验清单（待核验项目）

以下四项为本轮**无法在本地完成**的核查/检验。论文中均已以统一方式标记（表注 "flagged for
verification" / 正文 "marked for completion" / "listed in the verification schedule"），
未以任何形式包装成已完成。

### V1. Table 3 v3.0 置信区间的构造（优先级：高）——**已解决：已重建**

- **已定位原始代码**：在桌面 neo 项目找到 `identification/run_v3.py`、`identification/
  estimators_v2.py` 与原始 `ted_panel.csv`。`estimators_v2.cell_ci` 的 docstring 与实现
  确认：archived 区间 [−3.69, +7.12] 是 8 个 post-period (g,t) cell ATT 的 2.5/97.5
  **经验分位数**（`np.percentile(a, [2.5, 97.5])`），不是抽样 CI、不是 bootstrap；点估计
  +3.37 是按 n_treated 加权的均值（等权 cell 均值 +2.42），这解释了区间为何不以点估计
  为中心。
- **已复现**：用原始数据 + 原始代码完整复现 archived 点估计与区间，并计算可复现的
  cell-level t 区间 **[−1.34, +8.09]**（8 个 cell 为观测单位、权重∝n_treated、
  临界值 t(0.975, 7)）。新脚本 `analysis/run_v3_ci_reconstruct.py`，结果
  `materials/results/review4_v3_ci_reconstruction.json`。8 个 cell ATT 明细、
  cell SD 4.09pp、share_negative 0.25 均已记录。
- **论文已更新**：Table 3 的 v3.0 区间改为 [−1.34, +8.09]，表注完整披露 archived 区间
  的性质（经验分位、非抽样 CI、加权 vs 等权差异）与重建方法；6.2 正文、Figure 2 副标题
  （数据驱动读取重建值）同步更新。两个区间均跨零，定性结论不变。
- **遗留**：新区间仍是"cell 间离散"口径而非合同级聚类抽样 CI；论文表注已如实说明其构造。
  若要合同级聚类 Wald 区间，需在合同级面板上重跑 v3.0 汇总（本地有 micro panel，可作为
  后续核验项）。

### V2. Placebo 70%/120%/130% 的执行（优先级：中）

- **现状**：预注册要求四个 cutoff；原始运行只有 80% 产出估计；本轮在本地 ±20% 缓存上实际
  执行，确认 70%/130% 窗口内无对照侧、120% 仅 86 份 above 侧——结构上不可执行。
- **缺什么**：全量 TED CAN 提取（本地只有 326,718 份 ±20% band 缓存），或覆盖 ±30% 的缓存
  窗口。
- **为什么重要**：预注册诊断电池的三个成员没有结果，"估计量噪声已校准"的陈述目前只靠
  80% 一个 cutoff 支撑。
- **论文当前限制**：7.3 如实报告"仅一个 cutoff 产出可用估计"，其余标记待补。得到宽样本后
  运行 `analysis/run_placebo_extra.py`（已备好同规格脚本）并报告 τ/SE/p/CI/n。

### V3. SME 梯度的缺失数据稳健性（优先级：中高）

- **现状**：+33.40pp（p=0.0002）为跨国关联；缺失率、各国 SME 定义、填报完整性均可能贡献
  梯度。本地无 country-year 级 SME 缺失统计。
- **缺什么**：micro panel（1,303,529 份合同）中 `NUMBER_TENDERS_SME` 的 country-year 缺失
  矩阵，或 v4.0 聚合前的中间数据。
- **为什么重要**：这是论文"最强结果"（参与梯度）的主要混淆渠道；若梯度在完整填报子样本
  上大幅下降，"参与红利"的强度需要重写。
- **论文当前限制**：6.3 已将 +33.40pp 按"上界倾向的关联"读，并声明检验待完成。预设规则
  （不依赖估计结果）：(a) 全样本；(b) 剔除 SME 缺失率高于样本中位数的 country-year；
  (c) 仅保留填报制度稳定的国家。各报告国家数/cell 数/n/缺失率/β/SE/95%CI，比较 β 是否下降。
  下降才可写 "may partly reflect changes in reporting behavior"；不下降也不得宣称无报告偏差。

### V4. `OUT_OF_DIRECTIVES` 字段定义（优先级：低）

- **现状**：`results_v6.json` 记录 `ood_below=0.0133`（预注册将其列为自选择度量），但本地
  数据字典无该字段定义，论文未引用该数字。
- **缺什么**：`docs/data_dictionary.md` 中 OOD 标志的确切定义与 TED 原始字段名。
- **为什么重要**：若可确认定义，2.3/5.1 的选择性披露讨论可增加一个直接度量（阈值下方
  1.3% 合同带该标志）强化论证。
- **论文当前限制**：暂不引用；确认定义后再决定是否加入。

---

## 三、复现材料

- 论文源：`paper/transparency_and_competition.md`；成品：`paper/Does_Transparency_Increase_
  Competition.docx / .pdf`（46 页；Word 2021 与 PDFium 双引擎验证：无乱码、5 图齐全
  [页 22/24/26/30/38]、7 张表题注与内容同页、公式与文献完整）。
- 本轮新脚本与结果：`analysis/run_placebo_extra.py` →
  `materials/results/review4_placebo_extra.json`；`analysis/run_v3_ci_reconstruct.py` →
  `materials/results/review4_v3_ci_reconstruction.json`（V1 已解决）；
  `figures/shot_fig2.js`（Edge headless 重截 fig2 PNG）。
- 本轮引用的既有结果文件（未重算）：`results_v3.json`（v3.0 CI 结构）、`results_v6.json`
  （placebo 原始状态、密度）、`price_margin_v6.json`（−1.76pp）、`results_v4.json`
  （+33.40pp）、`preregistration_v6.yaml`（placebo 电池与自选择威胁的事前声明）。

---

## 四、第二轮修订记录（作者反馈的实质矛盾与细节）

以下每一项都先在本地材料中核实事实，再改文本；没有为消除矛盾而改动任何数据数值。

### R1. estimated-value 规格"反转符号"的矛盾（5.1 与 7.3）

- **事实**：7.3 报告的 estimated-value 规格为 **+2.30**（CI [−0.02, +4.62]），与主估计
  +0.82 同号且更大；5.1 原句 "it reverses the sign" 与 7.1 原句 "an estimate further
  from a competitive gain, not closer to one" 均与 +2.30 > +0.82 矛盾。
- **修改**：5.1 按作者给定文本改写（larger positive point estimate / CI includes zero /
  selected subsample / does not establish a statistically robust competitive gain）；
  7.1 同句改为 "returns an estimate with the same sign as the headline and further from
  zero"。全文已无 "reverses the sign" 残留。

### R2. 结论的显著性自相矛盾

- **事实**：Table 6 的 donut 家族在 type controls + 线性规格下 Holm 0.042–0.043、
  Romano–Wolf 0.031–0.047，**确有多重校正后仍显著的规格**；原结论 "no specification
  produces an estimate ... statistically distinguishable from zero" 与此冲突，且 7.3
  内部（"family-wise significant under the linear specification" 两句之后又写 "What no
  specification shows..."）也自相矛盾。
- **修改**：结论按作者给定文本改写（pre-registered main specifications do not yield a
  statistically detectable competitive gain / post hoc manipulation-robust linear
  specifications significant under corrections but sensitive to polynomial order）；
  7.3 两处同类句同步区分 "pre-registered" 与 "post hoc"；7.2 的 low-digital 半样本句
  收紧为 "nominally distinguishable ... does not survive correction"。

### R3. Table 3 区间命名（对应核验项 V1）

见 V1：archived 区间经原始代码确认为 8 cell 经验分位区间（非 95% CI），表格已改列
可复现的 cell-level t 区间并在表注完整披露两种口径；Figure 2 副标题同步。

### R4. 结论与摘要中 SME 参与度的因果语言

- **修改**：摘要、结论共 4 处（"broader participation with digital depth"、"the SME
  share of tenders rose with digital depth"、"this instrument delivered broader
  participation"）统一改为作者给定的关联表述：strong cross-country association +
  smaller and statistically less conclusive within-country estimate + "does not
  establish how much of the cross-country gradient reflects actual participation
  changes rather than institutional differences or reporting practices"。
  6.3 与引言原本已是 "associated / not yet causal" 口径，未动。

### R5. 标题"新旧并存"的核实结论

- **结论**：阅读伪影。`.md` 源文件、`.docx`、`.pdf` 三处均只有新标题 *Testing the
  Transparency–Competition Premise: Evidence from EU Public Procurement*（PDF 首页已
  逐字确认）。与之前几轮 "Table 2"→"2"、"Pistaferri"→"Pistaferr" 属同一类 PDF 文本
  提取层伪影，非文件问题。

### R6. 预注册措辞全文统一（重要）

- **核实的事实**：`neo/config/` 有 v1.0、v2.0、v5.0、v6.0 四份冻结预注册文件（v1.0 文件
  自带 `frozen_before_result_inspection: true`）；**v3.0/v4.0 没有独立冻结预注册**，
  其规格顺序记录于 failure_log F14/F15（顺序预注册模式，F8 有说明）；公开仓库只发布
  `config/preregistration_v6.yaml`（SHA-256 在 manifest）。v6 文件确实包含 placebo
  [0.7, 0.8, 1.2, 1.3]、TED 自选择威胁、结论限定 TED 可见样本、带宽网格 [±10/15/20/25%]、
  多项式 [1,2] 与决策规则——论文中相应"预注册"声明有据。
- **修改**：摘要、引言、第 8 节、状态声明中 "three pre-registered designs" / "Every
  design was pre-registered before its results" 等不实表述，改为准确分层：v6.0 主设计
  有可核查的冻结文件+哈希；v3.0/v4.0 辅助设计无可冻结计划、其规格在 failure log 中按
  执行顺序记录（更弱形式的记录，明说）；v6 文件中确有事前声明的项目（placebo 电池、
  TED 自选择、带宽网格）逐项指明"哪些声明有公开记录支持"。
- **连带修正**：5.1 原 "two threats ... are pre-registered" 转述不准确——冻结文件声明了
  TED 可见性选择与"买方操纵金额/拆单"威胁，但**跑动变量内生性（排序变量是结果）不在
  frozen threats 中**，已改为如实分层。

### R7. 决策规则降级状态未报告（本轮新发现的实质缺口）

- **事实**：v6 预注册 decision_rule 写明"密度检验显著 → 主估计不可信，全部结论降级"；
  本文密度检验确实显著（p < 0.0001）。但论文从未报告这一降级被触发，且 5.1 对规则的
  转述（"a significant density jump confines conclusions to the TED-visible sample"）
  与冻结文本不符；7.1 还有一句无出处的 "a 5% gap was the pre-registered alarm level"
  （文件中不存在 5% 警戒线，代码里是 p_binom < 0.05）。
- **修改**：5.1 决策规则段改为冻结文本的准确转述并明示"降级在此适用，头条估计以
  uncertain 状态报告"；7.1 删除 5% 警戒线、补降级触发句；结论主规格段加入同一状态句。
  三处口径一致。

### R8. 图题与图内容不符（5 处）

核对实际渲染图后发现题注描述了图中不存在的元素，全部修正：
- Figure 1：拟合线实为红色实线（题注原写"gray/dashed"）→ 改 "red segments"。
- Figure 2：实为柱状图（题注原写 "dark markers / horizontal whiskers"）→ 改为柱状 +
  三个 CI 数值（与 Table 3 一致）。
- Figure 3：所有柱同色（题注原写 "gray bars below, blue bars above"）→ 删除分色描述。
- Figure 4：实为带数值标签的柱状图（题注原写 "markers, p-values in parentheses"，
  图中无 p 值）→ 改为柱状 + 数值标签。
- Figure 5：实为折线+标记点（题注原写 "bars are decile means"）→ 改为 "line with
  markers at decile means"。
- 连带修复：`figures/make_figures.py` fig2 副标题原硬编码旧 CI [-3.7, +7.1]，改为从
  `review4_v3_ci_reconstruction.json` 数据驱动读取；用 Edge headless 重截 fig2 PNG
  （`figures/shot_fig2.js`，因 CDP 浏览器与本地 HTTP 服务未运行，改用系统 Edge +
  file:// 加载）。

### R9. 模型文件的核实结论（作者询问）

- **结论**：桌面 `neo/`、`新模型/`、`结构改造/` 三个文件夹中的模型（PSL-ABM v3.9、
  nicai_v2.py 等）全部属于另一个项目（NEO/PSL 腐败动态 ABM 研究），**不是本文第 4 节
  的采购拍卖模型**，与本文无关，未使用。第 4 节模型在第一轮已按指令补全（k_i/p_i/c
  辨析、假设条件段、H1/H2 标注 heuristic conjecture），本轮复核无需重写。

---

## 五、第三轮修订记录（数据核查发现的构造伪影与口径不一致）

触发：作者要求对本轮全部改动数字做源头核验（"你确定你这次数据都没错都有准确来源吧"）。
本轮改动数字（[−1.34, +8.09] 等）经重跑全部复现一致；但核验过程发现两个**先前存在**的
实质问题，均已修复并记录。

### A1. 密度检验是构造伪影（最重要，波及摘要/引言/2.1/2.2/5.1/6.1/7.1/7.3/结论）

**原始实现**（`neo/identification/run_v6.py::density_test`）：`bin = floor(r/0.02)`，
left = bin ≤ −1（12 箱，含 15.7% 填充的边缘箱），right = bin ≥ +1（9 箱，**排除紧贴
阈值上方的 bin 0**，含 11.6% 填充的边缘箱），二项检验零假设 p = 0.5。输出：
log gap −0.01568、binom p ≈ 0。论文据此声称"1.6% excess density below the line"。

**审计发现**（`analysis/run_density_audit.py`，输出 `review5_density_audit.json`；
直方图从 `analysis/rd_sample_cache.csv` 326,718 份合同精确复现，22 箱逐一核对一致）：

1. **机械零值**：密度完全对称时，该构造因槽位不对称（左 11 完整 + 15.7% 部分 ÷ 12；
   右 8 完整 + 11.6% 部分 ÷ 9）**机械产生 log gap −0.0306**（虚假"下方超额 3.1%"），
   比观测值 −0.0157 大一倍。偏差校正后"下方超额"为 **−1.5%**（即下方反而低）。
2. **修正检验全部不拒反对称**：
   - 对称完整箱（11 vs 9）：下 15,817.5 vs 上 16,518.1（上高 4.4%；t = 0.77, p = 0.45）；
   - 局部对偶箱：紧贴下方 15,085 vs 紧贴上方 20,296（下方低 25.7%）；
   - McCrary 局部线性外推比率 0.985；
   - 二项检验正确零假设 12/21 + 按 (国家,年,类型) 917 单元 cluster bootstrap：p = 0.14；
   - log gap 对机械零值 bootstrap：z = 1.39, p = 0.17。
3. **二项检验双重缺陷**：零假设 0.5 忽略 12:9 槽位不对称（正确为 12/21）；
   泊松独立性假设被违反约 16 倍（bin 计数 sd ≈ 2,046 vs 泊松 sd ≈ 127）。
4. **r = 0 堆点（数据特征，非操纵）**：4,659 份（1.4%）中标价等于阈值（4,460 份精确
   相等），69% 来自德国、89.8% 中标价 = 估值（全样本 38.4%）→ 报送惯例；堆点在阈值处
   而非下方，抬高 bin 0（这正是冻结代码排除 bin 0 的可能动因，但只从右侧排除即造成不对称）。
5. **打包估计三口径**：3,262（论文原采用，fit0.15_o5）/ 2,257（run_price_bunching.py）/
   11,062（review2_robustness.json 同文件复现值，CI [10,818, 11,353]）；归档敏感性网格
   （事后检验，冻结预注册中无打包估计器）18 格全网格 −65,537 ~ +13,091、8 次变号，
   仅取 ≤±0.20 窗口为 −2,830 ~ +4,795、4 次变号；"模型无关校准 2,800"为循环论证
   （1.6% × 176,274），已撤回。

**论文修改**：7.1 整节重写（冻结输出如实报告 → 构造缺陷与机械零值 → 修正检验 → 堆点
→ 打包估计不可辩护 → 决策规则处理 → 存续内容）；摘要/引言第二发现/2.1 表注/2.2/5.1
决策规则段/5.1 机械排序段/6.1 "5% 警戒线"改口径/7.3 manipulation-robust 全部改为
diagnostic/Table 6 题注/结论三处，全部去除操纵断定；Figure 3 重绘（中性标题 + 堆点
红纹段可视化）。

**决策规则的处理**：冻结规则"密度检验显著 → uncertain + 降级"只发生在有缺陷的实现下；
论文报告头条估计为干净 null，同时完整披露冻结输出、缺陷与修正数字供读者重判。
confinement 规则（结论限定 TED 可见样本）是预注册的结构性威胁，不依赖密度检验，继续有效。

### A2. 其他连带修正

- "manipulation-robust specifications"（7.3/Table 6/结论共 7 处）→ "diagnostic"
  （donut 与法定 running variable 的动机是结构性排序威胁，不是检测到的操纵）。
- 6.1 "a density gap larger than about five percent"（无出处的警戒线）→ "a density
  asymmetry that survives the construction audit of Section 7.1"。
- 3.x "cross-sectional cutoff designs fail through bunching" → "sorting at the cutoff"。
- README 结果台账与结论口径段同步更新；`figures/redraw_figures.py` fig3 重绘。

### A3. 复现方式

```
python analysis/run_density_audit.py     # 全部审计数字 → materials/results/review5_density_audit.json
python figures/redraw_figures.py         # 重绘 5 图（fig3 为新版）
```

---

## 六、第八轮修订记录（2026-10-22 深夜，审稿意见八项 + 决定性诊断）

审稿意见八项（130% 安慰剂显著 / running variable 可操纵 / 规格结论不一致 /
v3.0 推断方法敏感 / 密度规则被事后调整 / 堆积不稳健 / 异质性过度解读 /
数字前后不一致）逐项处理如下。全部新数字可复现（见 A3）。

### A1. 问题 1（最高）：130% 安慰剂显著 —— 从"无法解释的跳变"到"剖面定位"

- **修正阈值恢复口径（新发现的数值地雷）**：所有用 `exp(log(v) − r)` 恢复阈值的
  代码都会把 value 恰好等于阈值的堆点合同错分——±20% 带内 **4,246 份**。
  `run_v7_placebo_bunching.py` 与 `run_review8_profile.py` 已改为按整数法定
  阈值表直接重构断点。修正后 130% 点为 **−1.14pp（SE 0.37, p=0.005,
  CI [−1.90, −0.37], n=232,088）**（原 −1.15/p=.004 为恢复口径污染值）；
  70%/80%/120% 为 −0.62/+0.16/−0.14（p=0.119/0.533/0.802）。
  130% 过 Bonferroni（4 检验，阈值 0.0125）与 Holm（5 检验族含真实断点，
  调整 p=0.0245）→ 按预注册规则，估计量受威胁，论文直说。
- **断点剖面（决定性检验，新 Table 10）**：同一规格在 0.70τ–1.45τ 十六个断点
  重跑（`run_review8_profile.py` → `review8_placebo130_profile.json`）。
  结果：线性估计在 ±1.3pp 区间内振荡、**无单调漂移**（否证"平滑梯度"读法）；
  1.30τ 低于局部趋势 1.7 个残差 sd（不是孤立尖峰）；1.25τ（−1.25, p=.013）与
  1.35τ（−0.90）同为负（是邻域而非单点，但三点的上侧都被 ±40% 提取边界截断）；
  二次剖面平缓（−0.94~+1.67，仅 0.75τ/1.20τ 名义显著），**真实阈值处头条本身
  从 +1.27（p=.085）塌缩到 +0.12（p=.906）**。结论：设计自身诊断无法把头条
  认证为断点；1.00τ 剖面点精确复现 Table 8 头条（+1.27, p=.080 无小样本修正），
  内部一致性自校验通过。
- 1.3τ 邻域的 binscatter（0.01 箱）、带宽×阶数×donut 网格、留一国家法
  （`review8_placebo130.json` + `run_review8_corrections.py`）全部保留；
  摘要、7.3、7.4、结论、第 8 节验证日程同步改写。

### A2. 问题 2/3：log_value 共线性量化 + 规格归因纠正

- `run_review8_collinearity.py`（→ `review8_logvalue_collinearity.json`）：
  (国家×年×类型) 单元内 corr(log_value, r) = **1.000000**（917 单元），
  主回归中 log_value 的 **VIF > 400 万**——它是设计矩阵的确定性函数，不是控制。
- 控制集阶梯（法定口径）：无控制 +1.36（p=.047）/ 仅 log value +1.38（p=.047）/
  仅 type FE +1.27（p=.085）/ 双控制 +1.27（p=.085）。**+1.27→+1.36 的全部差异
  来自合同类型固定效应，与 log value 无关**（单独去掉 log value 只动 0.02）。
  论文原先"without the log-value control → +1.36"的表述在摘要、引言、Table 8
  注、结论共 6 处，已全部改为"with no controls at all"并注明归因。

### A3. 问题 4：v3.0 主推断声明

- 主推断定为设计原生 **influence-function multiplier bootstrap（国家聚类）**：
  [−0.32, +7.14]（SE 1.90）。理由：估计量原生推断、在处理赋值层（国家）聚类、
  且不像国家聚类 bootstrap 那样丢弃 551/2000 个重抽样。Table 3 行、Figure 2、
  题注全部切换；cell-level t（[−1.34, +8.09]）与国家聚类 bootstrap
  （[+0.28, +6.65]，不跨零）降为敏感性区间并在表注全文披露。

### A4. 问题 5/6：密度审计与堆积估计

- 7.1 保留"冻结输出 → 构造缺陷 → 机械零值 → 修正检验"全链，并在"What survives"
  明确：密度干净 ≠ 整个设计通过（130% 安慰剂仍触发 alarm）。
- 堆积估计改报第七轮法定阈值重建值：首选规格 **3,287**（bootstrap CI
  [2,132, 4,592]），敏感性网格 **−5,727 ~ +3,287、15 个不同规格变号 7 次**；
  归档网格（−65,537~+13,091）与旧论文段落的"8 次变号"等描述全部替换；
  "五次变号"笔误改为七次。仍不报任何单一计数。

### A5. 问题 7：异质性降级

- 数字化深度分组整体撤回（归档版不可复现 + 重跑版中位数=1.0 的 198 条异常），
  7.2 改写为"无有效数字深度分组、不作异质性声明"；摘要/引言中"七个子组"
  改为 Table 5 的五个子组；Table 5 Supply SE 0.86→0.85（归档值 0.8543）。
- 多重检验在法定口径重算（`run_review8_corrections.py`）：type 控制下三个 donut
  过 Bonferroni（0.024/0.040/0.038）、Holm（0.024–0.029）、Romano–Wolf
  （0.032–0.040），est_value 全不过；无控制下仅 ±1% donut 过 RW（0.040）。
  （修复了 RW 实现中一个把全部 t 置零的 bug：generator 里 `(_, yg)` 解包后
  引用未绑定的 `Xg`。）

### A6. 问题 8：全文数字统一（消灭的矛盾清单）

| 位置 | 旧值（矛盾源） | 新值 |
|---|---|---|
| 估计价值 RD | +2.30 / +2.32 / +3.15（p=.034/.011，显著） | **+1.22（p=.256, n=150,074）**；控制集 +1.13/+0.85/+0.82 |
| 估计价值修正原因 | —— | 指数恢复阈值错分估计侧堆点（4,608 份中 3,743 份，82% 德国） |
| v6.0 行（6.2 正文/图 2/表 3 注） | +0.82 / [−0.56, +2.21] | +1.27 / [−0.19, +2.72]，n=327,636 |
| Figure 2 | v3.0 [−1.3, +8.1]、v6.0 [−0.6, +2.2] | v3.0 [−0.3, +7.1]（主推断）、v6.0 [−0.2, +2.7] |
| 堆点"精确相等" | 5,116 与 5,121 同段并存 | 统一 5,121（round 到欧元） |
| ex-堆点对称比较 | 15,739/15,799（0.4%） | 15,857/15,967（0.7%，归档值） |
| donut 段（7.3） | +1.55/+1.40/+1.75，LOO +1.13~+2.12 | +1.75/+1.65/+1.89，LOO +1.39~+2.32 |
| 窗口 departure 段 | 对数窗 +0.78 vs 值空间 +0.82（归档样本） | 对数窗 +1.17 vs 值空间 +1.27（法定样本，n=323,519） |
| 族校正段 | 归档 Bonferroni/Holm/RW | 法定口径全套（见 A5） |
| 价格边际 RD | −1.55（SE 0.15, p<0.0001, 古典 SE） | −1.55（SE 0.77, p=0.054, 国家聚类，n=166,003） |
| 3.1/3.2 样本与构成 | 326,718 / 6.85·6.03 / 50.1%·49.2% | 327,636 / 6.91·5.94 / 50.3%·49.0% / 覆盖率 97.1% |
| 窗口分段 | +0.92 / +0.98（归档） | +1.42（p=.052）/ +0.83（p=.499） |
| Table 4 行 1 CI | [−1.40, +16.30] | [−1.39, +16.27] |
| est 覆盖率表述 | "41% of the threshold sample" | 46%（150,074/327,636） |
| 法规编号 | Reg. (EU) 2015/2191 | **Reg. (EU) 2015/2170**（legislation.gov.uk 核实） |
| Table 9 placebo | −1.15/p=.004/CI[−1.92,−0.39] | −1.14/p=.005/CI[−1.90,−0.37]（整数阈值口径） |

### A7. 带宽网格的原始数据端到端校验

- 曾怀疑 ±25% 点被 ±40% 提取截断；核实后 ±25% 带为 ratio∈[0.75, 1.25]，
  完整落在缓存内。`run_review8_bw25_raw.py` 从原始 TED zip 重提
  ratio∈[0.70, 1.30] 合同重算带宽×阶数网格：**8/8 格与缓存版逐位一致**
  （±25% p1 +1.33, p=.037, n=403,732, CI [0.09, 2.58]），法定数字不依赖缓存。
  （该脚本初版有两个 bug：ISO 字典 'ROU'→'RO' 漏掉全部罗马合同、提取窗 0.85
  截断 ±20/25% 带下侧；均已修正并以 ±10/15/20 三点逐位复现为校验。）

### A8. 复现方式

```
python analysis/run_review8_profile.py          # 断点剖面 + 130% 网格 → review8_placebo130_profile.json
python analysis/run_review8_collinearity.py     # log_value 共线性 → review8_logvalue_collinearity.json
python analysis/run_review8_corrections.py      # 族校正/LOO/窗口/分段/构成 → review8_corrections.json
python analysis/run_review8_estvalue_corrected.py  # 估计价值 RD 修正 → review8_estvalue_corrected.json
python analysis/run_review8_cpv.py              # type+CPV 控制集 → review8_cpv_statutory.json
python analysis/run_review8_bw25_raw.py         # 带宽网格原始数据校验 → review8_bw25_raw.json
python analysis/run_v7_placebo_bunching.py      # placebo battery + bunching（整数阈值口径）
python figures/redraw_figures.py                # 重绘 5 图（fig2 用主推断区间）
cd paper && python verify_round4.py             # 412 项论文↔归档逐条核对
```

---

## 七、第九轮修订记录（2026-10-24 深夜，审稿意见九项三档 + 希腊 bug）

第九轮审查发现的问题分三档：数据与设计层（希腊被静默剔除、样本量口径混用、
覆盖率无出处、表9投标期行无出处、7.6 清洗数字无出处、密度归因与自身数据矛盾）、
计数与口径层（约16处纯文本）、仓库卫生层（矛盾结果文件、缺失脚本）。逐项处理如下。
全部新数字可复现（见 A11）。

### A1. 问题 1（最严重）：希腊被静默剔除出主设计

- **bug**：`run_v7_estimate_rd.py`（及同族脚本）的 ISO2→ISO3 映射把希腊键写成
  `'GRC': 'GRC'`（TED 用两字母 `'GR'`），全部希腊公告落入 `code not in EU28`
  被丢弃。实测：过滤后希腊 CN 公告 **233,744 条**，其中带估计价值 **230,293 条**
  （占 CN 估值样本 4.9%）。v7.0 主设计实际只有 **27 国、27 个聚类**，而论文
  通篇写 EU-28 / "28 awarding countries"（摘要、3.1、5.1、表9注）。
  v6.0/v3.0/v4.0 均含希腊（28 国），只有 v7.0 漏。
- **影响**：同一规格（清洗 + type 控制 + 线性 + ±20%）单投标头条
  **+0.49（SE 0.91, p=0.593, n=164,203）→ −0.67（SE 1.46, p=0.650, n=179,065）**
  ——点估计翻符号；两者都不显著，无结论变化。外国中标 −1.25 → −1.21（p=0.016→0.019）。
  翻符号可追溯：希腊逐年的局部跳变在数据最多的 2020–2023 多为负（2018/19/21/22/23），
  剔除它们把估计推正。MDE 从 2.5pp 升至 4.23pp（SE 变大）。
- **处置**：修正映射，从原始 zip 重建 `cn_matched.csv`（4,688,892 行，28 国）与
  全部下游文件；论文 6.1 新增专段披露错误、影响与翻符号机制，摘要加一句，
  结论同步；5.1 的 "28 awarding countries — a count that is now true rather
  than nominal"。
- 附带修正：`run_v7_estimate_rd.py` 带宽网格的 ±25% 格实为 ±20%（`band` 已限
  ±20%，子集等于自身）——法定口径带宽网格改从全量缓存计算（图4 与正文）。

### A2. 问题 2：样本量三处口径混为一谈

- 3.1/5.1 原称 "4,458,599 notices, of which 3,775,003 (84.7%) resolve to an
  award notice **with a usable offer count**"——84.7% 只是匹配到授奖公告；
  可用报价数约 50%。已拆成三个各有所指的计数（3.1 新增说明段）：
  带估值公告 4,688,892（=过滤总数 7,966,779 的 58.9%）→ 匹配授奖 3,968,395（84.6%）
  → ±20% 带 339,636 → 各结局自有可得性：单投标 179,065 / 外国中标 280,578 /
  投标期 339,368。表9 三个 n 由此得到解释（字段可得性，不是过滤选择）。

### A3. 问题 3：CN 覆盖率数字无出处

- 原 "about 55% of the 8.58 million" 在任何脚本/结果文件中不存在。
  `run_review9_coverage.py` 从原始 CN zip 单遍计数：过滤后总数 **7,966,779**，
  带可用估值 **4,688,892（58.9%）**；逐年 36%（2013–15）→ 52–59%（2016–19）
  → 63–67%（2020–22）→ 58%（2023）。希腊 233,744/230,293 与审计完全一致。
- 3.1/7.5 的 "about a third of notices"（v7.0 之前的陈旧数）已删除，统一为 58.9%。

### A4. 问题 4：表9 投标期行无出处且与正文矛盾

- 原表9 行 −36.6（SE 24.2, p=0.142, n=316,779）无归档支持，且与 5.1 正文
  −39.2（SE 26.8, p=0.157, n=316,791）互相矛盾。定稿：**全表统一为清洗 +
  type 控制规格**，表9 投标期行 = −30.73（SE 23.30, p=0.198, CI [−78.54, +17.09],
  n=339,368）；5.1 第一阶段段同规格（±5% +0.46/SE 38.5/p=0.991；±10% −32.38；
  ±20% −30.73），并删除"每个带宽同号"的旧说法（±5% 现为零）。
  15 个第一阶段候选在 28 国重跑（`v7_first_stage_procedures.json`）：
  框架协议 −3.14（SE 1.16, p=0.012, Holm 0.17）与 INP（p=0.038, Holm 0.53）
  两个名义显著、均不过校正。

### A5. 问题 5：7.6 清洗后子样本数字无出处

- 原七个数（−3.27/+33.8/−4.81/−9.54/+0.40/+1.22/+0.71）无归档支持
  （只有清洗前 −3.224/1.43/0.0328/20,376 在 v7_density_robust.json）。
  重跑 `run_v7_clean_subsamples.py`（28 国）定稿：2013–16 −3.34（SE 1.42,
  p=0.026, n=20,781）、报价数 +0.33 份（p=0.038）、S −4.79（p=0.0009）、
  W −9.37（p=0.010）、U +0.05（p=0.983）、2017–19 +3.38（p=0.677）、
  2020–23 −2.38（p=0.543）；外国中标 −1.21（SE 0.49, p=0.019, n=280,578），
  控授标价 −1.56（SE 0.61, p=0.017, n=177,911），分期 −1.44/−1.48/−1.06，
  分型 −0.70/−0.98/−0.87。

### A6. 问题 6：密度归因与自身数据矛盾（重写）

- v7.0 估计价值样本上，冻结 12v9 构造给出 **log gap = +0.356**（每箱下 12,867
  vs 上 18,363，**下方稀 29.9%**）——与授标价值样本的 −0.0157（下方多 1.6%）
  **方向相反、大一个量级**；7.1 的机械伪影（对称密度下制造 3.1% 虚假"下方超额"）
  解释不了它。原 5.1/图3 题注称该拒绝"与其在授标价值样本上一样是构造伪影"，
  与自己的数据矛盾，且 +0.317（28 国为 +0.356）从未报告。
- 重写：报告 +0.356；指出下方箱计数从带下沿 1,736 升至紧贴线下 16,274 是
  **斜率不是跳变**——正是 2.3 节可见性选择故事预测的形态（自愿发布随合同规模上升），
  它是对连续性假设的限定而非对操纵的认证；局部检验（1 箱 16,274 vs 19,960，
  比率 0.82，聚类 bootstrap SE 0.13，p=0.16；2 箱 0.81，p=0.08）不支持断点。
- 图3 题注重写；堆点改按估计价值侧重算：**2,823 份在 0.01% 内**（2,617 份
  四舍五入到欧元后相等；精确相等仅 47），德国仅占 21.7%（授标价值侧 73.8%），
  堆点合同中 award=est 为 10.7%（全样本 3.4%）——德国 feed 解释不迁移，
  降格为"较弱的 rounding-to-threshold 惯例"。图中原误植的授标价值侧故事
  （5,314 份/74% 德国/90% award=est）已删除。

### A7. 问题 7（7.6 清洗计数两处合计口径）+ 电子份额声明错误

- 哨兵值：**精确 9,999,999,999,999 仅 14 行**；1,608 = 14 + 1,594 非正值合计。
- NUMBER_OFFERS：<1 为 428 行、≥999 为 420 行（原 "845 rows" 是旧口径合计）。
- **`NUMBER_OFFERS_ELECTR` 超限声明是错的**：原称 "3.04 million rows (68%)"，
  实为清洗规则把未匹配公告（elec_share 缺失）计作违规；真实超限仅
  **994 行（占有值行 1,447,645 的 0.1%）**。CN 记录的电子份额**可用**：
  带内 103,024 份有值，阈值跳变 −0.68pp（SE 0.59, p=0.257）——7.6 与表9 已改。
- value_est 越界 46,951（1.0%）；lots>1000 25,092；投标期 [1,365]。
- 清洗对比句改 28 国口径：raw+type −0.66 → clean+type −0.67；外国中标不变 −1.21；
  漏 type 哑变量的控制循环 bug 曾产出 −0.68（旧论文记为 +0.40，27 国口径）。

### A8. 问题 8 及计数/口径层纯文本修正（全部完成）

| 位置 | 旧 | 新 |
|---|---|---|
| 摘要/6.1/表3/结论/图1/图2 | +0.49/[−1.37,+2.35]/n=164,203 | −0.67/[−3.66,+2.32]/n=179,065（28 国） |
| 摘要 | "4.46M notices → 3.78M awards" | 4.69M → 3.97M（84.6%） |
| 摘要 | MDE 2.5pp | 4.2pp |
| 摘要:外国中标 SE | 0.16–0.54 | **0.13–0.44**（归档地平线 SE 0.134–0.440） |
| 5.1 平衡段 | "±5% cell holds 160,000" | **88,954**（160,000 实为 ±10% 带的 165,908/175,134） |
| 5.1 平衡段 | lots −0.16 | −1.26（希腊驱动，27 国为 −0.17，已注明） |
| 5.1 投标期差 | −0.44 天 / 37 天均值 | −0.40 天 / 36.9 天均值（t=6.39） |
| 5.1 placebo | smallest p=0.16 | smallest p=0.45（0.90τ） |
| 6.1 donut 跨度 | "2.9 points" | 2.1 points（+0.30 ~ −1.76） |
| 图4 题注 | −2.87/−0.05/+0.49/−0.81 | −4.26/−2.39/−0.67/−0.94；二次 −4.49 |
| 图4 题注 | "3.7-point range" | 2.1-point range |
| 表12 | +0.49/+2.28/−1.25；p=0.48；2.5pp | −0.67/+2.07/−1.21；p=0.16；4.2pp |
| 表12/7.5 | "estimate field covers about a third" | about 59% |
| 7.6 | 52,461 notices in 2013 / 1.2M in 2021 | 54,453（带估值）/ 806,331 |
| 7.6 | 20,360 contracts, SE 1.5 | 20,781, SE 1.42 |
| 表13/脚本/附加说明 | Reg. 2015/2191 | **2015/2170**（第八轮已改，本轮复查通过） |
| 第8节 | "31 result files, 29 reproducible" | **52 files, 49 reproducible**（第三项不可复现：results_v3_outlier_robust.json 无脚本、无论文引用） |
| 第8节 | "39 analysis scripts / 47 files / 8,369 行 / 497 校验" | 38 个 analysis 脚本 + 13 个 figures 构建器 / 54 文件 / 9,783 行 / **537 校验** |
| 3.1 逐字重复段 | 重复 | 已删（第八轮） |
| 重复 "### 6.1" 标题 | 两个 | 已并为 6.1/6.2（第八轮） |
| 结论两个 "main" 指代 | +1.27 与 +0.49 都称 main | 表3 增设 v7.0 主设计行，v6.0 标 archived；正文统一 |
| 堆积 "changes sign 5 times" | 5 | 7（第八轮已改，本轮复查通过） |

### A9. 表10/11 的 p=0.085 vs 0.080：SE 约定差异（如实披露）

两个归档文件对同一 +1.27（n=327,636）给出 SE 0.71/p=0.085（v6_rerun_final.json，
含小样本修正 G/(G−1)·(n−1)/(n−k)）与 SE 0.70/p=0.080（v7_placebo_bunching.json，
复刻冻结实现、无修正）。已在表10/表11 注释中说明约定差异，并给出修正约定的
精确值：真实断点 p=0.0849（与表8 一致）、130% 行 p=0.0057（仍过 Bonferroni
0.0125 与 Holm 0.025），结论不变。

### A10. 仓库卫生（第三档）

- `v7_clean_subsamples.json`：审查时缺失，实际已在 28 国缓存上重生（12:56），
  论文数字改引该文件（见 A5）。
- `rd_window_split.json` 与 `review8_corrections.json`：前者是**归档错误阈值**
  口径的分段（n=326,527），后者是法定口径（n=327,636）；论文引用后者。
  README 文件树已注明取代关系。
- `threshold_correction_density_detail.json` 与 `v6_rerun_final.json`：前者是
  第一次阈值修正脚本的早期口径（n=324,360），已被后者的 density 块取代；
  论文 7.1 引用后者。README 已注明。
- `v7_density_test.json` 的**生产脚本不在仓库**（复现性缺口）：补写
  `analysis/run_v7_density_test.py`（1/2 箱比率 + 国家聚类 bootstrap），
  28 国重跑（0.815/p=0.162；0.806/p=0.077）。
- 高发布子样本：归档文件同量两值 +2.28（p=0.371）与 +1.334（p=0.445），n 同为
  75,070——后者是 `placebo_highpub` 的 1.00τ 行，用 exp(log(v)−r) 浮点恢复阈值，
  把 value_est 恰等于阈值的合同错分（与 7.3 披露的伪影同源）。论文改引
  `single_highpub_cy`（整数阈值表）：28 国 **+2.07（p=0.412, n=76,588）**；
  placebo_highpub 1.10τ 显著（−5.74, p=0.027，1/6）。
- v7 图数据：`figures/build_v7_figdata.py` 无希腊 bug（消费旧缓存），但其
  ±25% 网格格实为 ±20%、拟合线未用论文规格。新增
  `analysis/run_review9_figures_v7.py` 从 28 国缓存重建全部 5 个图数据 JSON
  （floor 分箱与冻结构造逐位一致：16,274/19,960/18,247），原脚本文档注明被取代。

### A11. 复现方式（第九轮新增/重跑）

```
python analysis/run_review9_coverage.py        # 覆盖率分母（原始 zip 单遍）→ review9_cn_coverage.json
python analysis/run_review9_paper_numbers.py   # 平衡/堆点/MDE/清洗分解/第一阶段 → review9_paper_numbers.json
python analysis/run_review9_figures_v7.py      # 28 国图数据 → figures/*_v7.json
python analysis/run_v7_density_test.py         # 局部密度检验（补写的缺失脚本）
python analysis/run_v7_first_stage.py          # 第一阶段 15 候选（28 国）
python analysis/run_v7_estimate_rd.py          # v7.0 主设计全规格（28 国，修正映射后）
python analysis/run_v7_clean_subsamples.py     # 清洗 + 子样本分解
python analysis/run_v7_scale_placebo.py        # 外国中标 + 清洗后 placebo
python analysis/run_v7_density_robust.py       # McCrary + binscatter + 高发布子样本
python figures/redraw_figures.py               # 重绘 5 图
cd paper && python verify_round4.py            # 537 项论文↔归档逐条核对
cd paper && python verify_round8.py            # 文档级（docx/PDF）校验
```

### A12. 可追溯性收尾：主管线脚本补入 + 端到端验证（第九轮次日）

- **缺口**：论文第 8 节一贯声明仓库交付 `run_v3.py` / `run_v4.py` / `run_v6.py` 等
  主管线脚本，但审计发现 economy 仓库实际没有它们（存在于 neo 开发档案），
  `results_v3.json` / `results_v4.json` 成为无生产脚本的孤儿归档。
- **补入与复现**：从 neo 档案恢复 `identification/{run_v3,run_v4,run_v6,
  estimators_v2,estimators_v4}.py` 与 `data/{build_ted_panel,build_micro_panel}.py`，
  在 economy 仓库内重跑验证：
  - `results_v3.json`：ATT/CI/pre-trend/第一阶段全部字段逐位一致；
  - `results_v4.json`：main + dose 全部系数 beta/SE 机器精度一致（零差异）；
  - `results_v6.json`：从原始 TED zip 完整重跑（9 分 19 秒），**全部字段零差异**，
    含错误阈值表、密度 gap −0.0157、placebo −0.0515。
  （run_v3.py 缺 makedirs 导致 report/ 不存在时写文件失败，已补一行修复。）
- **Makefile/Docker**：Makefile 更新（537 项校验口径、补 v3/v4 目标与第九轮脚本、
  缓存行数 4.69M）；端到端链 figures → paper → verify 手动执行通过（本机无 make 与
  docker CLI，Dockerfile 未跑 build，保持标准配置）。
- **产出**：`report/` 下留下三份复现产物（results_v3/v4/v6.json、tables_v3.md）。

### A13. 并行编辑事件记录（密度口径冲突）

- 14:42 发现 `v7_density_test.json` 与 `run_v7_density_test.py` 被**另一进程**
  改为 above/below 口径（1.23 / p=0.34；1.24 / p=0.22），与论文全文引用的
  below/above 口径（0.82 / p=0.16；0.81 / p=0.08）矛盾。
- 已恢复为论文口径并重跑（种子 20261024，确定可复现），537 项校验恢复全过。
- 两口径的 p 值结论一致（均不拒绝断点），差异仅在报告方向；论文保留
  below/above 口径（<1 = 下方更稀，与 +0.356 的 below-thinner 叙事直接一致）。
- 提醒：仓库存在并行编辑风险，大批量改动前建议确认无其他会话在写。

---

## 八、第十轮修订记录（2026-10-25，外部评审九条 + 单位错误修复）

第十轮收到一份外部评审（九条）。逐条核实后：8 条方向成立，1 条（结论 CI 矛盾）
考证后不是错误（该 CI 明确归属 v6.0 归档设计），1 条（number of offers）评审被
论文的错误数字误导、却触发发现一个真 bug。全部处理如下。

### B1. 单位错误修复（评审第 7 条触发的真 bug）

- **bug**：`n_offers` 是**计数结局**（带内均值 3.78 份、中位数 2），但 Table 9 与
  7.6 把估计误乘 100 当“pp”报告：Table 9 的 **+20.22 实为 +0.20 份**（SE 0.10，
  p=0.061，CI [−0.01, +0.41]）；7.6 的 **+32.66 实为 +0.33 份**（SE 0.15, p=0.038）。
  波及 Table 9、7.6、REVISION_NOTES A5、verify_round4.py 共 4 处，全部修正。
- **稳健性诊断**（`run_review9_offer_robust.py` → `review9_offer_robust.json`）：
  原始差 −0.16 份（无希腊 −0.07）；99 分位 winsorize 后 **−0.007（p=0.94）**；
  log(1+offers) **p=0.38**；±25% 带宽 **−0.02（p=0.90）**；LOO 3/28 显著。
  结论：+0.20 是右尾驱动的边际信号（median 2、p99 25、max 293），**不作为发现
  报告**；Table 9 注已加段说明。评审说的“+20 份与单投标 null 的张力”不存在——
  修正后两者一致（都指向竞争微弱上升、不显著）。

### B2. v7.0 leave-one-country-out（评审第 2 条）

`run_review9_loo.py` → `review9_loo.json`：逐个剔除 28 国重跑头条。
- single：LOO 范围 **[−1.30, +0.49]**，**0/28 显著**——null 对每个国家都稳健；
  去希腊恰好复现旧 27 国值 **+0.49（p=0.59, n=164,203）**（内部验证旧跑只差希腊）；
  去德国 −0.56、去法国 −1.05。
- foreign_win：范围 [−1.50, −0.80]，**27/28 显著**（去法国 p=0.059）——finding
  不依赖单一国家。
- 结论（已写入 6.1 新段）：希腊翻符号是点估计层面的 noise，不是国家驱动的结果。

### B3. 两种 null 的区分（评审第 1 条）

6.1 新段：明确 (a) regime 变了而竞争没变（null = 改革无效的证据）与
(b) regime 在 cutoff 处没有可观测的机械变化（null = 无可识别的处理）。
论文倾向 (b)，理由是 first stage 失败是系统性的而非功效问题（投标期 SE 23 天
vs 指令 35 天最小期，机械跳变会被检测）。论文贡献相应降调为：**演示该阈值设计
无法识别其跨越的制度**，而非“透明度不提升竞争”的因果回答；政策相关性保留在
更窄的形式（制度的咬合可能在 notice record 不可观测的合规成本/审计风险维度）。

### B4. 早期效应机制展开（评审第 4 条）

7.6 三种 readings 展开：若早期为真，headline 应读作 “early positive, fading to
null”（不同 finding、不同政策含义）；reporting-artifact 读法的具体机制
（早期 coverage 36% vs 后期 63–67%、2013 年仅 54,453 带估值、running variable
恰生于该字段 → 子样本按设计依赖的字段被选择）；noise 读法的 family 论证。

### B5. foreign-winner 候选机制（评审第 3 条）

7.6 新段（标注 speculation）：COVID 压缩程序结构、后期 SE 小（1.27→0.43 份）
的统计解释、eForms 2023 起改变报告内容；声明三者均未识别，需按程序类型×
中标国籍的数据（现有 extract 不含）。

### B6. 结论 CI 明确化（评审第 5 条，考证后非错误但易混淆）

"What this paper does not say" 段改为两个 CI 明确并列：主设计 [−3.66, +2.32]
（排除 ≤2.3 点的 gain，不含小 loss）与归档 v6.0 [−0.19, +2.72]，并说明
“不让一个区间代表整篇论文”。

### B7. Coviello 对比深化（评审第 9 条）

结论新段：两结果不直接互斥的三个理由——visibility（意大利 below-line 可观测）、
阈值水平与边际信息含量（€209k/€5.2M vs 意大利低阈值）、制度年龄（新建 vs 协调）。
本文只主张更窄的结果。

### B8. Table 3 auxiliary 标注（评审第 6 条）

表注开头声明两个转化行是 auxiliary 而非 causal（v3.0 interval 方法依赖、
v4.0 单投标 event study 有 pre-trends），可置信的只有 v4.0 foreign-winner
event study（clean precise null，作为 corroboration 而非独立腿）。

### B9. 复现方式（第十轮新增）

```
python analysis/run_review9_loo.py           # v7.0 LOO（28 国逐个剔除）→ review9_loo.json
python analysis/run_review9_offer_robust.py  # n_offers 稳健性诊断 → review9_offer_robust.json
cd paper && python verify_round4.py          # 554 项论文↔归档逐条核对
```

---

## 第十一至十二轮：希腊修复闭环 + 密度 bootstrap 修正 + 全文重生成

### C1. 希腊剔除 bug 的修复与全链条重跑（第十一轮）

`run_v7_estimate_rd.py` 的国家码映射把 TED 的两字母代码 'GR' 误写成键
'GRC'，导致希腊全部 CN 公告被静默剔除，主设计实际只有 27 国而论文通篇
称 EU-28/28 聚类。已修复（'GR': 'GRC'）并同样修复
`run_v7_first_stage.py` 与 `run_transposition_contract.py` 的同类笔误，
删除陈旧缓存后从原始 zip 全量重跑：

- `cn_matched.csv` 4,458,599 → 4,688,892 行（28 国）；±20% 带 317,046 →
  339,636；匹配率 84.6%。
- **头条 +0.49 → −0.67 pp（SE 1.46, p = 0.650, CI [−3.66, +2.32],
  n = 179,065）**：符号翻转，结论方向不变（仍为无竞争收益的零结果），
  MDE 2.5 → 4.2pp。donut 三项全部不显著（+0.30/+0.16/−1.76）。
- 第一阶段：框架协议 −3.14pp（SE 1.16, p = 0.012, Holm 0.17）；
  投标期 −30.7 天（SE 23.3, p = 0.198）。安慰剂 0/7 不变。
- 外国中标份额 −1.21pp（SE 0.49, p = 0.019, n = 280,578）仍显著。
- 下游全部重建：`v7_clean_subsamples.json`（此前缺失，已恢复）、
  `v7_scale_placebo.json`、`v7_density_robust.json`、
  `v7_first_stage_procedures.json`、五个 review9 结果文件、五张图的数据
  与 PNG。
- 论文 6.1 新增更正披露段；摘要、表9、5.1、7.6、图1/3/4 题注、结论全部
  按新数字重写。

### C2. 覆盖率口径（第十一轮）

论文原称 "about 55% of the 8.58 million" 无出处。从原始 CN zip 单遍计数
（`run_review9_coverage.py`）：过滤后总数 **7,966,779**（含希腊），带估值
**4,688,892**，覆盖率 **58.9%**；3.1/7.5 原 "about a third" 一并废止。
主设计样本量表述重写：84.6% 仅为授奖匹配率，报价数可用率约 50%，
各结果可用率分别说明（3.1）。

### C3. 密度检验 bootstrap 修正（第十二轮）

`run_v7_density_test.py` 原用按国家名的 `isin` 子抽样（每次约保留 18/28 国、
无重复），低估聚类标准误。改为在预聚合的国家×箱计数矩阵上做有放回聚类
重抽（B=1000, seed=20261024, t(27)）：

- 1 箱比 0.8153：SE 0.132 → **0.153**，p 0.162 → **0.238**
- 2 箱比 0.8058：SE 0.110 → **0.127**，p 0.077 → **0.138**
- 结论方向不变（均不显著），5.1 正文、图3 题注、表12、verify_round4.py
  同步更新。
- 另新增 `run_review9_density_slope.py`：两侧局部 log 密度斜率
  （下方 +3.94/单位r, t=3.82；上方 +2.04, t=0.54）与外推比 0.89，
  论证 below-side 的稀疏是远离截止点的斜率而非截止点断点。

### C4. 其他修正（第十二轮）

- 主管线脚本补回仓库：`identification/run_v3.py`、`run_v4.py`、`run_v6.py`
  （此前 `results_v3/v4/v6.json` 无生产脚本）。三个脚本重跑输出写
  `report/`，与归档逐字段比对：**results_v3.json、results_v4.json、
  results_v6.json 全部零差异**。
- "8.93 million award notices" 无出处 → 原始 CAN 2013–2021 实测
  **6,882,163** 行，改为该数并注明口径。
- 第8节计数更新：63 个 Python 文件 / 11,250 行 / 55 个结果文件 /
  **556 项自动校验**（此前 47/8,369/49/497）。
- Makefile：verify 计数 537→556，补入 density_slope / figures_v7 /
  run_v6 三个目标。
- 重新生成 docx 并抽样核对关键数字（新值全部在、旧值除撤回段引用外
  全部清除）。
