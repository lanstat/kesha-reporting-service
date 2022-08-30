from report.builder.report import Report
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Report as ReportModel
from .serializers import ReportRequestSerializer, ReportSerializer
import shutil
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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


@swagger_auto_schema(method='get',
                     manual_parameters=[
                         openapi.Parameter('id',
                                           openapi.IN_PATH,
                                           type=openapi.TYPE_STRING)
                     ],
                     responses={200: 'success'})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, pk):
    """
    Download the packet report specified
    """
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
@permission_classes([IsAuthenticated])
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: ReportSerializer(many=True)})
    def get(self, request):
        reports = ReportModel.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ReportRequestSerializer,
                         responses={200: ReportSerializer})
    @parser_classes([MultiPartParser])
    def post(self, request):
        """
        Store a new report configuration
        """
        serializer = ReportRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetail(APIView):
    permission_classes = [IsAuthenticated]

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
