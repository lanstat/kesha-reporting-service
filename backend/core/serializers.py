from rest_framework import serializers
from .models import Font
import shutil
import random
import string
from django.core.files.storage import default_storage
from django.conf import settings
from os.path import join
import os
import subprocess
import re
from pathlib import Path


class FontSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    family = serializers.CharField()
    style = serializers.CharField()
    created = serializers.DateTimeField()


class FontStoreSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate(self, attrs):
        file = attrs['file']
        filename = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10))
        default_storage.save('tmp/' + filename + '.obj', file)
        file_path = join(settings.BASE_DIR, 'tmp', filename + '.obj')

        result = subprocess.run(['fc-query', file_path],
                                stdout=subprocess.PIPE).stdout
        font_name_re = re.compile(r'family\s*\:\s*\"(.*?)\"')
        font_name = font_name_re.findall(result.decode())

        if len(font_name) > 0:
            attrs['family'] = font_name[0]
            attrs['file_path'] = file_path
            style_re = re.compile(r'\s+style\s*\:\s*\"(.*?)\"')
            tmp = style_re.findall(result.decode())
            if len(tmp) > 0:
                attrs['style'] = tmp[0]
        else:
            os.remove(file_path)
            raise serializers.ValidationError('invalid font file')
        return attrs

    def create(self, validated_data):
        home = str(Path.home())
        old_path = validated_data['file_path']
        new_path = join(home, '.fonts')

        record = Font()
        record.family = validated_data['family']
        record.style = validated_data['style']
        record.source = join(new_path, old_path.split('/')[-1])

        shutil.move(old_path, new_path)
        subprocess.run(['fc-cache'])
        record.save()

        return record
