"""fig2/3 改 Bar 单色、fig4 双 series，去除全部 JsCode（pyecharts 2.0.3 转义缺陷）"""
s = open('make_figures.py', encoding='utf-8').read()

start = s.find("# ---------- Fig 2 & 3:")
end = s.find("# ---------- Fig 4:")
new = '''# ---------- Fig 2 & 3: Bar 横向条形（无 JsCode，类目轴标签）----------
r3 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v3.json')))
r4 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v4.json')))
r6 = json.load(open(os.path.join(FIG, '..', 'materials', 'results', 'results_v6.json')))
v3e = r3['att']['share_single_offer']['post_att']
v3ci = [r3['att']['share_single_offer']['ci']['ci_lo'], r3['att']['share_single_offer']['ci']['ci_hi']]
v4e = r4['main']['share_single_offer']['treated_post']['beta']
v4ci = r4['main']['share_single_offer']['treated_post']['ci']
v6e = r6['main']['single']['tau']
v6ci = r6['main']['single']['ci']
print('  CI:', {'v3': [round(v3e,4), v3ci], 'v4': [round(v4e,4), v4ci], 'v6': [round(v6e,4), v6ci]})

fig2 = Bar()
fig2.add_xaxis(['v6.0 RD (326,718 contracts)', 'v4.0 TWFE (1.30M contracts)',
                'v3.0 ATT (national timing)'])
fig2.add_yaxis('Estimate (pp)', [round(v6e * 100, 2), round(v4e * 100, 2), round(v3e * 100, 2)],
               bar_width='55%',
               itemstyle_opts=opts.ItemStyleOpts(color=RED),
               label_opts=opts.LabelOpts(is_show=True, position='right',
                   font_family=FONT, font_size=11, color=DARK))
fig2.set_global_opts(
    title_opts=base_title('Triple Convergence: Three Designs, One Null',
                     'Effect on single-offer share (pp) | 95% CI: v3.0 [-3.7, +7.1], '
                     'v4.0 [-0.6, +3.4], v6.0 [-0.6, +2.2] - all span zero'),
    xaxis_opts=opts.AxisOpts(type_='category',
        axislabel_opts=opts.LabelOpts(font_family=FONT, font_size=10, color=DARK)),
    yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig2.set_series_opts(markline_opts=opts.MarkLineOpts(
    data=[opts.MarkLineItem(y=0)],
    symbol='none',
    linestyle_opts=opts.LineStyleOpts(color=DARK, type_='dashed', width=1.5)))
fig2.render(os.path.join(FIG, 'fig2_triple_convergence.html'))
print('fig2 已生成')

specs = [
    ('±10% bw, linear', -0.0023), ('±15% bw, linear', 0.0035),
    ('±20% bw, linear (main)', 0.0082), ('±25% bw, linear', 0.0094),
    ('±20% bw, quadratic', -0.0061),
]
fig3 = Bar()
fig3.add_xaxis([x[0] for x in specs])
fig3.add_yaxis('Estimate (pp)', [round(x[1] * 100, 2) for x in specs],
               bar_width='60%',
               itemstyle_opts=opts.ItemStyleOpts(color=BLUE),
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
    data=[opts.MarkLineItem(y=0)],
    symbol='none',
    linestyle_opts=opts.LineStyleOpts(color=DARK, type_='dashed', width=1.5)))
fig3.render(os.path.join(FIG, 'fig3_sensitivity.html'))
print('fig3 已生成')

'''
s = s[:start] + new + s[end:]

start = s.find("# ---------- Fig 4: 密度检验 ----------")
end = s.find("# ---------- Fig 5:")
new4 = '''# ---------- Fig 4: 密度检验（双 series 区分阈值两侧）----------
below_c = [c for c in centers if c < 0]
below_n = [n for c, n in zip(centers, counts) if c < 0]
above_c = [c for c in centers if c >= 0]
above_n = [n for c, n in zip(centers, counts) if c >= 0]

fig4 = Bar()
fig4.add_xaxis([round(c, 3) for c in below_c])
fig4.add_yaxis('Below threshold', below_n, bar_width='88%',
               itemstyle_opts=opts.ItemStyleOpts(color=BLUE),
               label_opts=opts.LabelOpts(is_show=False),
               stack='density', gap='-100%')
fig4.add_xaxis([round(c, 3) for c in above_c])
fig4.add_yaxis('Above threshold', above_n, bar_width='88%',
               itemstyle_opts=opts.ItemStyleOpts(color=NAVY),
               label_opts=opts.LabelOpts(is_show=False),
               stack='density')
fig4.set_global_opts(
    title_opts=base_title('Contract Density at the Threshold',
                     'Histogram by distance to threshold - 1.6% excess density below '
                     '(binomial p < 0.0001)'),
    xaxis_opts=base_axis('category'),
    yaxis_opts=base_axis(),
    tooltip_opts=opts.TooltipOpts(is_show=False),
    legend_opts=opts.LegendOpts(is_show=False))
fig4.set_series_opts(markline_opts=opts.MarkLineOpts(
    data=[opts.MarkLineItem(x=0)],
    symbol='none',
    linestyle_opts=opts.LineStyleOpts(color=DARK, type_='dashed', width=1.5)))
fig4.render(os.path.join(FIG, 'fig4_density.html'))
print('fig4 已生成')

'''
s = s[:start] + new4 + s[end:]
open('make_figures.py', 'w', encoding='utf-8').write(s)
print('已去除全部 JsCode')
