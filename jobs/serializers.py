from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "description",
            "location",
            "job_type",
            "salary",
            "created_at",
        )
        read_only_fields = ("id", "created_at")