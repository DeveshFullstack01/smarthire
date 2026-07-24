import logging

from rest_framework import generics, permissions

from accounts.permissions import IsRecruiter

from .models import Job
from .serializers import JobSerializer

logger = logging.getLogger(__name__)


class JobCreateView(generics.CreateAPIView):
    """API endpoint for recruiters to create jobs."""

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRecruiter,
    ]

    def perform_create(self, serializer):
        logger.info(
            "Job creation requested by recruiter_id=%s",
            self.request.user.id,
        )

        company = self.request.user.companies.first()

        if company is None:
            logger.warning(
                "Recruiter has no associated company. recruiter_id=%s",
                self.request.user.id,
            )

        job = serializer.save(company=company)

        logger.info(
            "Job created successfully. job_id=%s recruiter_id=%s",
            job.id,
            self.request.user.id,
        )