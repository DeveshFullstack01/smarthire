"""Forms for editing a candidate profile."""

from django import forms

from .profile_models import CandidateProfile


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile

        fields = [
            "headline",
            "bio",
            "phone",
            "location",
            "linkedin_url",
            "github_url",
            "portfolio_url",
        ]

        widgets = {
            "headline": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control"}),
            "github_url": forms.URLInput(attrs={"class": "form-control"}),
            "portfolio_url": forms.URLInput(attrs={"class": "form-control"}),
        }