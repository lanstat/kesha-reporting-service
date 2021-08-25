from django.shortcuts import render
from report.builder.report import Report
from django.http import HttpResponse

def index(request):
    context = {}
    return render(request, 'index.html', context)

def generate_report(request):
    r = Report('tmp')
    r.set_parameters(request.GET.dict())
    file = r.generate()
    http_response = HttpResponse(file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename="javier.pdf"'
    return http_response
