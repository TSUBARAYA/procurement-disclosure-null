"""NEO v4.0 — 合同级（箱面板）估计量

两维交互固定效应（country×year + cpv2×year）的交替投影离差化 + WLS +
国家聚类稳健 SE。用于合同级回归：用箱内合同特征吸收组成变异。

参考文献口径：
- 交互 FE 离差化：Jochmans (2017) alternating projections
- 聚类 SE：Liang-Zeger (1986)
"""
import numpy as np
import pandas as pd
from scipy import stats


def demean(y, X, groups, w, n_iter=50, tol=1e-10):
    """交替投影离差化：对多组 FE 加权去均值。返回离差化后的 (y, X)。

    注意：处理变量在 country×year 层面时，FE 必须用 country + year 分离
    （country×year 会吸收处理变量导致共线）。
    """
    y = np.asarray(y, float).copy()
    X = np.asarray(X, float).copy()
    w = np.asarray(w, float).copy()
    for _ in range(n_iter):
        y0, X0 = y.copy(), X.copy()
        for g in groups:
            df = pd.DataFrame({'g': g})
            df['y'] = y * w
            for j in range(X.shape[1]):
                df[f'x{j}'] = X[:, j] * w
            df['sw'] = w
            m = df.groupby('g').sum()
            my = m['y'] / m['sw']
            for j in range(X.shape[1]):
                m[f'x{j}'] = m[f'x{j}'] / m['sw']
            y = y - df['g'].map(my).values
            for j in range(X.shape[1]):
                X[:, j] = X[:, j] - df['g'].map(m[f'x{j}']).values
        if max(np.max(np.abs(y - y0)), np.max(np.abs(X - X0))) < tol:
            break
    return y, X


def wls_cluster(y, X, w, cluster):
    """WLS + 聚类稳健 SE。返回 dict(beta, se, t, p, n, dof)。"""
    sw = np.sqrt(w)
    yw, Xw = y * sw, X * sw[:, None]
    XtX = Xw.T @ Xw
    XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ (Xw.T @ yw)
    resid = y - X @ beta
    # meat: sum over clusters of (sum_i X_i e_i w_i)(...)'  （转置 X 的标准化）
    u = resid * w
    Xu = X * u[:, None]
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in pd.unique(cluster):
        idx = cluster == g
        s = Xu[idx].sum(axis=0)
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    n = len(y)
    G = len(pd.unique(cluster))
    dof = max(G - 1, 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = beta / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), dof))
    return {'beta': beta, 'se': se, 't': t, 'p': p, 'n': n, 'dof': dof,
            'ci_lo': beta - stats.t.ppf(0.975, dof) * se,
            'ci_hi': beta + stats.t.ppf(0.975, dof) * se}


def contract_regression(panel, outcome, treat_col, controls, weights='n_contracts',
                        extra_x=None):
    """合同级回归：Y ~ treat + controls + type dummies + country + year + cpv2×year。

    处理变量在 country×year 层面 → FE 用 country + year + cpv2×year 分离
    （country×year 会吸收处理变量）。合同特征控制吸收组成变异。
    WLS，SE 聚类到国家。
    """
    d = panel.dropna(subset=[outcome, treat_col]).copy()
    if len(d) < 50:
        return {'error': '样本不足'}
    y = d[outcome].values
    w = d[weights].values if weights in d.columns else np.ones(len(d))
    parts = [d[[treat_col]].values.astype(float)]
    names = [treat_col]
    for c in controls:
        parts.append(d[[c]].values.astype(float))
        names.append(c)
    for t in ['S', 'U']:  # W 为基准
        parts.append((d['type'] == t).values.astype(float)[:, None])
        names.append(f'type_{t}')
    if extra_x:
        for c in extra_x:
            parts.append(d[[c]].values.astype(float))
            names.append(c)
    X = np.column_stack(parts)
    groups = [d['code'].astype(str).values,
              d['year'].astype(str).values,
              d['cpv2'].astype(str).values + '_' + d['year'].astype(str).values]
    yd, Xd = demean(y, X, groups, w)
    r = wls_cluster(yd, Xd, w, d['code'].astype('category').cat.codes.values)
    out = {'n': r['n'], 'dof': r['dof'], 'names': names}
    for i, nm in enumerate(names):
        out[nm] = {'beta': float(r['beta'][i]), 'se': float(r['se'][i]),
                   'p': float(r['p'][i]),
                   'ci': [float(r['ci_lo'][i]), float(r['ci_hi'][i])]}
    return out


def mde_from_panel(ted, outcome, window=(2013, 2015)):
    """从 TED 箱面板估计 MDE：结局在国家-年层面的年度变化 sd（按合同数加权）。"""
    d = ted[['code', 'year', outcome, 'n_contracts']].dropna()
    recs = []
    for (code, year), g in d.groupby(['code', 'year']):
        recs.append({'code': code, 'year': year, outcome:
                     float(np.average(g[outcome], weights=g['n_contracts']))})
    agg = pd.DataFrame(recs)
    ch = []
    for c, g in agg.groupby('code'):
        g = g.sort_values('year')
        s = g[outcome].dropna()
        if len(s) >= 3:
            ch.append(s.diff().std())
    sd = float(np.nanmean(ch))
    return {'sigma_change': sd, 'n_countries': len(ch)}
