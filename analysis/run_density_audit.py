"""密度检验审计（第三轮修订）：复现 run_v6.density_test 冻结输出，诊断构造缺陷，
给出修正检验。输出 economy/materials/results/review5_density_audit.json

口径与 run_v6.py density_test 完全一致：bin = floor(r/0.02)，left = bin<=-1，
right = bin>=1（bin 0 即紧贴阈值上方的箱被两侧同时排除），二项零假设 p=0.5。
"""
import os, json, math
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'rd_sample_cache.csv')
OUT = r'C:\Users\OMEN\Desktop\economy\materials\results\review5_density_audit.json'
BW = 0.02
SEED = 42

d = pd.read_csv(CACHE)
r = d['r'].values
cell = (d['code'].astype(str) + '_' + d['year'].astype(str) + '_' + d['type'].astype(str)).values
b = np.floor(r / BW).astype(int)
cnt = pd.Series(b).value_counts()
bins = np.arange(-12, 10)                      # 22 个箱（样本窗 ln0.8 ~ ln1.2 截断两端）
n = np.array([cnt.get(k, 0) for k in bins], dtype=float)

out = {}

# ---- 1. 冻结实现复现 ----
L = n[bins <= -1].sum(); R = n[bins >= 1].sum()
dens_l, dens_r = L / 12, R / 9
gap_frozen = math.log((dens_r + 1) / (dens_l + 1))
p_frozen = stats.binomtest(int(R), int(L + R), 0.5).pvalue
out['frozen_implementation'] = {
    'left_contracts': int(L), 'left_bins': 12, 'right_contracts': int(R), 'right_bins': 9,
    'mean_per_bin_left': dens_l, 'mean_per_bin_right': dens_r,
    'log_density_gap': gap_frozen, 'excess_below_pct': dens_l / dens_r - 1,
    'binom_p_null_half': float(p_frozen),
    'bin_counts': {int(k): int(v) for k, v in zip(bins, n)},
}

# ---- 2. 构造缺陷诊断 ----
fL = (-0.22 - math.log(0.8)) / BW             # 左边缘箱填充比例 0.157
fR = (math.log(1.2) - 0.18) / BW              # 右边缘箱填充比例 0.116
fullL = n[(bins <= -1) & (bins >= -11)]       # 11 个完整左箱
fullR = n[(bins >= 0) & (bins <= 8)]          # 9 个完整右箱（含 bin 0）
dnull = (fullL.sum() + fullR.sum()) / (len(fullL) + len(fullR))
gap_null = math.log(((8 + fR) * dnull / 9 + 1) / ((11 + fL) * dnull / 12 + 1))
ratio_null = ((11 + fL) / 12) / ((8 + fR) / 9)   # 对称零假设下 dens_l/dens_r 的机械值
out['construction_diagnosis'] = {
    'edge_fill_left_bin_minus12': fL, 'edge_fill_right_bin_plus9': fR,
    'bin0_excluded_from_right': True,
    'mechanical_log_gap_under_symmetry': gap_null,
    'mechanical_excess_below_pct': ratio_null - 1,
    'observed_over_mechanical': abs(gap_frozen / gap_null),
    'bias_corrected_excess_below_pct': (dens_l / dens_r) / ratio_null - 1,
}

# ---- 3. 修正检验 ----
b_below = float(n[bins == -1][0]); b_above = float(n[bins == 0][0])
mL, mR = fullL.mean(), fullR.mean()
sL, sR = fullL.std(ddof=1), fullR.std(ddof=1)
se = math.sqrt(sL**2 / len(fullL) + sR**2 / len(fullR))
t = (mR - mL) / se
# McCrary 式局部线性外推（log 计数 ~ 箱中心，两侧分别拟合，评价到各自相邻箱中心）
def lin(cx, cy):
    A = np.vstack([cx, np.ones_like(cx)]).T
    coef, *_ = np.linalg.lstsq(A, np.log(cy), rcond=None)
    return coef
centers = (bins + 0.5) * BW
cl = centers[(bins >= -11) & (bins <= -1)]; cr = centers[(bins >= 0) & (bins <= 8)]
bl = lin(cl, fullL); br = lin(cr, fullR)
pred_l = math.exp(bl[0] * (-0.01) + bl[1]); pred_r = math.exp(br[0] * (0.01) + br[1])
# 剔除 r=0 堆点后的对称比较
mp_above = int(((r >= 0) & (r < 1e-4)).sum()); mp_below = int(((r < 0) & (r >= -1e-4)).sum())
n_ex = n.copy()
n_ex[bins == 0] -= mp_above; n_ex[bins == -1] -= mp_below
mL_ex = n_ex[(bins <= -1) & (bins >= -11)].mean(); mR_ex = n_ex[(bins >= 0) & (bins <= 8)].mean()
out['corrected_tests'] = {
    'local_bin_pair': {'below_bin_minus1': int(b_below), 'above_bin0': int(b_above),
                       'below_over_above': b_below / b_above},
    'symmetric_full_bins': {'below_mean': mL, 'above_mean': mR, 'above_over_below': mR / mL,
                            't_stat': float(t), 'p_value': float(2 * stats.t.sf(abs(t), 18))},
    'mccrary_local_linear': {'pred_below': pred_l, 'pred_above': pred_r, 'ratio': pred_l / pred_r},
    'symmetric_full_bins_ex_masspoint': {'below_mean': mL_ex, 'above_mean': mR_ex,
                                         'above_over_below': mR_ex / mL_ex},
    'binom_correct_null_12_over_21': {
        'observed_left_share': float(L / (L + R)), 'null_share': 12 / 21},
    'masspoint_at_zero': {'above_0_to_1e4': mp_above, 'below_minus1e4_to_0': mp_below},
}

# ---- 4. cluster bootstrap（按 国家-年-类型 单元）----
cells = pd.unique(cell); ci = {c: np.where(cell == c)[0] for c in cells}
rng = np.random.default_rng(SEED)
gaps, diffs, shares = [], [], []
for _ in range(2000):
    pick = rng.choice(cells, size=len(cells), replace=True)
    idx = np.concatenate([ci[c] for c in pick])
    bb = np.floor(r[idx] / BW).astype(int)
    c2 = pd.Series(bb).value_counts()
    nn = np.array([c2.get(k, 0) for k in bins], dtype=float)
    Lx = nn[bins <= -1].sum(); Rx = nn[bins >= 1].sum()
    gaps.append(math.log((Rx / 9 + 1) / (Lx / 12 + 1)))
    fl = nn[(bins <= -1) & (bins >= -11)]; fr = nn[(bins >= 0) & (bins <= 8)]
    diffs.append(fr.mean() - fl.mean())
    shares.append(Lx / (Lx + Rx))
gaps = np.array(gaps); diffs = np.array(diffs); shares = np.array(shares)
obs_share = float(L / (L + R))
z_gap = (gap_frozen - gap_null) / gaps.std()
z_share = (obs_share - 12 / 21) / shares.std()
out['cluster_bootstrap'] = {
    'n_cells': len(cells), 'n_replicates': 2000, 'seed': SEED,
    'log_gap': {'mean': float(gaps.mean()), 'sd': float(gaps.std()),
                'ci95': [float(np.percentile(gaps, 2.5)), float(np.percentile(gaps, 97.5))]},
    'full_bin_diff_above_minus_below': {
        'mean': float(diffs.mean()), 'sd': float(diffs.std()),
        'ci95': [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
        'observed': float(mR - mL),
        'p_two_sided_vs_zero': float((np.abs(diffs) >= abs(mR - mL)).mean())},
    'left_share': {'mean': float(shares.mean()), 'sd': float(shares.std()),
                   'ci95': [float(np.percentile(shares, 2.5)), float(np.percentile(shares, 97.5))]},
    'z_loggap_vs_mechanical_null': float(z_gap),
    'p_loggap_vs_mechanical_null': float(2 * stats.norm.sf(abs(z_gap))),
    'z_left_share_vs_12_21': float(z_share),
    'p_left_share_vs_12_21': float(2 * stats.norm.sf(abs(z_share))),
}

# ---- 5. r=0 堆点特征 ----
mp = d[(r >= 0) & (r < 1e-4)]
sub = mp.dropna(subset=['value_est'])
out['masspoint_profile'] = {
    'n': int(len(mp)), 'n_exact_zero': int((r == 0).sum()),
    'share_of_sample': float(len(mp) / len(d)),
    'top_countries': mp['code'].value_counts().head(5).to_dict(),
    'pct_award_equals_estimate': float((sub['value'] == sub['value_est']).mean()),
    'pct_award_equals_estimate_full_sample': float(
        (d.dropna(subset=['value_est'])['value'] == d.dropna(subset=['value_est'])['value_est']).mean()),
    'mean_offers': float(mp['n_offers'].mean()), 'mean_offers_full': float(d['n_offers'].mean()),
}

with open(OUT, 'w') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('written:', OUT)
print(json.dumps({k: (v if not isinstance(v, dict) else '...') for k, v in out.items()}, indent=1))
print('\n关键数字:')
print(f"  冻结: log gap {gap_frozen:.5f}, excess below {dens_l/dens_r-1:.2%}, p {p_frozen:.2e}")
print(f"  机械零值: log gap {gap_null:.5f} (虚假 excess below {ratio_null-1:.2%}); 观测/机械 = {abs(gap_frozen/gap_null):.0%}")
print(f"  偏差校正后 excess below: {(dens_l/dens_r)/ratio_null-1:.2%}")
print(f"  对称完整 bin: below {mL:.1f} vs above {mR:.1f} (t={t:.2f}, p={2*stats.t.sf(abs(t),18):.3f})")
print(f"  局部对偶: below {b_below:.0f} vs above {b_above:.0f}")
print(f"  McCrary 外推 ratio (below/above): {pred_l/pred_r:.4f}")
print(f"  cluster bootstrap: z_gap={z_gap:.2f} (p={2*stats.norm.sf(abs(z_gap)):.3f}), z_share={z_share:.2f} (p={2*stats.norm.sf(abs(z_share)):.3f})")
