from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import FontSerializer, FontStoreSerializer
import os
from .models import Font
import subprocess

FONT_ID = openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)


class FontViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: FontSerializer(many=True)})
    def list(self, request):
        """
        Return a list of all registered fonts
        """
        records = Font.objects.all()

        family = request.GET.get('family', None)
        if family is not None:
            records = records.filter(family__contains=family)

        serializer = FontSerializer(records, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=FontStoreSerializer,
                         responses={200: FontSerializer})
    @action(methods=['post'],
            detail=False,
            parser_classes=[MultiPartParser],
            url_path='upload')
    def upload(self, request):
        """
        Store a new font
        """
        serializer = FontSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_object(self, pk):
        try:
            return Font.objects.get(pk=pk)
        except:
            raise Http404

    @swagger_auto_schema(manual_parameters=[FONT_ID],
                         responses={200: FontSerializer})
    def retrieve(self, request, pk):
        """
        Get a specific font information
        """
        record = self._get_object(pk)
        serializer = FontSerializer(record)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[FONT_ID],
                         responses={204: 'Success'})
    def destroy(self, request, pk):
        """
        Delete a specific font
        """
        record = self._get_object(pk)
        source = record.source
        if '/.fonts/' in source:
            record.delete()
            os.remove(source)
            subprocess.run(['fc-cache'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            errors = {'detail': 'cannot delete a system font'}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='post', responses={204: 'success'})
    @action(methods=['post'], detail=False, url_path='scan')
    def scan_all_fonts(self, request):
        """
        Scan and register all fonts installed in the system
        """
        Font.objects.all().delete()
        result = subprocess.run(['fc-list'], stdout=subprocess.PIPE).stdout
        lines = result.decode()
        lines = lines.strip().split('\n')
        records = []
        for line in lines:
            parts = line.split(':')
            record = Font()
            record.family = parts[1].strip()
            record.source = parts[0].strip()
            if len(parts) > 2:
                record.style = parts[2].strip().replace('style=', '')
            records.append(record)

        Font.objects.bulk_create(records)
        return Response(status=status.HTTP_204_NO_CONTENT)
