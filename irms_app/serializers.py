from rest_framework import serializers
from .models import *

class LocaltoPIDDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = PIDData
        fields = "__all__"
        read_only_fields = ('created_at',)
        