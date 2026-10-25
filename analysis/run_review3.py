"""三轮审稿统计回应（审稿意见 2/3/4）

1. 控制变量修正：log_value 是 running variable 的组内单调变换，不得作为
   RD 控制变量。改为：无控制 / 仅合同类型哑变量；并加二次多项式敏感性。
2. Romano–Wolf stepdown（国家聚类 bootstrap）+ Holm，针对四个
   manipulation-robust 规格（donut ±1/2/3、估计价值）。
3. 真正的预处置协变量平衡：CPV 大类份额、国家份额（±5% 带，含 donut）。
4. donut 规格对组成的敏感性：type FE、type + CPV1 FE。
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
df = pd.read_csv(os.path.join(HERE, 'rd_sample_cache.csv'))
df['ratio_v'] = np.exp(df['r'])
df['tu'] = (df['type'] == 'U').astype(float)
df['tw'] = (df['type'] == 'W').astype(float)
df['cpv1'] = df['cpv2'].astype(str).str[0]


# ---------- 估计器 ----------
def rd_fit(d, runvar, treat, controls='none', poly=1):
    """返回 beta, se（国家聚类），用于点估计与 bootstrap"""
    d = d.dropna(subset=[runvar, treat, 'single']).copy()
    cols = [treat, runvar, f'{treat}_x_{runvar}']
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    if poly == 2:
        d['r2'] = d[runvar] ** 2
        d['ar2'] = d[treat] * d['r2']
        cols += ['r2', 'ar2']
    if controls in ('type', 'type_cpv1'):
        cols += ['tu', 'tw']
    if controls == 'type_cpv1':
        for c in sorted(d['cpv1'].unique()):
            if c not in ('3',):  # 3 为最大类，作基准
                d[f'c{c}'] = (d['cpv1'] == c).astype(float)
                cols.append(f'c{c}')
    y = d['single'].astype(float)
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([y.rename('y')] + [d[c].astype(float).rename(c) for c in cols]
                     + [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in cols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.pinv(Xd.T @ Xd)
    cl = d['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.maximum(np.diag(V), 0))
    p = 2 * (1 - stats.t.cdf(abs(beta[1] / se[1]), G - 1))
    return {'tau_pp': round(float(beta[1]) * 100, 2), 'se_pp': round(float(se[1]) * 100, 2),
            'p': round(float(p), 4), 'n': int(n)}


def make_samples():
    # 容差 1e-9：边界行（比值真值 0.8/1.2）必须包含在 ±20% 带内
    band = df[(df['ratio_v'] - 1).abs() <= 0.2 + 1e-9]
    samples = {
        'donut01': (band[(band['ratio_v'] - 1).abs() > 0.01], 'r', 'above'),
        'donut02': (band[(band['ratio_v'] - 1).abs() > 0.02], 'r', 'above'),
        'donut03': (band[(band['ratio_v'] - 1).abs() > 0.03], 'r', 'above'),
    }
    sub = df[(df['value_est'] > 0) & (df['value'] > 0)].copy()
    sub['ratio'] = sub['value'] / sub['value_est']
    clean = sub[(sub['ratio'] >= 0.5) & (sub['ratio'] <= 2.0)].copy()
    clean['log_thr'] = clean['log_value'] - clean['r']
    clean['r_est'] = np.log(clean['value_est']) - clean['log_thr']
    clean['above_est'] = (clean['value_est'] >= np.exp(clean['log_thr'])).astype(int)
    clean['ratio_est'] = clean['value_est'] / np.exp(clean['log_thr'])
    samples['est_value'] = (clean[(clean['ratio_est'] - 1).abs() <= 0.2 + 1e-9], 'r_est', 'above_est')
    return samples


samples = make_samples()

# ---------- 1. 控制集 × 多项式网格 ----------
grid = {}
for name, (d, rv, tr) in samples.items():
    grid[name] = {
        'noctl_lin': rd_fit(d, rv, tr, 'none', 1),
        'type_lin': rd_fit(d, rv, tr, 'type', 1),
        'type_quad': rd_fit(d, rv, tr, 'type', 2),
        'typecpv_lin': rd_fit(d, rv, tr, 'type_cpv1', 1),
    }
base = df[(df['ratio_v'] - 1).abs() <= 0.2 + 1e-9]  # same tolerance as make_samples
grid['baseline'] = {
    'noctl_lin': rd_fit(base, 'r', 'above', 'none', 1),
    'type_lin': rd_fit(base, 'r', 'above', 'type', 1),
    'type_quad': rd_fit(base, 'r', 'above', 'type', 2),
    'typecpv_lin': rd_fit(base, 'r', 'above', 'type_cpv1', 1),
}

# ---------- 2. Holm ----------
def holm(pvals, names):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = [None] * m
    running = 0.0
    for rank, idx in enumerate(order):
        hp = min(1.0, (m - rank) * pvals[idx])
        running = max(running, hp)
        adj[idx] = round(running, 4)
    return dict(zip(names, adj))


fam_names = ['donut01', 'donut02', 'donut03', 'est_value']
holm_res = {}
for ctl in ('noctl_lin', 'type_lin'):
    pv = [grid[n][ctl]['p'] for n in fam_names]
    holm_res[ctl] = holm(pv, fam_names)
    print(f'HOLM {ctl}:', holm_res[ctl])

# ---------- 3. Romano–Wolf（国家聚类 bootstrap）----------
def cluster_stats(d, runvar, treat, controls):
    """按国家聚合充分统计量（FE 组嵌套在国家内，demean 与 bootstrap 可交换）"""
    d = d.dropna(subset=[runvar, treat, 'single']).copy()
    d[f'{treat}_x_{runvar}'] = d[treat] * d[runvar]
    cols = [treat, runvar, f'{treat}_x_{runvar}']
    if controls == 'type':
        cols += ['tu', 'tw']
    keys = d['code'].astype(str) + '_' + d['year'].astype(str)
    allv = pd.concat([d['single'].astype(float).rename('y')] +
                     [d[c].astype(float).rename(c) for c in cols] +
                     [keys.rename('k'), d['code'].rename('g')], axis=1)
    num_cols = ['y'] + cols
    gm = allv.groupby('k')[num_cols].transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(d))] + [(allv[c] - gm[c]).values for c in cols])
    out = {}
    for g in np.unique(d['code'].values):
        m = (d['code'].values == g)
        Xg, yg = Xd[m], yd[m]
        out[g] = (Xg.T @ Xg, Xg.T @ yg, Xg, yg)
    return out, Xd.shape[1]


def boot_est(stats_g, weights, G, beta_obs=None):
    """返回 centered t = (beta - beta_obs)/se；beta_obs=None 时返回原始 t"""
    k = next(iter(stats_g.values()))[0].shape[0]
    XtX = np.zeros((k, k)); Xty = np.zeros(k)
    for i, g in enumerate(stats_g):
        XtX += weights[i] * stats_g[g][0]
        Xty += weights[i] * stats_g[g][1]
    XtXi = np.linalg.pinv(XtX)
    beta = XtXi @ Xty
    meat = np.zeros((k, k))
    for i, g in enumerate(stats_g):
        Xg, yg = stats_g[g][2], stats_g[g][3]
        s = weights[i] * (Xg.T @ (yg - Xg @ beta))
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1))
    se = np.sqrt(max(np.diag(V)[1], 1e-12))
    if beta_obs is None:
        return beta[1], beta[1] / se
    return (beta[1] - beta_obs) / se


rng = np.random.default_rng(20261021)
rw = {}
for ctl in ('none', 'type'):
    stats_list, G = [], 28
    per_spec = {}
    for name in fam_names:
        d, rv, tr = samples[name]
        s, k = cluster_stats(d, rv, tr, ctl)
        per_spec[name] = s
    clusters = sorted(set().union(*[set(s) for s in per_spec.values()]))
    # 各规格的国家集合相同（同一批国家），按国家重抽样
    tau_key = 'noctl_lin' if ctl == 'none' else 'type_lin'
    t_obs = {n: abs(grid[n][tau_key]['tau_pp'] / grid[n][tau_key]['se_pp'])
             for n in fam_names}
    tau_obs = {n: grid[n][tau_key]['tau_pp'] / 100 for n in fam_names}
    B = 1000
    t_boot = {n: np.zeros(B) for n in fam_names}
    for b in range(B):
        w = rng.multinomial(G, [1 / G] * G)
        wmap = dict(zip(clusters, w))
        for n in fam_names:
            s = per_spec[n]
            ws = np.array([wmap.get(g, 0) for g in s])
            try:
                # centered：施加了联合原假设的重抽样 t 分布
                t_boot[n][b] = abs(boot_est(s, ws, G, beta_obs=tau_obs[n]))
            except Exception:
                t_boot[n][b] = 0.0
    # stepdown：按 t_obs 从大到小依次检验并剔除
    adj = {}
    max_t = np.maximum.reduce([t_boot[n] for n in fam_names])
    prev = 0.0
    order = sorted(fam_names, key=lambda n: -t_obs[n])
    for step, n in enumerate(order):
        p_n = float((max_t >= t_obs[n]).mean())
        prev = max(prev, p_n)
        adj[n] = round(min(1.0, prev), 4)
        remaining = order[step + 1:]
        max_t = (np.maximum.reduce([t_boot[o] for o in remaining])
                 if remaining else np.zeros(B))
    rw[ctl] = {'t_obs': {n: round(t_obs[n], 3) for n in fam_names}, 'rw_adj_p': adj}
    print(f'RW {ctl}:', json.dumps(rw[ctl]))

# ---------- 4. 预处置协变量平衡（CPV 大类、国家份额）----------
def diff_means_clustered(d, outcome, treat='above'):
    dd = d.dropna(subset=[outcome, treat]).copy()
    a = dd[dd[treat] == 1][outcome].astype(float)
    b = dd[dd[treat] == 0][outcome].astype(float)
    diff = a.mean() - b.mean()
    g = dd.groupby('code').apply(lambda x: x.loc[x[treat] == 1, outcome].mean()
                                 - x.loc[x[treat] == 0, outcome].mean(), include_groups=False)
    n_g = len(g)
    se = float(np.sqrt(((g - diff) ** 2).sum() / (n_g * (n_g - 1))))
    p = 2 * (1 - stats.t.cdf(abs(diff / se), n_g - 1)) if se > 0 else np.nan
    return {'diff_pp': round(float(diff) * 100, 2), 'se_pp': round(se * 100, 2),
            'p': round(float(p), 3) if se > 0 else None}


band05 = df[(df['ratio_v'] - 1).abs() <= 0.05].copy()
band05_d = band05[(band05['ratio_v'] - 1).abs() > 0.01].copy()
bal = {'baseline_pm05': {}, 'donut01_pm05': {}}
top_cpv = df['cpv2'].astype(str).str[:2].value_counts().head(6).index.tolist()
for c in top_cpv:
    band05[f'cpv_{c}'] = (band05['cpv2'].astype(str).str[:2] == c).astype(float)
    band05_d[f'cpv_{c}'] = (band05_d['cpv2'].astype(str).str[:2] == c).astype(float)
    bal['baseline_pm05'][f'cpv{c}'] = diff_means_clustered(band05, f'cpv_{c}')
    bal['donut01_pm05'][f'cpv{c}'] = diff_means_clustered(band05_d, f'cpv_{c}')
# 大国份额
for g in ['DEU', 'FRA', 'POL', 'ESP', 'ITA']:
    band05[f'g_{g}'] = (band05['code'] == g).astype(float)
    band05_d[f'g_{g}'] = (band05_d['code'] == g).astype(float)
    bal['baseline_pm05'][f'share_{g}'] = diff_means_clustered(band05, f'g_{g}')
    bal['donut01_pm05'][f'share_{g}'] = diff_means_clustered(band05_d, f'g_{g}')

res = {'controls_poly_grid': grid, 'holm': holm_res, 'romano_wolf': rw, 'prebalance_cpv_country': bal,
       'note': 'log_value 为 running variable 的组内单调变换，不作控制；'
               'elec_share 为第一阶段（post-treatment），不作控制。'}
out = os.path.join(ROOT, 'materials', 'results', 'review3_inference.json')
json.dump(res, open(out, 'w'), indent=2)
print('saved', out)
print(json.dumps(grid, indent=1))
print(json.dumps(bal, indent=1)[:2000])
