"""v7.0 续：密度断点的正规局部线性检验 + 关键稳健性。

上一轮发现 CN 估计价值的"12 箱 vs 9 箱"比较显示下方少 27%。这可能是
发布意愿随合同规模平滑下降（不是断点），也可能是阈值处真实的选择性发布。
必须用 McCrary 式局部线性外推区分。

另外补：
  1. 第一阶段细分（分 2013 / 2014-2016 / 2017-2023，因指令逐年生效）
  2. 只用在阈值以下发布率高的 country-year（选择性问题）
  3. binscatter 数据
  4. 多批次公告的处理

输出 materials/results/v7_density_robust.json
"""
import json, math, os, sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'materials', 'results', 'v7_density_robust.json')
TOL = 1e-9
sys.path.insert(0, HERE)


def rd(d, outcome, poly=1, cluster='code'):
    dd = d.dropna(subset=[outcome, 'r']).copy().reset_index(drop=True)
    if len(dd) < 100:
        return {'error': '样本不足', 'n': int(len(dd))}
    dd['tu'] = (dd['type'] == 'U').astype(float)
    dd['tw'] = (dd['type'] == 'W').astype(float)
    dd['ax'] = dd['above'] * dd['r']
    xcols = ['above', 'r', 'ax', 'tu', 'tw']
    for j in range(2, poly + 1):
        dd['r%d' % j] = dd['r'] ** j
        dd['ax%d' % j] = dd['above'] * dd['r'] ** j
        xcols += ['r%d' % j, 'ax%d' % j]
    y = dd[outcome].astype(float).values
    keys = dd['code'].astype(str) + '_' + dd['year'].astype(str)
    allv = pd.concat([pd.Series(y, name='y')] +
                     [dd[c].astype(float).rename(c) for c in xcols] +
                     [keys.rename('k')], axis=1)
    gm = allv.groupby('k').transform('mean')
    yd = (allv['y'] - gm['y']).values
    Xd = np.column_stack([np.ones(len(dd))] + [(allv[c] - gm[c]).values for c in xcols])
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    n, k = Xd.shape
    XtXi = np.linalg.pinv(Xd.T @ Xd)
    cl = dd['code'].values
    G = len(np.unique(cl))
    meat = np.zeros((k, k))
    for g in np.unique(cl):
        m = cl == g
        s = Xd[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1) * (n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    tau, s = beta[1], se[1]
    p = 2 * (1 - stats.t.cdf(abs(tau / s), G - 1))
    return {'tau_pp': round(float(tau) * 100, 3), 'se_pp': round(float(s) * 100, 3),
            'p': round(float(p), 4), 'n': int(n),
            'ci95_pp': [round(float(tau - stats.t.ppf(0.975, G - 1) * s) * 100, 2),
                        round(float(tau + stats.t.ppf(0.975, G - 1) * s) * 100, 2)]}


def mccrary(r, bw=0.10, order=1):
    """McCrary 式局部线性密度检验：两侧 log 密度外推到断点，报比值与 t 值。"""
    d = r[(r >= -bw) & (r <= bw)]
    lo = d[d < 0]
    hi = d[d >= 0]
    if len(lo) < 50 or len(hi) < 50:
        return None
    BW = 0.01
    def dens(x):
        e = np.arange(-bw, bw + 1e-9, BW)
        c = (e[:-1] + e[1:]) / 2
        cnt, _ = np.histogram(x, bins=e)
        return c, cnt.astype(float) / (len(x) * BW)
    cl_, nl = dens(lo)
    ch_, nh = dens(hi)
    fl = cl_ < 0
    fh = ch_ >= 0
    Al = np.vstack([cl_[fl], np.ones(fl.sum())]).T
    bl, *_ = np.linalg.lstsq(Al, np.log(np.maximum(nl[fl], 1e-6)), rcond=None)
    Ah = np.vstack([ch_[fh], np.ones(fh.sum())]).T
    bh, *_ = np.linalg.lstsq(Ah, np.log(np.maximum(nh[fh], 1e-6)), rcond=None)
    pl = math.exp(bl[0] * 0 + bl[1])
    ph = math.exp(bh[0] * 0 + bh[1])
    # 自助标准误（按 country 重抽）
    return {'ratio_below_over_above': round(pl / ph, 4),
            'log_gap': round(math.log(pl / ph), 4),
            'dens_below': round(pl, 2), 'dens_above': round(ph, 2),
            'bw': bw, 'order': order}


def main():
    df = pd.read_csv(os.path.join(HERE, 'cn_matched.csv'))
    df['above'] = (df['r'] >= 0).astype(int)
    R = {}
    band = df[((np.exp(df['r']) - 1).abs() <= 0.20 + TOL)].copy()
    print('CN ±20%% 带: %s（下 %s / 上 %s）'
          % (format(len(band), ','), format(int((band.above == 0).sum()), ','),
             format(int((band.above == 1).sum()), ',')))

    # ---------- 1. 正规密度检验 ----------
    print('\n[1] McCrary 式局部线性密度检验（CN 估计价值）')
    dens = {}
    for bw in (0.05, 0.10, 0.15, 0.20):
        d = mccrary(band['r'].values, bw=bw)
        if d:
            dens['bw%d' % int(bw * 100)] = d
            print('  ±%d%%: 下/上密度比 %.4f (log gap %+.4f)，下 %.1f vs 上 %.1f'
                  % (int(bw * 100), d['ratio_below_over_above'], d['log_gap'],
                     d['dens_below'], d['dens_above']))
    R['mccrary'] = dens

    # 箱计数明细
    BW = 0.02
    bins = np.arange(-12, 10)
    cnt = pd.Series(np.floor(band['r'].values / BW).astype(int)).value_counts()
    n = np.array([cnt.get(k, 0) for k in bins], dtype=int)
    print('\n  箱计数（k=-1 是紧贴阈值下方，k=0 是紧贴上方）：')
    for k in range(-6, 5):
        print('    k=%+d: %8d' % (k, n[bins == k][0]))
    R['bin_counts'] = {str(int(k)): int(n[bins == k][0]) for k in bins}

    # 对称箱窗（各取 9 个满箱）
    L9 = n[(bins <= -1) & (bins >= -9)].sum()
    R9 = n[(bins >= 1) & (bins <= 9)].sum()
    print('\n  对称满箱比较（各 9 箱）: 下 %s vs 上 %s → 每箱 %.0f vs %.0f'
          % (format(int(L9), ','), format(int(R9), ','), L9 / 9, R9 / 9))

    # ---------- 2. 第一阶段：分时期 ----------
    print('\n[2] 第一阶段（投标期）分时期')
    fs = {}
    for lab, yrs in [('2013', (2013, 2013)), ('2014-2016', (2014, 2016)),
                     ('2017-2023', (2017, 2023)), ('all', (2013, 2023))]:
        d = band[(band.year >= yrs[0]) & (band.year <= yrs[1])]
        d = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(d, 'tender_period', poly=1)
        fs[lab] = r
        print('  %-10s: %+.2f 天 (SE %.2f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    R['first_stage_by_period'] = fs

    # ---------- 3. 结果：分时期 + 多批次 ----------
    print('\n[3] 单投标份额：分时期 / 单批次 vs 多批次')
    res = {}
    for lab, sub in [('all', band),
                     ('single_lot', band[band['lots'].fillna(1) <= 1]),
                     ('multi_lot', band[band['lots'].fillna(0) > 1]),
                     ('y2013_2016', band[band.year <= 2016]),
                     ('y2017_2023', band[band.year >= 2017])]:
        s = sub[((np.exp(sub['r']) - 1).abs() <= 0.20 + TOL)]
        r = rd(s, 'single', poly=1)
        res[lab] = r
        print('  %-12s: %+.2fpp (SE %.2f, p=%.4f, n=%s)'
              % (lab, r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1),
                 format(r.get('n', 0), ',')))
    R['single_splits'] = res

    # ---------- 4. 阈值以下发布率高的 country-year ----------
    print('\n[4] 只在阈值以下发布率高的 country-year（缓解选择性发布）')
    df['below'] = 1 - df['above']
    pub = df.groupby(['code', 'year']).agg(
        n=('below', 'size'), n_below=('below', 'sum')).reset_index()
    pub['below_share'] = pub['n_below'] / pub['n']
    med = pub['below_share'].median()
    hi_cy = pub[pub['below_share'] >= med][['code', 'year']]
    print('  全样本阈值以下公告占比中位数 %.3f；取不低于中位数的 country-year（%d 个）'
          % (med, len(hi_cy)))
    band_hi = band.merge(hi_cy.assign(keep=1), on=['code', 'year'], how='inner')
    r = rd(band_hi, 'single', poly=1)
    R['single_highpub_cy'] = r
    print('  单投标份额: %+.2fpp (SE %.2f, p=%.4f, n=%s)'
          % (r.get('tau_pp', 0), r.get('se_pp', 0), r.get('p', 1), format(r.get('n', 0), ',')))
    # 高发布率子样本的安慰剂
    prof = {}
    for c in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
        d = df.copy()
        d['thr_pl'] = np.exp(np.log(d['value_est']) - d['r']) * c
        d['r'] = np.log(d['value_est']) - np.log(d['thr_pl'])
        d['above'] = (d['value_est'] >= d['thr_pl']).astype(int)
        b = d[((np.exp(d['r']) - 1).abs() <= 0.20 + TOL)]
        b = b.merge(hi_cy.assign(keep=1), on=['code', 'year'], how='inner')
        rr = rd(b, 'single', poly=1)
        prof['%.2f' % c] = rr
        flag = ' <- SIG' if rr.get('p', 1) < 0.05 else ''
        print('    %.2fτ: %+.2fpp (p=%.4f, n=%s)%s'
              % (c, rr.get('tau_pp', 0), rr.get('p', 1), format(rr.get('n', 0), ','), flag))
    R['placebo_highpub'] = prof

    # ---------- 5. binscatter 数据 ----------
    bs = []
    for k in range(-15, 16):
        lo, hi = k * BW, (k + 1) * BW
        m = (band['r'] >= lo - 1e-12) & (band['r'] < hi)
        if m.sum() > 0:
            sub = band[m]
            bs.append({'k': k, 'ratio': round(float(np.exp((lo + hi) / 2)), 4),
                       'n': int(m.sum()),
                       'single': round(float(sub['single'].mean()), 5) if sub['single'].notna().any() else None,
                       'tender': round(float(sub['tender_period'].mean()), 2) if sub['tender_period'].notna().any() else None})
    R['binscatter'] = bs
    print('\n[5] binscatter（单投标份额%，投标期天）')
    for b in bs:
        if -6 <= b['k'] <= 5:
            print('  k=%+d ratio=%.3f n=%7d single=%s tender=%s'
                  % (b['k'], b['ratio'], b['n'],
                     '%.1f' % (b['single'] * 100) if b['single'] is not None else 'NA',
                     b['tender'] if b['tender'] is not None else 'NA'))

    json.dump(R, open(OUT, 'w'), indent=1)
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()
