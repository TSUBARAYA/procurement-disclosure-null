"""第六轮复核：论文数字逐条对回归档 JSON（法定阈值 + 原始数据干净重跑版）。

覆盖：Table 1 法定阈值、Table 2（归档）、Table 8（干净重跑）、Table 3、Table 4、
Table 5、Table 6（归档 + 重跑列）、Table 7（归档 + 重跑列）、7.1 密度审计
（归档 + 重跑）、6.4 价格边际、7.2 数字化分组、placebo 诊断、带宽×阶数、
归档复现校验。

用法：python verify_round4.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, 'materials', 'results')
FIG = os.path.join(ROOT, 'figures')

checks = []


def chk(label, paper, archive, tol=0.005):
    checks.append((label, paper, archive, abs(paper - archive) <= tol))


def j(*path):
    d = json.load(open(os.path.join(RES, path[0])))
    for k in path[1:]:
        d = d[k]
    return d


FIN = json.load(open(os.path.join(RES, 'v6_rerun_final.json')))
RR = json.load(open(os.path.join(RES, 'v6_full_rerun.json')))

# ---------- 0. Table 1 法定阈值 ----------
TRUE = {'2013': (200000, 5000000), '2014': (207000, 5186000), '2015': (207000, 5186000),
        '2016': (209000, 5225000), '2017': (209000, 5225000), '2018': (221000, 5548000),
        '2019': (221000, 5548000), '2020': (214000, 5350000), '2021': (214000, 5350000),
        '2022': (215000, 5382000), '2023': (215000, 5382000)}
for y, (su, w) in TRUE.items():
    chk(f'Table1 {y} S/U', su, FIN['thresholds'][y][0], 0.5)
    chk(f'Table1 {y} W', w, FIN['thresholds'][y][1], 0.5)

# ---------- 1. 归档复现校验（A 块必须逐位复现 results_v6.json） ----------
arch = json.load(open(os.path.join(RES, 'results_v6.json')))
A = RR['A_archived_wrong']
chk('复现 n', 326718, A['n_contracts'], 0.5)
chk('复现 n_above', 150444, A['n_above'], 0.5)
chk('复现 n_below', 176274, A['n_below'], 0.5)
for oc, v in [('single', 0.008222), ('log_offers', -0.003239),
              ('elec_share', 0.004699), ('foreign_win', 0.011465)]:
    chk(f'复现 main.{oc}', v, A['main'][oc]['tau'], 1e-6)
chk('复现 density.gap', -0.015684, A['density']['log_density_gap'], 1e-6)
chk('复现 placebo0.8', -0.05146, A['placebo']['0.8']['tau'], 1e-5)
chk('复现 placebo0.8 p', 0.146, A['placebo']['0.8']['p'], 0.0005)

# ---------- 2. Table 2（归档主表） ----------
m6 = j('results_v6.json', 'main', 'single')
chk('T2 single tau', 0.82, m6['tau'] * 100)
chk('T2 single SE', 0.68, m6['se'] * 100, 0.01)
chk('T2 single p', 0.234, m6['p'], 0.0005)
chk('T2 single CI lo', -0.56, m6['ci'][0] * 100, 0.01)
chk('T2 single CI hi', 2.21, m6['ci'][1] * 100, 0.01)
chk('T2 n', 326718, m6['n'], 0.5)

# ---------- 3. Table 8（干净重跑主表） ----------
T8 = {'single': (1.27, 0.71, 0.085, -0.19, 2.72, 327636, 1.36, 0.047),
      'log_offers': (-1.89, 1.49, 0.216, -4.96, 1.17, 327636, -2.11, 0.099),
      'elec_share': (0.38, 0.30, 0.212, -0.23, 1.00, 136288, 0.39, 0.194),
      'foreign_win': (1.22, 0.90, 0.185, -0.62, 3.06, 327636, 1.13, 0.163)}
for oc, (tau, se, p, lo, hi, n, tn, tp) in T8.items():
    v = FIN['main'][oc]['prereg']
    chk(f'T8 {oc} tau', tau, v['tau_pp'])
    chk(f'T8 {oc} SE', se, v['se_pp'], 0.01)
    chk(f'T8 {oc} p', p, v['p'], 0.0006)
    chk(f'T8 {oc} CI lo', lo, v['ci95_pp'][0], 0.01)
    chk(f'T8 {oc} CI hi', hi, v['ci95_pp'][1], 0.01)
    chk(f'T8 {oc} n', n, v['n'], 0.5)
    w = FIN['main'][oc]['none']
    chk(f'T8 {oc} noc tl', tn, w['tau_pp'])
    chk(f'T8 {oc} noc p', tp, w['p'], 0.0006)
chk('T8 band n', 327636, FIN['n_band20_value'], 0.5)

# ---------- 4. Table 3 ----------
d3 = j('results_v3.json', 'att', 'share_single_offer')
chk('v3 ATT', 3.37, d3['post_att'] * 100)
d4 = j('results_v4.json', 'main', 'share_single_offer', 'treated_post')
chk('v4 TWFE', 1.39, d4['beta'] * 100)
ci3 = j('review4_v3_ci_reconstruction.json', 'single')
chk('v3 CI lo', -1.34, ci3['cell_t_ci95_pp'][0])
chk('v3 CI hi', 8.09, ci3['cell_t_ci95_pp'][1])
chk('v3 cell SE', 1.99, ci3['cell_se_pp'], 0.01)

# ---------- 5. Table 4 ----------
sm = j('results_v4.json', 'main', 'sme_tender_share', 'treated_post')
chk('SME binary tau', 7.44, sm['beta'] * 100)
chk('SME binary SE', 4.30, sm['se'] * 100, 0.01)
chk('SME binary p', 0.095, sm['p'], 0.0005)
ds = j('results_v4.json', 'dose', 'sme_tender_share', 'intensity')
chk('SME dose tau', 33.42, ds['beta'] * 100)
chk('SME dose SE', 7.87, ds['se'] * 100, 0.01)
chk('SME dose p', 0.0002, ds['p'], 0.0002)
sd = json.load(open(os.path.join(FIG, 'sme_dose.json')))
chk('SME D1', 8.7, sd[0]['sme'] * 100, 0.05)
chk('SME D10', 54.6, sd[-1]['sme'] * 100, 0.05)

# ---------- 6. Table 5 ----------
he = json.load(open(os.path.join(RES, 'heterogeneity_v6.json')))
for key, lab, tau, se, p, n in [
    ('type_S', 'Supply', 1.46, 0.86, 0.099, 7753),
    ('type_U', 'Service', 0.81, 1.90, 0.673, 7661),
    ('type_W', 'Works', -0.03, 1.44, 0.984, 814),
    ('cpi_high', 'HighCPI', 0.79, 1.21, 0.522, 7775),
    ('cpi_low', 'LowCPI', 1.29, 1.26, 0.323, 8453),
    ('baseline', 'Baseline', 1.39, 0.98, 0.168, 16228),
]:
    chk(f'T5 {lab} tau', tau, he[key]['beta'] * 100)
    chk(f'T5 {lab} SE', se, he[key]['se'] * 100, 0.01)
    chk(f'T5 {lab} p', p, he[key]['p'], 0.0005)
    chk(f'T5 {lab} n', n, he[key]['n'], 0.5)

# ---------- 7. Table 6：归档列 + 重跑列 ----------
rv = json.load(open(os.path.join(RES, 'rd_robustness_valuespace_v7.json')))
for key, lab, tau, se, p, n in [
    ('baseline', 'T6 baseline', 0.95, 0.64, 0.148, 326718),
    ('donut_01', 'T6 donut1', 1.55, 0.71, 0.036, 305895),
    ('donut_02', 'T6 donut2', 1.40, 0.73, 0.065, 291340),
    ('donut_03', 'T6 donut3', 1.75, 0.83, 0.045, 275425),
    ('est_value', 'T6 estvalue', 2.30, 1.12, 0.050, 135444),
]:
    chk(lab + ' tau', tau, rv[key]['tau_pp'])
    chk(lab + ' SE', se, rv[key]['se_pp'], 0.01)
    chk(lab + ' p', p, rv[key]['p'], 0.0005)
    chk(lab + ' n', n, rv[key]['n'], 0.5)
for key, lab, tau, se, p, n in [
    ('baseline', 'T6r baseline', 1.36, 0.65, 0.047, 327636),
    ('donut01', 'T6r donut1', 1.75, 0.70, 0.018, 306623),
    ('donut02', 'T6r donut2', 1.65, 0.72, 0.029, 291984),
    ('donut03', 'T6r donut3', 1.89, 0.85, 0.034, 275931),
]:
    v = FIN['donut'][key]
    chk(lab + ' tau', tau, v['tau_pp'])
    chk(lab + ' SE', se, v['se_pp'], 0.01)
    chk(lab + ' p', p, v['p'], 0.0006)
    chk(lab + ' n', n, v['n'], 0.5)
v = json.load(open(os.path.join(RES, 'review8_estvalue_corrected.json')))['value20']['none']
chk('T6r estvalue tau', 1.22, v['tau_pp'])
chk('T6r estvalue SE', 1.05, v['se_pp'], 0.01)
chk('T6r estvalue p', 0.256, v['p'], 0.0006)
chk('T6r estvalue n', 150074, v['n'], 0.5)
EV = json.load(open(os.path.join(RES, 'review8_estvalue_corrected.json')))
chk('T6r estvalue logband tau', 1.17, EV['log20']['none']['tau_pp'])
chk('est masspoint n', 4608, EV['est_masspoint']['n_within_cent'], 1.0)
chk('est masspoint flips', 3743, EV['classification_flips']['n'], 1.0)

# ---------- 8. Table 7：重跑两列 ----------
for ctl, cols in [('none', [('baseline', 1.36, .047), ('donut01', 1.75, .018),
                            ('donut02', 1.65, .029), ('donut03', 1.89, .034)]),
                  ('type', [('baseline', 1.27, .085), ('donut01', 1.88, .006),
                            ('donut02', 1.83, .010), ('donut03', 2.13, .010)])]:
    for spec, tau, p in cols:
        v = FIN['grid'][ctl][spec]
        chk(f'T7r {ctl}/{spec} tau', tau, v['tau_pp'])
        chk(f'T7r {ctl}/{spec} p', p, v['p'], 0.0006)
chk('T7r est none tau', 1.22, EV['value20']['none']['tau_pp'])
chk('T7r est type tau', 0.85, EV['value20']['type']['tau_pp'])
chk('T7r est type p', 0.536, EV['value20']['type']['p'], 0.0006)
chk('T7r est prereg tau', 0.82, EV['value20']['prereg']['tau_pp'])
chk('T7r est logval tau', 1.13, EV['value20']['logval']['tau_pp'])
CPVs = json.load(open(os.path.join(RES, 'review8_cpv_statutory.json')))
for lab, tau, p, n in [('baseline', 1.17, .131, 327636), ('donut01', 1.82, .010, 306623),
                       ('donut02', 1.77, .017, 291984), ('donut03', 2.03, .020, 275931)]:
    chk(f'CPV {lab} tau', tau, CPVs[lab]['tau_pp'])
    chk(f'CPV {lab} p', p, CPVs[lab]['p'], 0.0006)
    chk(f'CPV {lab} n', n, CPVs[lab]['n'], 0.5)

# ---------- 9. 密度审计（重跑） ----------
D = FIN['density']
for lab, paper, arch_, tol in [
    ('gap', -0.01136, D['log_density_gap'], 0.00002),
    ('excess below %', 1.1, D['excess_below_pct'] * 100, 0.05),
    ('mechanical', -0.0306, D['mechanical_log_gap'], 0.0001),
    ('bias-corrected %', -1.90, D['bias_corrected_excess_below_pct'] * 100, 0.02),
    ('sym below', 15867, D['symmetric_full_bins']['below_mean'], 1.0),
    ('sym above', 16557, D['symmetric_full_bins']['above_mean'], 1.0),
    ('sym t', 0.88, D['symmetric_full_bins']['t_stat'], 0.005),
    ('sym p', 0.39, D['symmetric_full_bins']['p_value'], 0.005),
    ('mccrary', 1.007, D['mccrary_ratio'], 0.001),
    ('ex-mp below', 15857, D['ex_masspoint']['below_mean'], 1.0),
    ('ex-mp above', 15967, D['ex_masspoint']['above_mean'], 1.0),
    ('binom p', 0.29, D['binom_p_correct_null'], 0.006),
    ('p vs mechanical', 0.076, D['p_loggap_vs_mechanical'], 0.0006),
    ('bin -1', 16011, D['bin_minus1'], 0.5),
    ('bin 0', 19641, D['bin_0'], 0.5),
    ('masspoint', 5314, D['masspoint'], 0.5),
    ('masspoint exact', 5121, D['masspoint_exact'], 0.5),
    ('masspoint share %', 1.62, D['masspoint_share_pct'], 0.005),
    ('masspoint DEU %', 73.8, D['masspoint_deu_pct'], 0.05),
    ('masspoint award=est %', 90.1, D['masspoint_award_eq_est_pct'], 0.05),
    ('full award=est %', 38.4, D['full_award_eq_est_pct'], 0.05),
    ('n cells', 917, D['n_cells'], 0.5),
    ('left contracts', 176853, D['left_contracts'], 0.5),
    ('right contracts', 131142, D['right_contracts'], 0.5),
]:
    chk('density ' + lab, paper, arch_, tol)
# 归档对照
da = json.load(open(os.path.join(RES, 'review5_density_audit.json')))
chk('density archived gap', -0.0157, da['frozen_implementation']['log_density_gap'], 0.0001)
chk('density archived sym t', 0.77, da['corrected_tests']['symmetric_full_bins']['t_stat'], 0.005)
chk('density archived mccrary', 0.985, da['corrected_tests']['mccrary_local_linear']['ratio'], 0.001)
chk('density archived masspoint', 4659, da['masspoint_profile']['n'], 0.5)

# ---------- 10. 价格边际 ----------
P = FIN['price_margin']
chk('price single %', 5.95, P['single_mean_pct'], 0.005)
chk('price multi %', 6.61, P['multi_mean_pct'], 0.005)
chk('price RD pp', -1.55, P['discount_rd']['tau_pp'], 0.005)
chk('price RD p', 0.054, P['discount_rd']['p'], 0.0006)
chk('price coverage %', 95.4, P['coverage_pct'], 0.05)
chk('price clean share %', 53.1, P['clean_share_pct'], 0.05)
chk('price n clean', 166003, P['n_clean'], 0.5)

# ---------- 11. 样本构成 ----------
C = FIN['composition']
chk('n above', 150783, C['n_above'], 0.5)
chk('n below', 176853, C['n_below'], 0.5)
chk('mean offers below', 6.91, C['mean_offers_below'], 0.005)
chk('mean offers above', 5.94, C['mean_offers_above'], 0.005)
chk('ge3 below %', 50.3, C['share_ge3_below'], 0.05)
chk('ge3 above %', 49.0, C['share_ge3_above'], 0.05)

# ---------- 12. placebo 诊断 ----------
for c, nb, na in [('0.7', 0, 327636), ('0.8', 194, 327442),
                  ('1.2', 327630, 6), ('1.3', 327636, 0)]:
    chk(f'placebo {c} n_below', nb, FIN['placebo'][c]['n_below'], 0.5)
    chk(f'placebo {c} n_above', na, FIN['placebo'][c]['n_above'], 0.5)
chk('placebo 0.8 tau', -4.23, RR['B_corrected']['placebo']['0.8']['tau'] * 100, 0.01)
chk('placebo 0.8 p', 0.006, RR['B_corrected']['placebo']['0.8']['p'], 0.0006)

# ---------- 13. 带宽 × 阶数 ----------
for bw, lin, quad in [('10', 0.27, -1.04), ('15', 0.84, -0.31),
                      ('20', 1.27, 0.11), ('25', 1.33, 0.63)]:
    chk(f'bw{bw} lin', lin, FIN['bw_poly'][f'bw{bw}_lin']['tau_pp'])
    chk(f'bw{bw} quad', quad, FIN['bw_poly'][f'bw{bw}_quad']['tau_pp'])
bw6 = j('results_v6.json', 'bandwidth')
chk('bw archived 10', -0.23, bw6['0.1']['single']['tau'] * 100)
chk('bw archived 25', 0.94, bw6['0.25']['single']['tau'] * 100)

# ---------- 13b. 带宽 × 阶数：原始数据端到端校验（第八轮） ----------
BW25 = json.load(open(os.path.join(RES, 'review8_bw25_raw.json')))
for bw, lin, quad in [('10', 0.28, -1.04), ('15', 0.84, -0.30),
                      ('20', 1.27, 0.12), ('25', 1.33, 0.63)]:
    chk(f'raw bw{bw} lin', lin, BW25['grid'][f'bw{bw}_p1']['tau_pp'])
    chk(f'raw bw{bw} quad', quad, BW25['grid'][f'bw{bw}_p2']['tau_pp'])
chk('raw bw25 p', 0.037, BW25['grid']['bw25_p1']['p'], 0.0006)
chk('raw bw25 n', 403732, BW25['grid']['bw25_p1']['n'], 0.5)
chk('raw bw25 CI lo', 0.09, BW25['grid']['bw25_p1']['ci95_pp'][0], 0.005)
chk('raw bw25 CI hi', 2.58, BW25['grid']['bw25_p1']['ci95_pp'][1], 0.005)

# ---------- 14. 数字化分组（重跑，high 为数据异常） ----------
DS = FIN['digital_split']
chk('digital median', 1.0, DS['median_elec_share'], 1e-9)
chk('digital high n', 198, DS['high']['n'], 0.5)
chk('digital low tau', 1.23, DS['low']['tau_pp'])
chk('digital low p', 0.028, DS['low']['p'], 0.0006)
chk('digital low n', 136090, DS['low']['n'], 0.5)

# ---------- 15. 图数据 ----------
g4 = json.load(open(os.path.join(FIG, 'fig4_grid_corr.json')))
for bw, tau in [('0.1', 0.27), ('0.15', 0.84), ('0.2', 1.27), ('0.25', 1.33)]:
    chk(f'Fig4 bw{bw}', tau, g4['bandwidth'][bw]['tau_pp'])
chk('Fig4 poly2', 0.11, g4['poly']['2']['tau_pp'])
dn = json.load(open(os.path.join(FIG, 'density_corr.json')))
chk('Fig3 n', 327636, dn['n'], 0.5)
chk('Fig3 bin0', 19641, dn['counts'][dn['centers'].index(0.01)], 0.5)


# ---------- 16. v3.0 原生推断（第七轮） ----------
VI = json.load(open(os.path.join(RES, 'v3_inference_and_audit.json')))['v3_inference']
chk('v3 ATT pp', 3.374, VI['post_att_pp'], 0.001)
chk('v3 n cells', 8, VI['n_cells'], 0.5)
chk('v3 archived CI lo', -3.69, VI['archived_percentile_ci'][0], 0.005)
chk('v3 archived CI hi', 7.12, VI['archived_percentile_ci'][1], 0.005)
chk('v3 cell-t SE', 1.995, VI['cell_level_t']['se_pp'], 0.0005)
chk('v3 cell-t lo', -1.343, VI['cell_level_t']['ci'][0], 0.0005)
chk('v3 cell-t hi', 8.091, VI['cell_level_t']['ci'][1], 0.0005)
chk('v3 multiplier SE', 1.896, VI['influence_function_multiplier']['se_pp'], 0.0005)
chk('v3 multiplier lo', -0.32, VI['influence_function_multiplier']['ci'][0], 0.005)
chk('v3 multiplier hi', 7.14, VI['influence_function_multiplier']['ci'][1], 0.005)
chk('v3 cbootstrap SE', 1.65, VI['country_cluster_bootstrap']['se_pp'], 0.005)
chk('v3 cbootstrap lo', 0.28, VI['country_cluster_bootstrap']['ci'][0], 0.005)
chk('v3 cbootstrap hi', 6.65, VI['country_cluster_bootstrap']['ci'][1], 0.005)
chk('v3 cbootstrap B', 1449, VI['country_cluster_bootstrap']['n_replicates'], 1.0)
chk('v3 archived reproduced', 1, 1 if VI['archived_reproduced'] else 0, 0.5)

# ---------- 17. placebo battery（第七轮，±40% 带；第八轮改用整数阈值表） ----------
PB = json.load(open(os.path.join(RES, 'v7_placebo_bunching.json')))['placebo']
for c, n, tau, p in [('0.7', 250161, -0.62, 0.119), ('0.8', 314014, 0.16, 0.533),
                     ('1.2', 298741, -0.14, 0.802), ('1.3', 232088, -1.14, 0.005)]:
    chk(f'placebo40 {c} n', n, PB[c]['n'], 0.5)
    chk(f'placebo40 {c} tau', tau, PB[c]['tau'] * 100, 0.005)
    chk(f'placebo40 {c} p', p, PB[c]['p'], 0.0006)
chk('placebo40 1.3 CI lo', -1.90, PB['1.3']['ci'][0] * 100, 0.005)
chk('placebo40 1.3 CI hi', -0.37, PB['1.3']['ci'][1] * 100, 0.005)
chk('placebo40 1.3 SE', 0.37, PB['1.3']['se'] * 100, 0.005)
chk('placebo40 1.3 n_below', 173546, PB['1.3']['n_below'], 0.5)
chk('placebo40 1.3 n_above', 58542, PB['1.3']['n_above'], 0.5)
chk('placebo40 true tau', 1.27, PB['true_1.0']['tau'] * 100, 0.005)
chk('placebo40 0.8 n_below', 168693, PB['0.8']['n_below'], 0.5)
chk('placebo40 1.2 n_above', 116563, PB['1.2']['n_above'], 0.5)

# ---------- 17b. 断点剖面（第八轮） ----------
PR = json.load(open(os.path.join(RES, 'review8_placebo130_profile.json')))
for c, tau, p, n in [('0.70', -0.62, 0.119, 250161), ('0.75', 0.85, 0.045, 301234),
                     ('0.80', 0.16, 0.533, 314014), ('0.85', -1.02, 0.061, 319332),
                     ('0.90', -1.13, 0.013, 320319), ('0.95', 0.26, 0.555, 323047),
                     ('1.00', 1.27, 0.080, 327636), ('1.05', 1.25, 0.059, 327421),
                     ('1.10', 0.24, 0.598, 328161), ('1.15', -0.33, 0.334, 325961),
                     ('1.20', -0.14, 0.802, 298741), ('1.25', -1.25, 0.013, 267160),
                     ('1.30', -1.14, 0.005, 232088), ('1.35', -0.90, 0.296, 203356),
                     ('1.40', 0.54, 0.895, 173099)]:
    v = PR['cutoff_profile_linear'][c]
    chk(f'profile {c} tau', tau, v['tau_pp'], 0.006)
    chk(f'profile {c} p', p, v['p'], 0.0006)
    chk(f'profile {c} n', n, v['n'], 0.5)
chk('profile slope', 0.821, PR['profile_shape']['trend_slope_pp_per_cutoff'], 0.002)
chk('profile z 1.30', -1.71, PR['profile_shape']['z_1.30_vs_trend'], 0.02)
chk('profile quad 1.00', 0.12, PR['cutoff_profile_quadratic']['1.00']['tau_pp'], 0.006)
chk('profile quad 1.30', -0.60, PR['cutoff_profile_quadratic']['1.30']['tau_pp'], 0.006)
chk('holm 1.30', 0.0245, PR['holm']['1.30'], 0.0002)
chk('holm 1.00', 0.3184, PR['holm']['1.00'], 0.0002)

# ---------- 17c. log_value 共线性（第八轮） ----------
CO = json.load(open(os.path.join(RES, 'review8_logvalue_collinearity.json')))
chk('coll corr cy_type', 1.0, CO['within_cell_collinearity']['corr_logvalue_r_within_cy_type'], 1e-6)
chk('coll vif>4e6', 1, 1 if CO['vif_logvalue']['vif'] > 4e6 else 0, 0.5)
chk('coll flips', 4246, CO['threshold_recovery']['flips_in_band'], 0.5)
for lab, tau, p in [('none', 1.359, 0.047), ('logval', 1.38, 0.047),
                    ('type', 1.269, 0.085), ('prereg', 1.268, 0.085)]:
    chk(f'coll ctl {lab} tau', tau, CO['control_sets'][lab]['tau_pp'], 0.002)

# ---------- 17d. 族校正 / LOO / 窗口 / 构成 / 价格（第八轮） ----------
CR = json.load(open(os.path.join(RES, 'review8_corrections.json')))
for ctl, donut, bonf, holm, rw in [('none', 'donut01', 0.072, 0.072, 0.040),
                                   ('type', 'donut01', 0.0244, 0.0244, 0.032),
                                   ('type', 'donut03', 0.0384, 0.0288, 0.040),
                                   ('none', 'est_value', 1.0, 0.2559, 0.211),
                                   ('type', 'est_value', 1.0, 0.5355, 0.486)]:
    chk(f'corr {ctl}/{donut} bonf', bonf, CR['corrections'][ctl]['bonferroni'][donut], 0.0002)
    chk(f'corr {ctl}/{donut} holm', holm, CR['corrections'][ctl]['holm'][donut], 0.0002)
    chk(f'corr {ctl}/{donut} rw', rw, CR['corrections'][ctl]['romano_wolf'][donut], 0.0002)
chk('LOO min', 1.39, CR['loo_donut01_none']['min'], 0.006)
chk('LOO max', 2.32, CR['loo_donut01_none']['max'], 0.006)
chk('log window prereg tau', 1.17, CR['log_window']['prereg']['tau_pp'])
chk('log window n', 323519, CR['log_window']['n'], 0.5)
chk('split 2013_21 tau', 1.42, CR['window_split']['2013_2021']['prereg']['tau_pp'])
chk('split 2022_23 tau', 0.83, CR['window_split']['2022_2023']['prereg']['tau_pp'])
chk('split 2022_23 n', 85656, CR['window_split']['2022_2023']['n'], 0.5)
chk('comp share 2022_23', 26.1, CR['composition']['share_2022_23_pct'], 0.05)
chk('comp offer coverage', 97.1, CR['composition']['offer_field_coverage_pct'], 0.05)
chk('comp offers below', 6.91, CR['composition']['mean_offers_below'], 0.005)
chk('comp offers above', 5.94, CR['composition']['mean_offers_above'], 0.005)
chk('price mean award', 213582, CR['price_descriptive']['mean_award'], 1.0)

# ---------- 18. bunching 重建（第七轮） ----------
BU = json.load(open(os.path.join(RES, 'v7_placebo_bunching.json')))['bunching']
chk('bunching preferred', 3287, BU['archived_script_replica']['excess_contracts'], 1.0)
chk('bunching boot lo', 2132, BU['bootstrap']['ci95'][0], 1.0)
chk('bunching boot hi', 4592, BU['bootstrap']['ci95'][1], 1.0)
chk('bunching boot sd', 610, BU['bootstrap']['sd'], 1.0)
chk('bunching neg share', 0.0, BU['bootstrap']['share_negative'], 0.001)
g = BU['sensitivity_grid']
for w, order, v in [('w08', 'p3', 1069), ('w08', 'p5', 797), ('w08', 'p7', 1466),
                    ('w10', 'p3', 101), ('w10', 'p5', 1560), ('w10', 'p7', 502),
                    ('w15', 'p3', -602), ('w15', 'p5', -414), ('w15', 'p7', 800),
                    ('w20', 'p3', -3140), ('w20', 'p5', 1412), ('w20', 'p7', -1647),
                    ('w25', 'p3', -5727), ('w25', 'p5', 3287), ('w25', 'p7', -3023)]:
    chk(f'bunching grid {w}/{order}', v, g[w][order], 1.0)

# ---------- 19. 可复现性审计 ----------
AU = json.load(open(os.path.join(RES, 'v3_inference_and_audit.json')))['audit']
chk('audit reproducible', 29, sum(1 for v in AU.values() if v['status'] == 'reproducible'), 0.5)
chk('audit not reproducible', 2, sum(1 for v in AU.values() if v['status'] == 'NOT reproducible'), 0.5)
chk('audit total files', 31, len(AU), 0.5)


# ---------- 20. v7.0 主设计：法定估计价值 RD（第九轮，28 国含希腊） ----------
V7 = json.load(open(os.path.join(RES, 'v7_estimate_rd.json')))
chk('v7 n_cn', 4688892, V7['n_cn'], 0.5)
chk('v7 n_with_can', 3968395, V7['n_with_can'], 0.5)
chk('v7 match_rate', 0.8463, V7['match_rate'], 0.0005)
chk('v7 n_band20', 339636, V7['n_band20'], 0.5)
chk('v7 first stage tp bw5', -10.783, V7['first_stage_tender_period']['bw5_p1']['tau_pp'], 0.0005)
chk('v7 first stage tp bw10', -39.281, V7['first_stage_tender_period']['bw10_p1']['tau_pp'], 0.0005)
chk('v7 first stage tp bw10 p', 0.0608, V7['first_stage_tender_period']['bw10_p1']['p'], 0.0006)
chk('v7 first stage tp bw20', -35.345, V7['first_stage_tender_period']['bw20_p1']['tau_pp'], 0.0005)
chk('v7 first stage tp bw20 n', 339380, V7['first_stage_tender_period']['bw20_p1']['n'], 0.5)
chk('v7 single tau (无控制)', -0.668, V7['single']['bw20_p1']['tau_pp'], 0.0005)
chk('v7 single p (无控制)', 0.6255, V7['single']['bw20_p1']['p'], 0.0006)
chk('v7 single n (无控制)', 179096, V7['single']['bw20_p1']['n'], 0.5)
chk('v7 placebo sig count', 0, V7['n_placebo_sig'], 0.5)
for c, tau, n in [('0.70', 1.821, 93253), ('0.80', -0.482, 120210), ('0.90', -1.910, 146102),
                  ('1.00', -1.257, 179096), ('1.10', 1.950, 196866), ('1.20', -1.011, 220394),
                  ('1.30', -2.158, 227640), ('1.40', -0.909, 231773)]:
    chk(f'v7 placebo {c} tau', tau, V7['placebo_profile'][c]['tau_pp'], 0.006)
    chk(f'v7 placebo {c} n', n, V7['placebo_profile'][c]['n'], 0.5)
# B 轮：清洗后主结果（v7_scale_placebo.json，含类型哑变量的正确规格）
SP = json.load(open(os.path.join(RES, 'v7_scale_placebo.json')))
chk('v7 clean single tau', -0.669, SP['main_clean']['baseline']['tau_pp'], 0.0005)
chk('v7 clean single se', 1.456, SP['main_clean']['baseline']['se_pp'], 0.0005)
chk('v7 clean single p', 0.6496, SP['main_clean']['baseline']['p'], 0.0006)
chk('v7 clean single n', 179065, SP['main_clean']['baseline']['n'], 0.5)
chk('v7 clean single CI lo', -3.66, SP['main_clean']['baseline']['ci95_pp'][0], 0.005)
chk('v7 clean single CI hi', 2.32, SP['main_clean']['baseline']['ci95_pp'][1], 0.005)
for w, tau in [(1, 0.304), (2, 0.157), (3, -1.759)]:
    chk(f'v7 clean donut {w} tau', tau, SP['main_clean'][f'donut{w}']['tau_pp'], 0.0005)
chk('v7 clean fw tau', -1.214, SP['foreign_win']['type only']['tau_pp'], 0.0005)
chk('v7 clean fw se', 0.486, SP['foreign_win']['type only']['se_pp'], 0.0005)
chk('v7 clean fw p', 0.019, SP['foreign_win']['type only']['p'], 0.0006)
chk('v7 clean fw n', 280578, SP['foreign_win']['type only']['n'], 0.5)
chk('v7 clean fw+logaward tau', -1.561, SP['foreign_win']['type + log award value']['tau_pp'], 0.0005)
chk('v7 clean fw+logaward p', 0.017, SP['foreign_win']['type + log award value']['p'], 0.0006)
chk('v7 clean fw+logaward n', 177911, SP['foreign_win']['type + log award value']['n'], 0.5)
chk('v7 clean fw 2020-23 tau', -1.058, SP['foreign_win']['by_period']['2020-2023']['tau_pp'], 0.0005)
chk('v7 clean fw 2020-23 p', 0.0213, SP['foreign_win']['by_period']['2020-2023']['p'], 0.0006)
chk('v7 clean fw type U tau', -0.975, SP['foreign_win']['by_type']['U']['tau_pp'], 0.0005)
chk('v7 clean placebo nsig', 0, SP['placebo_clean']['n_sig'], 0.5)
chk('v7 clean placebo ntotal', 7, SP['placebo_clean']['n_total'], 0.5)
chk('v7 clean placebo 0.90 tau (最小 p)', -2.005, SP['placebo_clean']['estimates']['0.90']['tau_pp'], 0.005)
chk('v7 clean placebo 0.90 p', 0.4469, SP['placebo_clean']['estimates']['0.90']['p'], 0.0006)
chk('v7 clean placebo 0.70 tau', 1.879, SP['placebo_clean']['estimates']['0.70']['tau_pp'], 0.005)
# 第一阶段：程序结构（v7_first_stage_procedures.json）
FS = json.load(open(os.path.join(RES, 'v7_first_stage_procedures.json')))
chk('fs fra tau', -3.135, FS['first_stage_candidates']['fra_agreement']['tau_pp'], 0.0005)
chk('fs fra p', 0.0115, FS['first_stage_candidates']['fra_agreement']['p'], 0.0006)
chk('fs fra holm', 0.1725, FS['holm_first_stage']['fra_agreement'], 0.0006)
chk('fs INP p', 0.0379, FS['first_stage_candidates'].get('INP', FS['top_type_rd']['INP'])['p'], 0.0006)
chk('fs tender_period tau', -34.582, FS['first_stage_candidates']['tender_period']['tau_pp'], 0.0005)
chk('fs tender_period p', 0.1703, FS['first_stage_candidates']['tender_period']['p'], 0.0006)
chk('fs n_band', 339636, FS['n_band20'], 0.5)
# 图数据与论文一致（v7.0 图数据 JSON）
FV = json.load(open(os.path.join(RES, 'v7_scale_placebo.json')))
BD = json.load(open(os.path.join(ROOT, 'figures', 'fig2_estimates_v7.json')))
chk('fig2 v7 single tau matches', FV['main_clean']['baseline']['tau_pp'], BD['v7_single']['tau_pp'], 0.0005)
chk('fig2 v7 fw tau matches', FV['foreign_win']['type only']['tau_pp'], BD['v7_foreign_win']['tau_pp'], 0.0005)
# 密度（type FE 口径，来自 v7_density_robust）
DR = json.load(open(os.path.join(RES, 'v7_density_robust.json')))
chk('v7 single typeFE tau', -0.660, DR['single_splits']['all']['tau_pp'], 0.005)
chk('v7 single typeFE se', 1.455, DR['single_splits']['all']['se_pp'], 0.01)
chk('v7 single typeFE p', 0.6538, DR['single_splits']['all']['p'], 0.0006)
chk('v7 single_lot tau', -1.766, DR['single_splits']['single_lot']['tau_pp'], 0.005)
chk('v7 y2013_2016 tau', -3.288, DR['single_splits']['y2013_2016']['tau_pp'], 0.005)
chk('v7 bin_minus1', 16274, DR['bin_counts']['-1'], 0.5)
chk('v7 bin_0', 19960, DR['bin_counts']['0'], 0.5)
chk('v7 balance tender diff', -0.404, V7['balance']['tender_period']['diff'], 0.0005)
chk('v7 balance tender t', -6.387, V7['balance']['tender_period_t']['t'], 0.0006)
chk('v7 balance lots diff', -1.256, V7['balance']['lots']['diff'], 0.01)
chk('v7 balance gpa diff', -0.017, V7['balance']['gpa']['diff'], 0.005)
# 密度聚类 bootstrap（第九轮重建，28 国）
DT = json.load(open(os.path.join(RES, 'v7_density_test.json')))
chk('v7 density ratio 1bin', 0.8153, DT['density_ratio_1bin'], 0.0005)
chk('v7 density se 1bin', 0.1531, DT['se_1bin'], 0.0006)
chk('v7 density p 1bin', 0.2381, DT['p_1bin'], 0.0006)
chk('v7 density ratio 2bin', 0.8058, DT['density_ratio_2bin'], 0.0005)
chk('v7 density se 2bin', 0.1269, DT['se_2bin'], 0.0006)
chk('v7 density p 2bin', 0.1377, DT['p_2bin'], 0.0006)
chk('v7 frozen 12v9 below', 154406, DT['frozen_12v9']['below'], 0.5)
chk('v7 frozen 12v9 log gap', 0.3557, DT['frozen_12v9']['log_gap'], 0.0005)
# 清洗与子样本（v7_clean_subsamples.json，28 国）
CS = json.load(open(os.path.join(RES, 'v7_clean_subsamples.json')))
chk('cs single tau', -0.669, CS['main_clean']['single']['tau_pp'], 0.0005)
chk('cs n_offers tau (份)', 0.202, CS['main_clean']['n_offers']['tau_pp'] / 100, 0.0005)
chk('cs n_offers 2013-16 (份)', 0.327, CS['n_offers_subsamples']['2013-2016']['tau_pp'] / 100, 0.0005)
chk('cs tender tau', -30.728, CS['main_clean']['tender_period']['tau_pp'], 0.0005)
chk('cs elec tau', -0.682, CS['main_clean']['elec_share']['tau_pp'], 0.0005)
chk('cs 2013-16 tau', -3.342, CS['single_subsamples']['2013-2016']['tau_pp'], 0.0005)
chk('cs 2013-16 p', 0.0257, CS['single_subsamples']['2013-2016']['p'], 0.0006)
chk('cs 2013-16 n', 20781, CS['single_subsamples']['2013-2016']['n'], 0.5)
chk('cs 2013-16 S tau', -4.791, CS['single_subsamples']['2013-2016 S']['tau_pp'], 0.0005)
chk('cs 2013-16 S p', 0.0009, CS['single_subsamples']['2013-2016 S']['p'], 0.0006)
chk('cs 2013-16 W tau', -9.371, CS['single_subsamples']['2013-2016 W']['tau_pp'], 0.0005)
chk('cs n_offers 2013-16 tau', 32.655, CS['n_offers_subsamples']['2013-2016']['tau_pp'], 0.0005)
chk('cs highpub 1.10 sig', -5.742, DR['placebo_highpub']['1.10']['tau_pp'], 0.005)
chk('cs highpub est', 2.074, DR['single_highpub_cy']['tau_pp'], 0.0005)
chk('cs award sentinel rule total', 1608, CS['cleaning']['award_value_sentinel'], 0.5)
chk('cs n_offers invalid', 848, CS['cleaning']['n_offers_invalid'], 0.5)
chk('cs value_est out of range', 46951, CS['cleaning']['value_est_out_of_range'], 0.5)
# 第九轮补算（review9_paper_numbers.json）
R9 = json.load(open(os.path.join(RES, 'review9_paper_numbers.json')))
chk('r9 headline tau', -0.669, R9['headline']['tau_pp'], 0.0005)
chk('r9 headline G', 28, R9['headline']['G'], 0.5)
chk('r9 MDE', 4.23, R9['mde_pp'], 0.01)
chk('r9 masspoint n', 2823, R9['masspoint_0.01% 内']['n'], 0.5)
chk('r9 masspoint deu', 21.7, R9['masspoint_0.01% 内']['deu_share'], 0.05)
chk('r9 n_bw5_28', 88954, R9['n_bw5_28'], 0.5)
chk('r9 clean sentinel exact', 14, R9['clean_counts']['award_sentinel_exact'], 0.5)
chk('r9 clean nonpos', 1594, R9['clean_counts']['award_nonpos'], 0.5)
chk('r9 n_offers ge999', 420, R9['clean_counts']['n_offers_ge999'], 0.5)
chk('r9 elec gt offers', 994, R9['clean_counts']['elec_gt_offers'], 0.5)
chk('r9 first stage clean bw20 tau', -30.728, R9['first_stage_clean_type']['bw20']['tau_pp'], 0.0005)
chk('r9 first stage clean bw10 tau', -32.384, R9['first_stage_clean_type']['bw10']['tau_pp'], 0.0005)
# 覆盖率分母（review9_cn_coverage.json）
CV = json.load(open(os.path.join(RES, 'review9_cn_coverage.json')))
chk('cov filtered total', 7966779, CV['total_filtered'], 0.5)
chk('cov with est', 4688892, CV['total_with_est'], 0.5)
chk('cov pct', 58.86, CV['coverage'], 0.01)
chk('cov grc filtered', 233744, CV['grc_filtered'], 0.5)
chk('cov grc with est', 230293, CV['grc_with_est'], 0.5)
chk('cov 2013 with est', 54453, CV['by_year']['2013']['with_est'], 0.5)
chk('cov 2021 with est', 806331, CV['by_year']['2021']['with_est'], 0.5)
# ---------- 20b. v7.0 LOO + n_offers 稳健性（第十轮，评审意见） ----------
LOO = json.load(open(os.path.join(RES, 'review9_loo.json')))
chk('LOO single lo', -1.300, LOO['single']['loo_min'], 0.005)
chk('LOO single hi', 0.490, LOO['single']['loo_max'], 0.005)
chk('LOO single nsig', 0, LOO['single']['n_significant'], 0.5)
chk('LOO single drop GRC tau', 0.490, LOO['single']['loo']['GRC']['tau_pp'], 0.005)
chk('LOO single drop GRC n', 164203, LOO['single']['loo']['GRC']['n'], 0.5)
chk('LOO single drop DEU tau', -0.558, LOO['single']['loo']['DEU']['tau_pp'], 0.005)
chk('LOO single drop FRA tau', -1.046, LOO['single']['loo']['FRA']['tau_pp'], 0.005)
chk('LOO fw nsig', 27, LOO['foreign_win']['n_significant'], 0.5)
chk('LOO fw hi', -0.800, LOO['foreign_win']['loo_max'], 0.005)
chk('LOO fw drop FRA p', 0.059, LOO['foreign_win']['loo']['FRA']['p'], 0.0006)
OR = json.load(open(os.path.join(RES, 'review9_offer_robust.json')))
chk('offer baseline tau (份)', 0.202, OR['baseline']['tau'], 0.0005)
chk('offer winsor p99 tau', -0.007, OR['winsor_p99']['tau'], 0.0005)
chk('offer winsor p99 p', 0.9378, OR['winsor_p99']['p'], 0.0006)
chk('offer log1p p', 0.3797, OR['log1p']['p'], 0.0006)
chk('offer bw25 tau', -0.024, OR['bandwidth']['±25%']['tau'], 0.0005)
chk('offer raw diff', -0.16, OR['distribution']['raw_diff'], 0.005)
# 转化设计（第八轮）
TP = json.load(open(os.path.join(RES, 'transposition_never_control.json')))
chk('trans single ATT', 2.335, TP['single_notyet']['att_pp'], 0.0005)
chk('trans single pre e-4', 8.625, TP['single_notyet']['coefs']['-4']['coef_pp'], 0.0005)
chk('trans single pre p e-4', 0.033, TP['single_notyet']['coefs']['-4']['p'], 0.0006)
chk('trans single pre p e-3', 0.009, TP['single_notyet']['coefs']['-3']['p'], 0.0006)
chk('trans single pre p e-2', 0.006, TP['single_notyet']['coefs']['-2']['p'], 0.0006)
chk('trans fw ATT', 0.23, TP['foreign_win_notyet']['att_pp'], 0.0005)
chk('trans fw pre all insig', 1, 1 if TP['foreign_win_notyet']['pre_all_insignificant'] else 0, 0.5)
chk('trans fw post e0 p', 0.745, TP['foreign_win_notyet']['coefs']['0']['p'], 0.0006)
chk('trans fw noHUN ATT', 0.25, TP['foreign_win_noHUN']['att_pp'], 0.005)
chk('trans single noHUN ATT', 2.53, TP['single_noHUN']['att_pp'], 0.005)
# 面板口径校验
CL = json.load(open(os.path.join(RES, 'transposition_contract_level.json')))
chk('panel contracts', 5917167, CL['n_contracts'], 0.5)

# ---------- 报告 ----------
bad = [c for c in checks if not c[3]]
print(f'共校验 {len(checks)} 项，一致 {len(checks) - len(bad)} 项，不一致 {len(bad)} 项\n')
if bad:
    print('!!! 不一致项：')
    for lab, p_, a_, _ in bad:
        print(f'   {lab:34s} 论文={p_:>12}  归档={a_:>12}')
    sys.exit(1)
print('全部一致。')
