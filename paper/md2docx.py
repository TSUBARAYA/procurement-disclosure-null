"""把论文 Markdown 转成学术格式 docx（TNR、两端对齐、表格、图片）

关键点：Markdown 源是硬换行的（每个逻辑段拆成多行），必须按空线分块、
块内行合并为一个段落，否则 docx 里全是单行段——单行段是段落末行，
两端对齐不拉伸末行，右边缘永远是锯齿状。
"""
import re, os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))          # economy/paper
ROOT = os.path.dirname(HERE)                                # economy/

SRC = os.path.join(HERE, 'transparency_and_competition.md')
DST = os.path.join(HERE, 'Testing_the_Transparency_Competition_Premise.docx')
FIGDIR = os.path.join(ROOT, 'figures')

doc = Document()

# 全局样式：TNR 小四（12pt）
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')


def set_tnr(run, size=12, bold=False, italic=False):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')


def add_heading(text, level):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True  # 防孤行标题落在页尾
    sizes = {1: 16, 2: 14, 3: 12.5}
    r = p.add_run(text)
    set_tnr(r, sizes.get(level, 12), True)
    return p


def emit_para(text):
    """普通正文段：两端对齐 + 首行缩进 + 1.5 倍行距，处理链接/粗体/斜体"""
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = text.replace('`', '')
    text = re.sub(r'[ \t]{2,}', ' ', text)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Pt(24)
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            r = p.add_run(part[2:-2]); set_tnr(r, 12, True)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            r = p.add_run(part[1:-1]); set_tnr(r, 12, italic=True)
        elif part:
            r = p.add_run(part.replace('*', '')); set_tnr(r, 12)
    return p


def emit_cell_runs(p, text, size, base_bold=False):
    """表格单元格：解析 **bold** / *italic*（与 emit_para 同规则），base_bold 供表头用。"""
    text = text.replace('`', '')
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            r = p.add_run(part[2:-2]); set_tnr(r, size, True)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            r = p.add_run(part[1:-1]); set_tnr(r, size, italic=True)
        elif part:
            r = p.add_run(part.replace('*', '')); set_tnr(r, size, bold=base_bold)


def add_table(rows, widths=None):
    """rows: list of list of str；widths: 可选列宽（英寸），逐列设置避免窄表被均分压碎"""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    n_cols = len(rows[0])
    t = doc.add_table(rows=len(rows), cols=n_cols)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for ci, w in enumerate(widths):
            for cell in t.columns[ci].cells:
                cell.width = Inches(w)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit')
        trPr.append(cant)
        if ri == 0:
            th = OxmlElement('w:tblHeader')
            trPr.append(th)
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            c = t.cell(ri, ci)
            c.text = ''
            p = c.paragraphs[0]
            emit_cell_runs(p, cell, 10.5, base_bold=(ri == 0))
            # 整表防跨页拆行：除最后一行外全部 keep_with_next，
            # 配合题注的 keep_with_next，题注+表格保持在同一页
            if ri < len(rows) - 1:
                p.paragraph_format.keep_with_next = True
    doc.add_paragraph()  # 表后间距
    return t


def _flatten_png(path):
    """RGBA→RGB 扁平化：部分 docx→PDF 转换器对带 alpha 通道的 PNG 会丢图，
    贴到白底另存为 RGB 再嵌入。返回可直接嵌入的路径。"""
    try:
        from PIL import Image
        im = Image.open(path)
        if im.mode in ('RGBA', 'LA', 'PA'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            rgba = im.convert('RGBA')
            bg.paste(rgba, mask=rgba.split()[-1])
            out = os.path.splitext(path)[0] + '_rgb.png'
            bg.save(out)
            return out
        return path
    except Exception:
        return path


def add_figure(png_name, caption):
    path = os.path.join(FIGDIR, png_name)
    if not os.path.exists(path):
        print(f'  ✗ 图缺失: {png_name}')
        return
    embed = _flatten_png(path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(embed, width=Inches(6.0))
    # 图片与题注保持同页
    p.paragraph_format.keep_with_next = True
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    set_tnr(r, 10.5, italic=True)


FIG_MAP = {
    1: 'fig1_rd_plot.png',
    2: 'fig2_triple_convergence.png',
    3: 'fig4_density.png',
    4: 'fig3_sensitivity.png',
    5: 'fig5_sme_dose.png',
}

# 表格列宽（英寸，总宽 6.5）：避免多列表被均分压碎成每格一词
TABLE_WIDTHS = {
    'Table 1': [1.0, 1.2, 1.2, 3.1],
    'Table 2': [1.45, 0.8, 0.55, 0.6, 1.15, 1.0, 0.95],
    'Table 3': [1.5, 1.45, 1.45, 0.85, 1.25],
    'Table 4': [1.6, 0.9, 0.7, 0.7, 1.6],
    'Table 5': [1.35, 0.95, 0.65, 0.65, 1.4, 0.9],
    'Table 6': [1.7, 0.95, 0.65, 0.65, 0.85, 1.7],
    'Table 7': [1.6, 0.72, 0.72, 0.65, 0.72, 0.68, 0.71, 0.7],
    'Table 8': [1.45, 0.8, 0.55, 0.6, 1.15, 1.0, 0.95],
    'Table 9': [1.5, 0.9, 0.65, 0.65, 1.4, 1.0],
    'Table 10': [0.75, 0.95, 1.25, 0.9, 0.55, 0.6, 1.3],
    'Table 11': [0.95, 0.85, 0.6, 0.85, 0.95, 0.85, 0.6],
    'Table 12': [1.75, 2.35, 1.05, 1.35],
    'Table 13': [1.45, 1.55, 0.65, 1.5, 1.35],
}

# ---------- 解析 Markdown：按空行分块，块内硬换行合并 ----------
raw = open(SRC, encoding='utf-8').read()
blocks = re.split(r'\n\s*\n', raw)

for block in blocks:
    lines = [l.rstrip() for l in block.split('\n') if l.strip()]
    if not lines:
        continue
    first = lines[0].strip()

    # 水平线
    if all(l.strip() == '---' for l in lines):
        continue

    # 图：题注块（题注自身可能跨多行）
    mfig = re.match(r'^\*\*Figure\s+(\d+)\.\*\*', first)
    if mfig:
        n = int(mfig.group(1))
        caption = ' '.join(l.strip() for l in lines).replace('**', '').replace('*', '').replace('`', '')
        png = FIG_MAP.get(n)
        if png:
            add_figure(png, caption)
        else:
            print(f'  ✗ 未映射的图: Figure {n}')
        continue

    # 标题
    mh = re.match(r'^(#{1,3})\s+(.*)', first)
    if mh:
        level = len(mh.group(1))
        text = mh.group(2).strip()
        if level == 1:
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text); set_tnr(r, 18, True)
            p.paragraph_format.space_after = Pt(18)
        else:
            add_heading(text, level)
        if len(lines) > 1:  # 防御：标题块若夹带正文行
            emit_para(' '.join(l.strip() for l in lines[1:]))
        continue

    # 表格（块前可能带题注行，题注与表格行之间可能无空行）
    if any(l.lstrip().startswith('|') for l in lines):
        j = 0
        while j < len(lines) and not lines[j].lstrip().startswith('|'):
            j += 1
        if j > 0:
            cap = emit_para(' '.join(l.strip() for l in lines[:j]))
            cap.paragraph_format.keep_with_next = True
        rows = []
        for l in lines[j:]:
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                continue
            rows.append(cells)
        if rows:
            cap_text = ' '.join(lines[:j])
            widths = None
            for key, w in TABLE_WIDTHS.items():
                if key + '.' in cap_text:
                    widths = w
                    break
            add_table(rows, widths=widths)
        continue

    # 普通正文段：块内所有硬换行合并为一段
    p = emit_para(' '.join(l.strip() for l in lines))
    # 独立成块的题注（**Table N.** / **Figure N.**）与后续表格保持同页
    if re.match(r'^\*\*(Table|Figure)\s+\d+', first):
        p.paragraph_format.keep_with_next = True

doc.save(DST)

# 文档元数据
from docx import Document as _D
_d = _D(DST)
_d.core_properties.title = ('Testing the Transparency-Competition Premise: '
                            'Evidence from EU Public Procurement')
_d.core_properties.subject = 'public procurement; e-procurement; transparency; regression discontinuity'
_d.core_properties.keywords = 'public procurement; e-procurement; transparency; RD; bunching; null result'
_d.save(DST)

print(f'已生成 {DST}')
print(f'  段落数: {len(doc.paragraphs)} | 表格数: {len(doc.tables)}')
