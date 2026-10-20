# NEO 数据字典（data_dictionary.md）

版本：v1.0.0 | 冻结日期：2026-10-18 | 面板：`data/interim/panel.csv`（2,338 行 = 167 国 × 2010–2023，部分国家有缺年）

> 状态规范（预注册 data_governance）：**verified** = 官方来源 URL + 本地副本 + sha256 指纹；**unverified** = 有来源未核对；**placeholder** = 结构占位禁止入检。本面板所有进入检验的列均为 verified。

## 1. 因变量

| 变量 | 方向 | 定义 | 来源 | 覆盖 | 状态 |
|---|---|---|---|---|---|
| `corruption_objective` | 越高越腐败 | **主结局**。WJP 法治指数因子2"腐败缺席"总分（0–1，越高越清廉）取 1−x 转换 | World Justice Project Rule of Law Index, Factor 2，经 World Bank Data360（2013–2025，143 国） | 2013–2025（2017 原缺，1 年缺口线性插值，见 missing_log.csv） | verified |
| `obj_exec` / `obj_jud` / `obj_polmil` / `obj_leg` | 越高越腐败 | 客观子指标：行政/司法/警察军队/立法部门"不以公职谋私"（1−x） | WJP 因子2 四个分项（WJP_ROL_2_1..2_4） | 同上 | verified |
| `corruption_wgi` | 越高越腐败 | 世行 WGI 控制腐败估计（−2.5~2.5）线性映射到 0–1：`1−(v+2.5)/5` | World Bank WGI CC.EST | 149 国 2010–2023 | verified |
| `corruption_vdem` | 越高越腐败 | V-Dem 政治腐败指数 v2x_corr（0–1） | V-Dem via Our World in Data | 148 国 2010–2023 | verified |
| `corruption_cpi` | 越高越腐败 | TI CPI（0–100，0=最清廉）映射：`(100−score)/100`；2010/2011 回填 2012 值 | Transparency International CPI via OWID | 143 国 2012–2023 | verified |
| `pubcorr_vdem` | 越高越腐败 | V-Dem 公共部门腐败指数 v2x_pubcorr（0–1） | V-Dem via OWID | 201 国（长历史，取 2010+） | verified |

**诚实声明（写入报告）**：`corruption_objective` 不是行政记录（审计/采购/司法立案），而是 WJP 的家庭+专家调查中关于**贿赂经历与风险**的分项合成。全球范围可按年获得的行政腐败记录（政府采购单一来源比例、司法立案率等）无公开年度面板；本项目的"客观"是相对纯感知指数的经历/风险口径，该局限在主结果表与 README 中显著标注。

## 2. 处理变量（来自 `data/external/reform_events.csv`，逐条带来源）

| 字段 | 说明 |
|---|---|
| `treated` | 1 = 该国在登记库中有合格事件（前后各 ≥3 年 WJP 客观数据） |
| `event_year` | 该国**最早**合格事件的生效年 |
| `event_time` | 年份 − event_year（事件研究相对时间） |

事件组（26 个合格国）：EU/GBR 2014/24/EU 采购指令转化截止 2016-04-18（21 国合格）；日本 My Number 2016-01；印度 GeM 2016-08-09；乌克兰 ProZorro 2016-08-01；智利 Mercado Público 强制 2018-04-01；哥伦比亚 SECOP II 强制 2020。乌克兰 Diia（2020-02-06）为第二事件，按规则不覆盖首事件。

## 3. 调节变量（H2，全部取**事件前三年均值**防事后操纵）

| 变量 | 方向 | 定义 | 来源 |
|---|---|---|---|
| `separation_index` | 越高越分权 | WJP 因子1"政府权力约束"总分（0–1） | WJP ROL Factor 1 via Data360 |
| `transparency` | 越高越开放 | WJP 因子3"开放政府"总分（0–1） | WJP ROL Factor 3 via Data360 |

## 4. 协变量

| 变量 | 定义 | 来源 | 覆盖 |
|---|---|---|---|
| `digital_share` | 互联网用户率 ÷100（0–1） | World Bank WDI IT.NET.USER.ZS | 149 国 2010–2023 |
| `gdp_pc_ppp` | 人均 GDP（PPP，不变价，2017 国际元） | World Bank WDI NY.GDP.PCAP.PP.KD | 149 国 2010–2023 |
| `egdi` | UN 电子政务发展指数（0–1） | UN DESA via Data360 | 193 国 2003–2020 |
| `digital_id_online` | 拥有在线数字身份的成人比例（%） | World Bank ID4D/Findex E_ID | 58 国，2024（三年一次） |
| `shock_pol` | V-Dem 选举民主指数年度绝对变化（政治断裂） | V-Dem via OWID | 147 国 2010–2023 |
| `shock_econ` | 人均 GDP 年增长率 | World Bank WDI | 147 国 |
| `shock_conf` | UCDP/PRIO 冲突死亡对数 log(1+deaths) | UCDP via OWID | 147 国 |

## 5. 缺失与插值规则（不静默填补）

1. 仅对**单个年份缺口**（前后年均有值）做线性插值，全部记录于 `missing_log.csv`（1,159 格）。
2. WJP 无 2017 年数据 → 2017 年客观值均为 2016/2018 插值（113 国），事件研究中 event_time=1 的解释须考虑此点。
3. CPI 2010/2011 回填 2012（序列对齐，H8c 类窗口不用 2010–2011）。
4. 其余一律留空；检验时按案例删除并报告覆盖数，不做多重插补冒充观测。

## 6. 数据指纹

全部文件 sha256 前 16 位于 `data/raw/manifest.json`。任何重新抓取须比对指纹；不一致 → 运行作废并记入 `runs/failed/`。
