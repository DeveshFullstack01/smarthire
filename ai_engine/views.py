from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applicants.models import Application

from .models import InterviewQuestion
from .question_service import generate_interview_questions
from ai_engine.services import analyze_resume_file

@login_required
def interview_questions(request, application_id):
    """Display generated interview questions for an application."""

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    questions = (
        InterviewQuestion.objects.filter(
            application=application,
        )
        .order_by(
            "skill",
            "created_at",
        )
    )

    context = {
        "application": application,
        "questions": questions,
    }

    return render(
        request,
        "ai_engine/interview_questions.html",
        context,
    )


@login_required
def generate_questions(request, application_id):
    """Generate interview questions and redirect to the dashboard."""

    generate_interview_questions(application_id)

    return redirect(
        "interview-questions",
        application_id=application_id,
    )