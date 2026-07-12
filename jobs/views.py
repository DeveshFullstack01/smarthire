from rest_framework import generics, permissions
from accounts.permissions import IsRecruiter
from .models import Job
from .serializers import JobSerializer


class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiter]

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(company=company)