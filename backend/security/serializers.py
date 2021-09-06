from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, max_length=50)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])

        return user

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        if len(validated_data['password']):
            instance.set_password(validated_data['password'])
        instance.save()

        return instance
