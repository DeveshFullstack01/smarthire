from django import forms
from django.utils import timezone

from .models import Offer


class OfferForm(forms.ModelForm):

    joining_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )

    expiry_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = Offer

        fields = [
            "designation",
            "employment_type",
            "work_location",
            "offered_salary",
            "joining_bonus",
            "joining_date",
            "expiry_date",
            "offer_letter",
            "recruiter_note",
        ]

        widgets = {

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Senior Java Backend Developer",
                }
            ),

            "employment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "work_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bangalore, India",
                }
            ),

            "offered_salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1800000",
                    "step": "0.01",
                }
            ),

            "joining_bonus": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "200000",
                    "step": "0.01",
                }
            ),

            "offer_letter": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),

            "recruiter_note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Congratulations! We are pleased to offer you..."
                    ),
                }
            ),
        }

        labels = {
            "designation": "Designation",
            "employment_type": "Employment Type",
            "work_location": "Work Location",
            "offered_salary": "Annual CTC",
            "joining_bonus": "Joining Bonus",
            "joining_date": "Joining Date",
            "expiry_date": "Offer Expiry Date",
            "offer_letter": "Offer Letter (PDF)",
            "recruiter_note": "Recruiter Message",
        }

    def clean_joining_date(self):

        joining_date = self.cleaned_data["joining_date"]

        if joining_date < timezone.now().date():
            raise forms.ValidationError(
                "Joining date cannot be in the past."
            )

        return joining_date

    def clean_expiry_date(self):

        expiry_date = self.cleaned_data["expiry_date"]

        if expiry_date < timezone.now().date():
            raise forms.ValidationError(
                "Offer expiry date cannot be in the past."
            )

        return expiry_date

    def clean_offer_letter(self):

        offer_letter = self.cleaned_data.get("offer_letter")

        if offer_letter:

            if not offer_letter.name.lower().endswith(".pdf"):
                raise forms.ValidationError(
                    "Only PDF offer letters are allowed."
                )

            if offer_letter.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Offer letter cannot exceed 5 MB."
                )

        return offer_letter

    def clean(self):

        cleaned_data = super().clean()

        joining_date = cleaned_data.get("joining_date")
        expiry_date = cleaned_data.get("expiry_date")

        if (
            joining_date
            and expiry_date
            and expiry_date >= joining_date
        ):
            self.add_error(
                "expiry_date",
                "Offer expiry must be before the joining date."
            )

        return cleaned_data