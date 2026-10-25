"""论文 5 张学术图表（pyecharts 2.x，学术配色）
已验证可渲染组合：Scatter+value轴+markline / Bar+类目轴 / Line+value轴。无 JsCode。
"""
import json, os
from pyecharts import options as opts
from pyecharts.charts import Scatter, Line, Bar

FIG = os.path.dirname(os.path.abspath(__file__))
NAVY = '#1F4E79'; BLUE = '#2E75B6'; RED = '#C00000'; GREY = '#7F7F7F'; DARK = '#262626'; LIGHT = '#D9D9D9'
FONT = 'Georgia, "Times New Roman", serif'


def base_title(text, sub=None):
    return opts.TitleOpts(
        title=text, subtitle=sub,
        title_textstyle_opts=opts.TextStyleOpts(font_family=FONT, font_size=15,
                                                font_weight='bolder', color=DARK),
        subtitle_textstyle_opts=opts.TextStyleOpts(font_family=FONT, font_size=11, color=GREY),
        pos_left='center', pos_top='top')


def base_axis(axis_type='value'):
    return opts.AxisOpts(
        type_=axis_type,
        axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=DARK)),
        axistick_opts=opts.AxisTickOpts(is_show=True),
        axislabel_opts=opts.LabelOpts(font_family=FONT, font_size=11, color=DARK),
        splitline_opts=opts.SplitLineOpts(is_show=True,
            linestyle_opts=opts.LineStyleOpts(color=LIGHT, width=0.5, type_='dashed')))


# ---------- Fig 1: RD 断点图 ----------
d = json.load(open(os.path.join(FIG, 'rd_binscatter.json')))
fit = json.load(open(os.path.join(FIG, 'rd_fitlines.json')))
centers, share, counts = d['centers'], d['share'], d['counts']
yl = [round(v * 100, 2) for v in fit['left']['y']]
yr = [round(v * 100, 2) for v in fit['right']['y']]

fig1 = Scatter()
fig1.add_xaxis([round(c, 3) for c in centers])
fig1.add_yaxis('Bin means', [round(s_ * 100, 2) for s_ in share],
               symbol_size=5, itemstyle_opts=opts.ItemStyleOpts(color=NAVY, opacity=0.75),
               label_opts=opts.LabelOpts(is_show=False))
fig1.set_global_opts(
    title_opts=base_title('Contract-Level Competition at the Legal Threshold',
                          'Single-offer share by distance to threshold (log scale) | '
                          '326,718 contracts | EU-28, 2013-2023'),
    xaxis_opts=base_axis(), yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig1.set_series_opts(markline_opts=opts.MarkLineOpts(
    symbol='none',
    data=[
        [opts.MarkLineItem(coord=[-0.15, yl[0]]), opts.MarkLineItem(coord=[0, yl[-1]])],
        [opts.MarkLineItem(coord=[0, yr[0]]), opts.MarkLineItem(coord=[0.15, yr[-1]])],
        opts.MarkLineItem(x=0),
    ],
    linestyle_opts=opts.LineStyleOpts(color=RED, width=2)))
fig1.render(os.path.join(FIG, 'fig1_rd_plot.html'))
print('fig1 OK')

# ---------- Fig 2: 三重收敛（Bar） ----------
r3 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v3.json')))
r4 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v4.json')))
r6 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v6.json')))
v3e = r3['att']['share_single_offer']['post_att']
# v3.0 区间：已重建的 cell-level t 区间（review4_v3_ci_reconstruction.json），
# 替代 archived results_v3.json 中 cell_ci 的经验分位区间 [−3.69, +7.12]
r3ci = json.load(open(os.path.join(FIG, '..', 'materials', 'results',
                                   'review4_v3_ci_reconstruction.json')))
v3ci = r3ci['single']['cell_t_ci95_pp']
v4e = r4['main']['share_single_offer']['treated_post']['beta']
v4ci = r4['main']['share_single_offer']['treated_post']['ci']
v6e = r6['main']['single']['tau']
v6ci = r6['main']['single']['ci']
print('  CI:', {'v3': [round(v3e, 4), v3ci], 'v4': [round(v4e, 4), v4ci], 'v6': [round(v6e, 4), v6ci]})

fig2 = Bar()
fig2.add_xaxis(['v6.0 RD (326,718 contracts)', 'v4.0 TWFE (1.30M contracts)',
                'v3.0 ATT (national timing)'])
fig2.add_yaxis('Estimate (pp)', [round(v6e * 100, 2), round(v4e * 100, 2), round(v3e * 100, 2)],
               bar_width='55%', itemstyle_opts=opts.ItemStyleOpts(color=RED),
               label_opts=opts.LabelOpts(is_show=True, position='right',
                                         font_family=FONT, font_size=11, color=DARK))
fig2.set_global_opts(
    title_opts=base_title('Triple Convergence: Three Designs, One Null',
                          f'Effect on single-offer share (pp) | 95% CI: v3.0 '
                          f'[{v3ci[0]:.1f}, {v3ci[1]:.1f}], v4.0 '
                          f'[{v4ci[0] * 100:.1f}, {v4ci[1] * 100:.1f}], v6.0 '
                          f'[{v6ci[0] * 100:.1f}, {v6ci[1] * 100:.1f}] - all span zero'),
    xaxis_opts=opts.AxisOpts(type_='category',
        axislabel_opts=opts.LabelOpts(font_family=FONT, font_size=10, color=DARK)),
    yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig2.set_series_opts(markline_opts=opts.MarkLineOpts(
    data=[opts.MarkLineItem(y=0)], symbol='none',
    linestyle_opts=opts.LineStyleOpts(color=DARK, type_='dashed', width=1.5)))
fig2.render(os.path.join(FIG, 'fig2_triple_convergence.html'))
print('fig2 OK')

# ---------- Fig 3: 规格敏感性（Bar） ----------
specs = [('±10% bw, linear', -0.0023), ('±15% bw, linear', 0.0035),
         ('±20% bw, linear (main)', 0.0082), ('±25% bw, linear', 0.0094),
         ('±20% bw, quadratic', -0.0061)]
fig3 = Bar()
fig3.add_xaxis([x[0] for x in specs])
fig3.add_yaxis('Estimate (pp)', [round(x[1] * 100, 2) for x in specs],
               bar_width='60%', itemstyle_opts=opts.ItemStyleOpts(color=BLUE),
               label_opts=opts.LabelOpts(is_show=True, position='right',
                                         font_family=FONT, font_size=11, color=DARK))
fig3.set_global_opts(
    title_opts=base_title('The Null Is Stable Across Specifications',
                          'Point estimates on single-offer share (pp) - every specification '
                          'has a confidence interval spanning zero'),
    xaxis_opts=opts.AxisOpts(type_='category',
        axislabel_opts=opts.LabelOpts(font_family=FONT, font_size=10, color=DARK, rotate=30)),
    yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig3.set_series_opts(markline_opts=opts.MarkLineOpts(
    data=[opts.MarkLineItem(y=0)], symbol='none',
    linestyle_opts=opts.LineStyleOpts(color=DARK, type_='dashed', width=1.5)))
fig3.render(os.path.join(FIG, 'fig3_sensitivity.html'))
print('fig3 OK')

# ---------- Fig 4: 密度检验（Bar + 字符串类目） ----------
fig4 = Bar()
fig4.add_xaxis([str(round(c, 3)) for c in centers])
fig4.add_yaxis('Contracts', counts, bar_width='88%',
               itemstyle_opts=opts.ItemStyleOpts(color=BLUE),
               label_opts=opts.LabelOpts(is_show=False))
fig4.set_global_opts(
    title_opts=base_title('Contract Density at the Threshold',
                          'Histogram by distance to threshold - 1.6% excess density below '
                          '(binomial p < 0.0001)'),
    xaxis_opts=base_axis('category'),
    yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig4.render(os.path.join(FIG, 'fig4_density.html'))
print('fig4 OK')

# ---------- Fig 5: SME 剂量反应（Line） ----------
dose = json.load(open(os.path.join(FIG, 'sme_dose.json')))
xs = [d_['mid'] for d_ in dose]
ys = [round(d_['sme'] * 100, 1) for d_ in dose]
fig5 = Line()
fig5.add_xaxis(xs)
fig5.add_yaxis('SME tender share (%)', ys, is_symbol_show=True, symbol_size=7,
               is_smooth=False,
               linestyle_opts=opts.LineStyleOpts(color=NAVY, width=2.5),
               itemstyle_opts=opts.ItemStyleOpts(color=NAVY),
               label_opts=opts.LabelOpts(is_show=False))
fig5.set_global_opts(
    title_opts=base_title('Participation Responds: The SME Channel',
                          'SME share of tenders by electronic-offer share (deciles, '
                          '1.30M contracts): 8.7% -> 54.6%'),
    xaxis_opts=base_axis(), yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False))
fig5.render(os.path.join(FIG, 'fig5_sme_dose.html'))
print('fig5 OK')
print('全部 5 张 HTML 已就绪')
