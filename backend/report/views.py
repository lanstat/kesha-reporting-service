from django.shortcuts import render
from report.builder.report import Report

def index(request):
    context = {}
    return render(request, 'index.html', context)

def generate_report(request):
    r = Report('tmp')
    return r.generate('javier')
