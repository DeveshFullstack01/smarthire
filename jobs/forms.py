from datetime import date

from django import forms

from .models import Job


class JobForm(forms.ModelForm):

    class Meta:
        model = Job

        fields = [
            "title",
            "description",
            "location",
            "job_type",
            "salary",
            "experience",
            "vacancies",
            "application_deadline",
            "status",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter job title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter job description",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter job location",
                }
            ),

            "job_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter salary",
                    "min": 0,
                }
            ),

            "experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Required experience (Years)",
                    "min": 0,
                }
            ),

            "vacancies": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Number of vacancies",
                    "min": 1,
                }
            ),

            "application_deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

        labels = {
            "title": "Job Title",
            "description": "Job Description",
            "location": "Location",
            "job_type": "Job Type",
            "salary": "Salary",
            "experience": "Required Experience (Years)",
            "vacancies": "Number of Vacancies",
            "application_deadline": "Application Deadline",
            "status": "Job Status",
        }

    def clean_salary(self):
        salary = self.cleaned_data["salary"]

        if salary <= 0:
            raise forms.ValidationError(
                "Salary must be greater than zero."
            )

        return salary

    def clean_experience(self):
        experience = self.cleaned_data["experience"]

        if experience < 0:
            raise forms.ValidationError(
                "Experience cannot be negative."
            )

        return experience

    def clean_vacancies(self):
        vacancies = self.cleaned_data["vacancies"]

        if vacancies < 1:
            raise forms.ValidationError(
                "Vacancies must be at least 1."
            )

        return vacancies

    def clean_application_deadline(self):
        deadline = self.cleaned_data["application_deadline"]

        if deadline < date.today():
            raise forms.ValidationError(
                "Application deadline cannot be in the past."
            )

        return deadline