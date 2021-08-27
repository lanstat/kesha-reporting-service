from report.builder.report import Report
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Report as ReportModel
from .serializers import ReportSerializer
import shutil
from django.conf import settings
from os.path import join
import os
import zipfile
import io


def make_archive(source):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED,
                         False) as zip_file:
        for root, dirs, files in os.walk(source):
            for file in files:
                zip_file.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file),
                                    os.path.join(source)))
    return zip_buffer


@api_view(['GET'])
def download_report(request, pk):
    try:
        record = ReportModel.objects.get(code=pk)
    except:
        raise Http404
    report_path = join(settings.BASE_DIR, 'media', record.code)
    if not os.path.exists(report_path):
        raise Http404

    file = make_archive(report_path)
    http_response = HttpResponse(file.getvalue(),
                                 content_type='application/zip')
    http_response['Content-Disposition'] = 'filename="' + pk + '.zip"'
    return http_response


@api_view(['GET', 'POST'])
def generate_report(request, pk):
    try:
        record = ReportModel.objects.get(code=pk)
    except:
        raise Http404
    r = Report(record.code)
    params = request.GET.dict()
    r.set_parameters(params)
    file = r.generate()
    http_response = HttpResponse(file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename="' + pk + '.pdf"'
    return http_response


class ReportList(APIView):
    def get(self, request):
        reports = ReportModel.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetail(APIView):
    def get_object(self, pk):
        try:
            return ReportModel.objects.get(code=pk)
        except:
            raise Http404

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        shutil.rmtree(join(settings.BASE_DIR, 'media', report.code))
        return Response(status=status.HTTP_204_NO_CONTENT)
