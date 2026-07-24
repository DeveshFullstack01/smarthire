from django import forms

from .models import Interview


class InterviewForm(forms.ModelForm):

    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = Interview

        fields = [
            "interview_type",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "interviewer_name",
            "notes",
        ]

        widgets = {
            "interview_type": forms.Select(
                attrs={"class": "form-select"}
            ),
            "duration_minutes": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "meeting_link": forms.URLInput(
                attrs={"class": "form-control"}
            ),
            "interviewer_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }