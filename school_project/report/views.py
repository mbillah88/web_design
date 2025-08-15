# report/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def generate_result_pdf(request):
    html_string = render_to_string('report/result_pdf.html', {'student': request.user.student})
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="result.pdf"'
    return response
