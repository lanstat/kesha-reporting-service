from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.response import Response


class UserList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        records = User.objects.all()
        serializer = UserSerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return User.objects.get(username=pk)
        except:
            raise Http404

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = UserSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        record = self.get_object(pk)
        data = request.data.copy()
        data.update({'username': 'tmp'})
        serializer = UserSerializer(record, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = self.get_object(pk)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
