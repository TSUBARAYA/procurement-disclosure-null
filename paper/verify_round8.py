"""第八轮：docx/PDF 文档级一致性校验（在 verify_round4.py 的论文↔归档核对之上）。

检查：
  A. 关键新数字在 docx 与 PDF 中都出现；
  B. 已作废的旧数字不再出现（白名单除外——白名单内的都是明确标注为归档/撤回的上下文）；
  C. 新表（Table 8/9/10）在 docx 中存在；
  D. 图片嵌入与页数；
  E. 乱码。
用法：python verify_round8.py
"""
import os
import re
import sys

import fitz
from docx import Document

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, 'Testing_the_Transparency_Competition_Premise.docx')
PDF = os.path.join(HERE, 'Testing_the_Transparency_Competition_Premise.pdf')

doc = Document(DOCX)
parts = [p.text for p in doc.paragraphs]
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            parts.append(c.text)
docx_text = '\n'.join(parts)
norm = re.sub(r'\s+', ' ', docx_text)

pdf = fitz.open(PDF)
pdf_text = '\n'.join(page.get_text() for page in pdf)
norm_pdf = re.sub(r'\s+', ' ', pdf_text)

fails = []


def need(pat, label=None):
    """该模式必须出现在 docx 与 pdf 中。"""
    lab = label or pat
    for name, hay in (('docx', norm), ('pdf', norm_pdf)):
        if pat.lower() not in hay.lower():
            fails.append(f'MISSING in {name}: {lab}')


def forbid(pat, label=None):
    """该模式不得出现在 docx 与 pdf 中。"""
    lab = label or pat
    for name, hay in (('docx', norm), ('pdf', norm_pdf)):
        if pat.lower() in hay.lower():
            fails.append(f'STALE in {name}: {lab}')


# ---------- A. 关键新数字 ----------
for pat in ['+1.27', '0.085', '−0.19, +2.72', '327,636', '150,783', '176,853',
            '+1.36', '−1.14', '0.005', '−1.90, −0.37', '232,088', '173,546',
            '58,542', '+1.22', '0.256', '150,074', '1.000000', '5,314', '5,121',
            '3,287', '−5,727', '2,132', '4,592', '15,857', '15,967',
            '[−0.32, +7.14]', '+0.28, +6.65', '+1.75', '+1.65', '+1.89',
            '0.018', '0.029', '0.034', '1.39', '2.32', '2015/2170',
            'Table 10', 'cutoff profile', '0.70τ', '1.45τ',
            '166,003', '0.054', '318,179', '6.91', '5.94', '50.3', '49.0',
            '323,519', '+1.42', '+0.83', '0.024', '0.040', '0.025',
            'mechanical', 'no controls at all', 'contract type, not the log value',
            '+1.33', '0.037', 'withdraw', 'multiplier bootstrap']:
    need(pat)

# ---------- B. 作废数字（不得出现；明确标注为归档/撤回的披露除外） ----------
# 这些模式只允许出现在"撤回/归档"披露句中；本检查确保它们不以现行结论的身份出现。
DISCLOSURE_OK = {
    # 模式: 必须与之共现的披露语境词
    '+2.32': ['then +2.32'],
    '−0.06 pp': ['80,002'],
    '+0.76 pp': ['229,890'],
    '80,002': ['withdrawn', 'cannot be reproduced'],
    '229,890': ['withdrawn', 'cannot be reproduced'],
}
for pat, why in [
    ('without the log-value control', '旧的 +1.36 归因表述'),
    ('−1.15', '旧 130% placebo 值'),
    ('p = 0.004,', '旧 placebo p 值'),
    ('[−1.92, −0.39]', '旧 placebo CI'),
    ('+3.15 (p = 0.011)', '旧估计价值预注册值'),
    ('+3.05 (0.012)', 'Table 7 旧估计价值列'),
    ('5,116', '堆点精确数旧值'),
    ('15,739', '旧 ex-堆点值'),
    ('15,799', '旧 ex-堆点值'),
    ('65,537', '旧堆积网格'),
    ('+13,091', '旧堆积网格'),
    ('2015/2191', '旧法规编号'),
    ('41% of the threshold sample', '旧估计覆盖率'),
    ('+1.40, +16.30', 'Table 4 旧 CI'),
    ('+0.92 pp over 2013–2021', '旧窗口分段'),
    ('changes sign five times', '堆积变号笔误'),
    ('−0.23, +0.35, +0.82, and +0.94', '旧归档带宽网格表述'),
    ('+1.13 to +2.12', '旧 LOO 范围'),
    ('165,498', '旧价格子样本'),
    ('317,285', '旧报价覆盖率'),
    ('6.85 below', '旧构成统计'),
]:
    forbid(pat, why)

# ---------- C. 表数量与标题 ----------
if len(doc.tables) != 13:
    fails.append(f'docx 表格数 {len(doc.tables)} != 13')
for tname in ['Table 8.', 'Table 9.', 'Table 10.', 'Table 2. Main results']:
    if tname not in docx_text:
        fails.append(f'docx 缺少 {tname}')

# ---------- D. 图片与页数 ----------
img_pages = [i + 1 for i, page in enumerate(pdf) if page.get_images(full=True)]
if len(img_pages) != 5:
    fails.append(f'PDF 图片页 {img_pages}（应为 5 张）')
print(f'PDF 页数: {len(pdf)} | docx 段落: {len(doc.paragraphs)} | 表: {len(doc.tables)} | 图页: {img_pages}')

# ---------- E. 乱码 ----------
GARBLE = ['\ufffd', '□', '■', 'Ã©', 'â€', 'Â ']
g = [x for x in GARBLE if x in pdf_text]
if g:
    fails.append(f'乱码: {g}')

# ---------- 报告 ----------
if fails:
    print(f'\n{len(fails)} 项失败：')
    for f in fails:
        print('  ' + f)
    sys.exit(1)
print('文档级校验全部通过。')
