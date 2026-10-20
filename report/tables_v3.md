# NEO v3.0 合同级采购数据主结果（TED CAN，EU-28，2013-2021）

- 6782760 份合同 -> 252 个 country-year；种子 20261018

## 一、第一阶段（电子投标份额 = 改革机制直接度量）

- 处理后 2-3 年 ATT: 0.38216546666666673
- 动态（相对事件年）: -5:+0.129, -4:+0.025, -3:+0.011, -2:+0.001, 0:+0.053, 1:+0.210, 2:+0.303, 3:+0.405, 4:+0.651, 5:+0.678, 6:+0.863

## 二、主结局 ATT（CS 式，not-yet-treated 对照）

| 结局 | ATT(post 2-3) | 事前趋势 p | σ_Δ(年变化) |
|---|---|---|---|
| share_single_offer | 0.033738933333333346 | 0.6755413753436916 | 0.0189 |
| mean_offers | -10.4985668 | 0.3649753729528668 | 5.9920 |
| elec_offer_share | 0.38216546666666673 | 0.8314218484292248 | 0.1238 |
| foreign_winner_share | -0.0214372 | 0.17991570906971546 | 0.0051 |
| share_single_offer_works | -0.00018786666666667008 | 0.47224864909363473 | 0.0203 |

## 三、MDE 对比

- TED 单投标占比: MDE=0.0405（σ=0.0189）
- v2.0 WJP: MDE=0.1302（σ=0.0609）
- 改善倍数: 3.22x

## 四、剂量反应（连续电子化强度）

- share_single_offer ~ elec_lag1 + 双向FE: β=-0.0165 (se=0.0345, p=0.636)

## 五、判定

- 第一阶段为正: True
- 单投标 ATT CI 排除 0: False
- 事前趋势: pre_ok_share_single_offer=True, pre_ok_mean_offers=True, pre_ok_elec_offer_share=True, pre_ok_foreign_winner_share=True, pre_ok_share_single_offer_works=True