from rest_framework import generics, permissions
from .serializers import CandidateSignupSerializer, RecruiterSignupSerializer


class CandidateSignupView(generics.CreateAPIView):
    serializer_class = CandidateSignupSerializer
    permission_classes = [permissions.AllowAny]


class RecruiterSignupView(generics.CreateAPIView):
    serializer_class = RecruiterSignupSerializer
    permission_classes = [permissions.AllowAny]
