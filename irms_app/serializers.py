from rest_framework import serializers
from .models import *

class PIDDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PIDData
        fields = "__all__"
        read_only_fields = ('created_at',)

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiogasPlantReport
        fields = "__all__"
        read_only_fields = ('date', )