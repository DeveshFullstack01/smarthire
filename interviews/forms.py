from django import forms
from django.utils import timezone

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
            "interview_round",
            "interview_type",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "interviewer_name",
            "notes",
        ]

        widgets = {
            "interview_round": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "interview_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 15,
                }
            ),

            "meeting_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "interviewer_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data["scheduled_at"]

        if scheduled_at <= timezone.now():
            raise forms.ValidationError(
                "Interview must be scheduled in the future."
            )

        return scheduled_at

    def clean_duration_minutes(self):
        duration = self.cleaned_data["duration_minutes"]

        if duration < 15:
            raise forms.ValidationError(
                "Minimum duration is 15 minutes."
            )

        if duration > 480:
            raise forms.ValidationError(
                "Maximum duration is 8 hours."
            )

        return duration

    def clean(self):
        cleaned_data = super().clean()

        interview_type = cleaned_data.get("interview_type")
        meeting_link = cleaned_data.get("meeting_link")

        if (
            interview_type == Interview.InterviewType.ONLINE
            and not meeting_link
        ):
            self.add_error(
                "meeting_link",
                "Meeting link is required for online interviews.",
            )

        return cleaned_data


class InterviewFeedbackForm(forms.ModelForm):
    """
    Recruiter fills this after the interview.
    """

    class Meta:
        model = Interview

        fields = [
            "technical_rating",
            "communication_rating",
            "problem_solving_rating",
            "recommendation",
            "feedback",
        ]

        widgets = {
            "technical_rating": forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={
                    "class": "form-select",
                },
            ),

            "communication_rating": forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={
                    "class": "form-select",
                },
            ),

            "problem_solving_rating": forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={
                    "class": "form-select",
                },
            ),

            "recommendation": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),

            "feedback": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write interview feedback...",
                },
            ),
        }

    def save(self, commit=True):
        interview = super().save(commit=False)

        ratings = [
            interview.technical_rating,
            interview.communication_rating,
            interview.problem_solving_rating,
        ]

        ratings = [r for r in ratings if r is not None]

        if ratings:
            interview.overall_rating = round(
                sum(ratings) / len(ratings),
                2,
            )

        if commit:
            interview.save()

        return interview