"""用 matplotlib 重绘 5 张学术图（替代 pyecharts 版）

修复问题：pyecharts 默认 grid 边距导致内容仅占画布 28%，嵌入 Word 后充斥白边。
新方案：matplotlib + bbox_inches='tight'，内容充满画面；300 DPI；冷色学术配色；
Times New Roman；白底浅灰虚线网格。
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))          # economy/figures
ROOT = os.path.dirname(HERE)                                # economy/
FIGDIR = HERE
RESULTS = os.path.join(ROOT, 'materials', 'results')

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'axes.unicode_minus': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#404040',
    'axes.linewidth': 0.8,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'savefig.dpi': 300,
})

BLUE = '#1F4E79'   # 深蓝
DARK = '#404040'   # 深灰（拟合线/标记）
GRAY = '#7F7F7F'   # 灰
LGRAY = '#D9D9D9'  # 浅灰网格

FIGDIR = HERE


def style_ax(ax, ygrid=True, xgrid=False):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if ygrid:
        ax.grid(axis='y', color=LGRAY, linestyle='--', linewidth=0.6, zorder=0)
    if xgrid:
        ax.grid(axis='x', color=LGRAY, linestyle='--', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


# ---------- Figure 1: RD binscatter + 局部线性拟合 ----------
# 第五轮修订：改用正确阈值口径（Section 7.4）；归档口径的数据见 rd_binscatter.json
bs = json.load(open(f'{FIGDIR}/rd_binscatter_v7.json'))
fl = json.load(open(f'{FIGDIR}/rd_fitlines_v7.json'))

fig, ax = plt.subplots(figsize=(7.0, 4.0))
style_ax(ax)
centers = np.array(bs['centers'])
share = np.array(bs['share']) * 100
ax.scatter(centers, share, s=22, color=BLUE, zorder=3, label='Bin means (0.02-width bins)')
ax.plot(fl['left']['x'], np.array(fl['left']['y']) * 100, color=DARK, lw=1.8, zorder=4,
        label='Local linear fit below threshold (solid)')
ax.plot(fl['right']['x'], np.array(fl['right']['y']) * 100, color=DARK, lw=1.8, ls='--', zorder=4,
        label='Local linear fit above threshold (dashed)')
ax.axvline(0, color='#333333', lw=1.2, ls='-', zorder=2)
ax.annotate('Legal threshold', xy=(0, ax.get_ylim()[1]), xytext=(4, -2),
            textcoords='offset points', fontsize=8.5, color='#333333', va='top')
ax.set_xlabel('Log distance to procurement threshold (log estimated value − log threshold)')
ax.set_ylabel('Single-offer share (%)')
ax.set_title('Competition at the Legal Threshold (v7.0: pre-award estimate)', fontweight='bold')
ax.legend(frameon=False, loc='lower right')
fig.savefig(f'{FIGDIR}/fig1_rd_plot.png', bbox_inches='tight', pad_inches=0.06)
plt.close(fig)
print('fig1 ok (v7.0 estimate running variable)')

# ---------- Figure 2: forest plot ----------
# v3.0 用设计原生推断（IF multiplier bootstrap，国家聚类）[-0.32, +7.14]；
# 归档的 [-3.69, +7.12] 是 8 个 cell ATT 的 2.5–97.5 分位区间，不是抽样 CI。
V7 = json.load(open(f'{FIGDIR}/fig2_estimates_v7.json'))
designs = [
    ('v7.0 threshold RD\n(legal estimate, n=179,065)', V7['v7_single']['tau_pp'],
     V7['v7_single']['ci95_pp'][0], V7['v7_single']['ci95_pp'][1]),
    ('v7.0 threshold RD\n(foreign-winner share)', V7['v7_foreign_win']['tau_pp'],
     V7['v7_foreign_win']['ci95_pp'][0], V7['v7_foreign_win']['ci95_pp'][1]),
    ('v4.0 transposition TWFE\n(1.30M contracts)', 1.39, -0.62, 3.40),
    ('v3.0 transposition ATT\n(252 country-year cells)', 3.37, -0.32, 7.14),
]
fig, ax = plt.subplots(figsize=(7.0, 3.0))
style_ax(ax, ygrid=False, xgrid=True)
ys = np.arange(len(designs))[::-1]
for y, (name, est, lo, hi) in zip(ys, designs):
    ax.plot([lo, hi], [y, y], color=BLUE, lw=2.2, solid_capstyle='butt', zorder=3)
    ax.plot([lo, lo], [y - 0.08, y + 0.08], color=BLUE, lw=2.2, zorder=3)
    ax.plot([hi, hi], [y - 0.08, y + 0.08], color=BLUE, lw=2.2, zorder=3)
    ax.scatter([est], [y], s=55, color=DARK, zorder=4)
    ax.annotate(f'{est:+.2f} [{lo:+.2f}, {hi:+.2f}]', xy=(est, y), xytext=(0, 10),
                textcoords='offset points', ha='center', fontsize=8.5, color='#333333')
ax.axvline(0, color=GRAY, lw=1.0, ls='--', zorder=2)
ax.annotate('Null (no effect)', xy=(0, -0.42), xytext=(3, 0), textcoords='offset points',
            fontsize=8.5, color=GRAY)
ax.set_yticks(ys)
ax.set_yticklabels([d[0] for d in designs])
ax.set_xlabel('Effect on competition measure (percentage points), 95% CI')
ax.set_title('Primary Estimates and 95% Intervals: No Competitive Gain', fontweight='bold')
ax.set_ylim(-0.6, len(designs) - 0.3)
fig.savefig(f'{FIGDIR}/fig2_triple_convergence.png', bbox_inches='tight', pad_inches=0.06)
plt.close(fig)
print('fig2 ok (v7.0 main design)')

# ---------- Figure 3: 断点处合同密度（density audit） ----------
# 第五轮修订：改用正确阈值口径（Section 7.4）；归档口径见 density.json
dn = json.load(open(f'{FIGDIR}/density_v7.json'))
fig, ax = plt.subplots(figsize=(7.0, 3.9))
style_ax(ax)
centers = np.array(dn['centers'])
counts = np.array(dn['counts'])
colors = [GRAY if c < 0 else BLUE for c in centers]
ax.bar(centers, counts, width=0.018, color=colors, zorder=3)
# bin 0（中心 +0.01）顶部 2,823 份为 r≈0 处报告惯例堆点（21.7% 德国、10.7% award=est）
MP = 2823
i0 = int(np.where(np.isclose(centers, 0.01))[0][0])
ax.bar([centers[i0]], [counts[i0] - MP], width=0.018, color=BLUE, zorder=3)
ax.bar([centers[i0]], [MP], bottom=[counts[i0] - MP], width=0.018,
       color='#C00000', hatch='///', edgecolor='white', linewidth=0.3, zorder=4)
ax.axvline(0, color='#333333', lw=1.2, zorder=4)
ax.set_ylim(0, 27500)
ax.annotate('Legal threshold', xy=(0, 27500), xytext=(4, -3),
            textcoords='offset points', fontsize=8.5, color='#333333', va='top')
ax.annotate('Mass point at the line: 2,823 notices report\nestimates within 0.01% of the threshold; 21.7%\nGerman, 10.7% award = estimate (3.4% overall)',
            xy=(0.013, counts[i0] + 300), xytext=(0.062, 25200),
            fontsize=8, color='#C00000', va='top',
            arrowprops=dict(arrowstyle='->', color='#C00000', lw=0.9))
ax.set_xlabel('Log distance to threshold (log estimate − log threshold)')
ax.set_ylabel('Contracts per bin')
ax.set_title('Notice Density at the Threshold (v7.0: pre-award estimate)', fontweight='bold')
from matplotlib.patches import Patch
# 图例口径：下方 = bin <= -1（12 箱），上方 = bin >= 0（10 箱，含紧贴阈值上方的 bin 0）。
# 冻结密度检验只用 bin >= 1 的 9 箱作右侧，bin 0 被两侧同时排除——这正是 7.1 审计的构造不对称。
ax.legend(handles=[Patch(color=GRAY, label='Below the line, bins \u2264 \u22121 (154,406 contracts)'),
                   Patch(color=BLUE, label='Above the line, bins \u2265 0 (185,230 contracts)'),
                   Patch(facecolor='#C00000', hatch='///', edgecolor='white',
                         label='Mass point at the line (2,823)')],
          frameon=False, loc='upper left', fontsize=8)
fig.savefig(f'{FIGDIR}/fig4_density.png', bbox_inches='tight', pad_inches=0.06)
plt.close(fig)
print('fig3 ok (v7.0 density)')

# ---------- Figure 4: 敏感性（带宽 × 多项式阶数） ----------
# 第五轮修订：改用正确阈值口径（Section 7.4）
res = json.load(open(f'{FIGDIR}/fig4_grid_v7.json'))
bw = res['bandwidth']
poly = res['poly']
bw_keys = sorted(bw.keys(), key=float)
bw_est = [bw[k]['tau_pp'] for k in bw_keys]
bw_p = [bw[k]['p'] for k in bw_keys]
poly_keys = sorted(poly.keys(), key=int)
poly_est = [poly[k]['tau_pp'] for k in poly_keys]
poly_p = [poly[k]['p'] for k in poly_keys]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0))
for ax in (ax1, ax2):
    style_ax(ax, ygrid=False, xgrid=True)
    ax.axvline(0, color=GRAY, lw=1.0, ls='--', zorder=2)

ax1.plot(bw_est, range(len(bw_keys)), 'o-', color=BLUE, lw=1.6, ms=6, zorder=3)
for i, (e, p) in enumerate(zip(bw_est, bw_p)):
    ax1.annotate(f'{e:+.2f} (p={p:.2f})', xy=(e, i), xytext=(0, 9),
                 textcoords='offset points', ha='center', fontsize=8, color='#333333')
ax1.set_yticks(range(len(bw_keys)))
ax1.set_yticklabels([f'±{int(float(k) * 100)}%' for k in bw_keys])
ax1.set_ylabel('Bandwidth')
ax1.set_xlabel('Estimate (pp)')
ax1.set_title('Bandwidth', fontsize=10)

ax2.plot(poly_est, range(len(poly_keys)), 'o-', color=BLUE, lw=1.6, ms=6, zorder=3)
for i, (e, p) in enumerate(zip(poly_est, poly_p)):
    ax2.annotate(f'{e:+.2f} (p={p:.2f})', xy=(e, i), xytext=(0, 9),
                 textcoords='offset points', ha='center', fontsize=8, color='#333333')
ax2.set_yticks(range(len(poly_keys)))
ax2.set_yticklabels([f'Order {k}' for k in poly_keys])
ax2.set_ylabel('Polynomial order')
ax2.set_xlabel('Estimate (pp)')
ax2.set_title('Polynomial order', fontsize=10)
ax1.invert_yaxis(); ax2.invert_yaxis()
fig.suptitle('Specification Grid: v7.0 Legal Running Variable', fontweight='bold', fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(f'{FIGDIR}/fig3_sensitivity.png', bbox_inches='tight', pad_inches=0.06)
plt.close(fig)
print('fig4 ok')

# ---------- Figure 5: SME 份额剂量反应 ----------
sd = json.load(open(f'{FIGDIR}/sme_dose.json'))
fig, ax = plt.subplots(figsize=(7.0, 3.6))
style_ax(ax)
mids = [d['mid'] for d in sd]
sme = [d['sme'] * 100 for d in sd]
x = np.arange(1, len(sd) + 1)
ax.bar(x, sme, width=0.62, color=BLUE, zorder=3)
for xi, v in zip(x, sme):
    ax.annotate(f'{v:.1f}%', xy=(xi, v), xytext=(0, 3), textcoords='offset points',
                ha='center', fontsize=8.5, color='#333333')
ax.set_xticks(x)
ax.set_xticklabels([f'D{i}' for i in x])
ax.set_xlabel('Electronic-offer share decile (D1 = lowest, D10 = highest; 1.30M contracts)')
ax.set_ylabel('SME share of tenders (%)')
ax.set_title('Participation Responds: SME Share by Electronic-Offer Decile', fontweight='bold')
ax.set_ylim(0, max(sme) * 1.15)
fig.savefig(f'{FIGDIR}/fig5_sme_dose.png', bbox_inches='tight', pad_inches=0.06)
plt.close(fig)
print('fig5 ok')
