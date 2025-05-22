from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter
from django.shortcuts import render


@method_decorator(csrf_exempt, name='dispatch')
def generate_invoice(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body)

    PAGE_WIDTH = A4[0]
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    # --- Top Info Table ---
    top_data = [
        ["Consignee", data["consignee"]],
        ["Company Number", data["company_number"]],
        ["Address", data["address"]],
        ["Corporation Tax Ref", data["corp_tax_ref"]],
        ["Date", data["date"]],
        ["Invoice No", data["invoice_no"]],
        ["Delivery", data["delivery"]],
        ["HS Code", data["hs_code"]],
        ["Payment Terms", data["payment_terms"]]
    ]
    top_col_widths = [130, 360]
    top_total_width = sum(top_col_widths)
    top_x = (PAGE_WIDTH - top_total_width) / 2

    top_table = Table(top_data, colWidths=top_col_widths)
    top_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey)
    ]))
    top_table.wrapOn(c, A4[0], A4[1])
    top_table.drawOn(c, top_x, 420)

    # --- Product Table ---
    product_data = [
        ["Description of Product", "Quantity", "Unit Price US$", "Amount US$"],
        [data["product_description"], data["quantity"], data["unit_price"], data["amount"]],
        [data["packing_note"], "", "", ""],
        ["", "", "Total Invoice Value US$", data["amount"]]
    ]
    product_col_widths = [200, 100, 120, 120]
    product_total_width = sum(product_col_widths)
    product_x = (PAGE_WIDTH - product_total_width) / 2

    product_table = Table(product_data, colWidths=product_col_widths, rowHeights=[25]*len(product_data))
    product_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("SPAN", (0, 3), (2, 3)),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold")
    ]))
    product_table.wrapOn(c, A4[0], A4[1])
    product_table.drawOn(c, product_x, 300)

    c.save()
    packet.seek(0)

    # Merge with template
    template_reader = PdfReader("template.pdf")
    overlay_pdf = PdfReader(packet)
    output = PdfWriter()

    template_page = template_reader.pages[0]
    template_page.merge_page(overlay_pdf.pages[0])
    output.add_page(template_page)

    final_output = BytesIO()
    output.write(final_output)
    final_output.seek(0)

    return FileResponse(final_output, as_attachment=True, filename="invoice.pdf")




def invoice_form_view(request):
    return render(request, "invoice_form.html")