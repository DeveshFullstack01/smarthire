from django import forms

from .models import EmployeeOnboarding


class EmployeeOnboardingForm(forms.ModelForm):

    class Meta:
        model = EmployeeOnboarding

        fields = [
            "date_of_birth",
            "gender",
            "phone",
            "alternate_phone",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "emergency_contact_name",
            "emergency_contact_relationship",
            "emergency_contact_phone",
            "pan_number",
            "aadhaar_number",
            "passport_number",
            "driving_license_number",
            "bank_name",
            "account_number",
            "ifsc_code",
            "bank_branch",
        ]

        widgets = {

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                choices=[
                    ("", "Select Gender"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
                attrs={
                    "class": "form-select",
                },
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone number",
                }
            ),

            "alternate_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Alternate phone number",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Complete address",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "pincode": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "emergency_contact_relationship": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "pan_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ABCDE1234F",
                }
            ),

            "aadhaar_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "12 digit Aadhaar number",
                }
            ),

            "passport_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "driving_license_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "bank_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "account_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "ifsc_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "bank_branch": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")

        if pincode and (
            not pincode.isdigit()
            or len(pincode) != 6
        ):
            raise forms.ValidationError(
                "Pincode must contain exactly 6 digits."
            )

        return pincode

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get("aadhaar_number")

        if aadhaar and (
            not aadhaar.isdigit()
            or len(aadhaar) != 12
        ):
            raise forms.ValidationError(
                "Aadhaar number must contain exactly 12 digits."
            )

        return aadhaar

    def clean_pan_number(self):
        pan = self.cleaned_data.get("pan_number")

        if pan:
            pan = pan.upper()

            if (
                len(pan) != 10
                or not pan[:5].isalpha()
                or not pan[5:9].isdigit()
                or not pan[9].isalpha()
            ):
                raise forms.ValidationError(
                    "Enter a valid PAN number."
                )

        return pan

    def clean_ifsc_code(self):
        ifsc = self.cleaned_data.get("ifsc_code")

        if ifsc:
            ifsc = ifsc.upper()

        return ifsc