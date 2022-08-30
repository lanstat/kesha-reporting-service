from rest_framework import serializers
from .models import Report
from .builder.report import Report as ReportBuilder
import shutil
import random
import string
from django.core.files.storage import default_storage
from django.conf import settings
from os.path import join
import os
from django.utils import timezone


class ReportSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    created = serializers.DateTimeField()


class ReportRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    file = serializers.FileField()

    def validate(self, attrs):
        file = attrs['file']
        filename = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10))
        default_storage.save('tmp/' + filename + '.zip', file)
        file_path = join(settings.BASE_DIR, 'tmp', filename + '_dec')
        shutil.unpack_archive(
            join(settings.BASE_DIR, 'tmp', filename + '.zip'), file_path)

        os.remove(join(settings.BASE_DIR, 'tmp', filename + '.zip'))
        if ReportBuilder.validate_config(file_path):
            attrs['file_path'] = file_path
        else:
            shutil.rmtree(file_path)
            raise serializers.ValidationError('invalid configuration file')
        return attrs

    def create(self, validated_data):
        record = Report()
        record.code = validated_data['code']
        record.save()
        shutil.move(validated_data['file_path'],
                    join(settings.BASE_DIR, 'media', record.code))

        return record

    def update(self, instance, validated_data):
        instance.updated = timezone.now()
        instance.save()
        shutil.rmtree(join(settings.BASE_DIR, 'media', instance.code))
        shutil.move(validated_data['file_path'],
                    join(settings.BASE_DIR, 'media', instance.code))

        return instance
