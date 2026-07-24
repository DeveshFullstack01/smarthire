import os

from django import forms
from django.core.exceptions import ValidationError

from .models import Resume


class ResumeForm(forms.ModelForm):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
    }

    class Meta:
        model = Resume
        fields = [
            "file",
        ]

    def clean_file(self):
        file = self.cleaned_data.get("file")

        if not file:
            raise ValidationError(
                "Please select a resume to upload."
            )

        extension = os.path.splitext(file.name)[1].lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                "Only PDF, DOC and DOCX files are allowed."
            )

        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(
                "Resume size must not exceed 5 MB."
            )

        return file