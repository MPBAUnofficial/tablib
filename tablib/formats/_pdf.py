from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.pagesizes import A4

import tablib
from tablib.compat import BytesIO

title = 'pdf'
extensions = ('pdf', )

margin = 10

table_style = [
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.Whiter(colors.black, 0.1)]),
    ('FACE', (0, 0), (-1, -1), 'Helvetica'),
]

header_style = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.Whiter(colors.black, 0.6)),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'),
]

totals_style = [
    ('FACE', (0, -1), (-1, -1), 'Helvetica-Bold'),
]

title_style = ParagraphStyle(
    name='Title Style', fontName='Helvetica-Bold', fontSize=16
)

description_style = ParagraphStyle(
    name='Description Style', fontName='Helvetica-Bold', fontSize=10
)


def export_book(databook):
    max_width = 0
    pagesize = list(A4)
    elements = []

    for dataset in databook._datasets:
        data = []
        totals = None

        if dataset.headers is not None:
            new_header = [item if item is not None else '' for item in
                          dataset.headers]
            data.append(new_header)

        for row in dataset._data:
            new_row = [item if item is not None else '' for item in row]
            if row.has_tag('totals'):
                totals = row
            else:
                data.append(new_row)

        if totals is not None:
            data.append(totals)

        if not data:
            continue

        table = Table(data, hAlign='LEFT')

        style = table_style[:]
        if totals is not None:
            style += totals_style
        if dataset.headers:
            style += header_style

        table.setStyle(style)

        if dataset.title is not None:
            elements.append(Paragraph(dataset.title, title_style))
            elements.append(Spacer(1, 20))

        elements.append(table)
        elements.append(PageBreak())

        max_width = max(max_width, table.minWidth() + 2*margin + 2*dataset.width)

    if max_width > A4[0]:
        pagesize[0] = max_width

    stringbuf = BytesIO()
    doc = SimpleDocTemplate(stringbuf, pagesize=pagesize, leftMargin=margin,
                            topMargin=margin, rightMargin=margin,
                            bottomMargin=margin)
    doc.build(elements)
    return stringbuf.getvalue()


def export_set(dataset):
    book = tablib.Databook([dataset])
    return export_book(book)
