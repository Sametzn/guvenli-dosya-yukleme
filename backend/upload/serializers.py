from rest_framework import serializers
from .models import VirusLog

class VirusLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(source='created_at')

    class Meta:
        model = VirusLog
        fields = ['id', 'user', 'action', 'filename', 'sha256', 'detected', 'result_detail', 'timestamp']
