from core.renderers import PDFRenderer, ZipRenderer
from report.builder.report import Report
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from django.http import HttpResponse, Http404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Report as ReportModel
from .serializers import ReportCreateSerializer, ReportSerializer, ReportUpdateSerializer
import shutil
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from os.path import join
import os
import zipfile
import io

REPORT_ID = openapi.Parameter('id',
                              openapi.IN_PATH,
                              'Report\'s UID',
                              type=openapi.TYPE_STRING)


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


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __get_object(self, pk):
        try:
            return ReportModel.objects.get(code=pk)
        except:
            raise Http404

    @swagger_auto_schema(responses={200: ReportSerializer(many=True)})
    def list(self, request):
        reports = ReportModel.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ReportCreateSerializer,
                         responses={201: ReportSerializer})
    @action(methods=['post'],
            detail=False,
            parser_classes=[MultiPartParser],
            url_path='upload')
    def create_record(self, request):
        """
        Store a new report configuration
        """
        serializer = ReportCreateSerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            return Response(ReportSerializer(record).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ReportUpdateSerializer,
                         manual_parameters=[REPORT_ID],
                         responses={200: ReportSerializer})
    @action(methods=['patch'],
            detail=True,
            parser_classes=[MultiPartParser],
            url_path='patch')
    def patch_record(self, request, pk):
        """
        Update a report configuration
        """
        report = None
        if pk is not None:
            report = self.__get_object(pk)
        serializer = ReportUpdateSerializer(report, data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            status_code = status.HTTP_200_OK
            return Response(ReportSerializer(record).data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(manual_parameters=[REPORT_ID],
                         responses={200: ReportSerializer})
    def retrieve(self, request, pk):
        report = self.__get_object(pk)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[REPORT_ID],
                         responses={204: 'success'})
    def destroy(self, request, pk=None):
        report = self.__get_object(pk)
        report.delete()
        shutil.rmtree(join(settings.BASE_DIR, 'media', report.code))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(method='get',
                         manual_parameters=[REPORT_ID],
                         responses={200: 'Report config'})
    @action(methods=['get'], detail=True, renderer_classes=[ZipRenderer])
    def download(self, request, pk):
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

    @swagger_auto_schema(methods=['get', 'post'],
                         manual_parameters=[REPORT_ID],
                         responses={200: 'Report generated with the params'})
    @action(methods=['get', 'post'],
            detail=True,
            renderer_classes=[PDFRenderer])
    def generate(self, request, pk):
        """
        Generate a report, it receives multiple params as query string
        """
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
