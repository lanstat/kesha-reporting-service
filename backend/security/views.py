from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .serializers import UserCreateSerializer, UserSerializer, UserStoreSerializer
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

USER_ID = openapi.Parameter('id',
                            openapi.IN_PATH,
                            'Username',
                            type=openapi.TYPE_STRING)


class UserViewset(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def list(self, request):
        """
        List all users registered
        """
        records = User.objects.all()
        serializer = UserSerializer(records, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserCreateSerializer,
                         responses={201: UserSerializer})
    def create(self, request):
        """
        Create an user
        """
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(UserSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_object(self, pk):
        try:
            record = User.objects.get(username=pk)
            record.username = pk
            return record
        except:
            raise Http404

    @swagger_auto_schema(manual_parameters=[USER_ID],
                         responses={200: UserSerializer})
    def retrieve(self, request, pk):
        """
        Get an user specified
        """
        record = self._get_object(pk)
        serializer = UserSerializer(record)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserStoreSerializer,
                         manual_parameters=[USER_ID],
                         responses={200: UserSerializer})
    def partial_update(self, request, pk):
        """
        Update a selected user
        """
        record = self._get_object(pk)
        serializer = UserStoreSerializer(record, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(UserSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(manual_parameters=[USER_ID],
                         responses={204: 'success'})
    def destroy(self, request, pk):
        """
        Delete a user
        """
        record = self._get_object(pk)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
