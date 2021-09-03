from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import FontSerializer
import os
from .models import Font
import subprocess


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_all_fonts(request):
    Font.objects.all().delete()
    result = subprocess.run(['fc-list'],
                            stdout=subprocess.PIPE).stdout
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


class FontList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = Font.objects.all()

        family = request.GET.get('family', None)
        if family is not None:
            records = records.filter(family__contains=family)

        serializer = FontSerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FontSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FontDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Font.objects.get(pk=pk)
        except:
            raise Http404

    def get(self, request, pk):
        record = self.get_object(pk)
        serializer = FontSerializer(record)
        return Response(serializer.data)

    def delete(self, request, pk):
        record = self.get_object(pk)
        source = record.source
        if '/.fonts/' in source:
            record.delete()
            os.remove(source)
            subprocess.run(['fc-cache'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            errors = {
                'detail': 'cannot delete a system font'
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
