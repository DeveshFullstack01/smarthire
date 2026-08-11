import logging
import os
import mimetypes
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from ai_engine.services import calculate_match_score
from applicants.models import Application
from django.http import FileResponse, Http404
from .forms import ResumeForm
from .models import Resume

logger = logging.getLogger(__name__)


@login_required
def upload_resume(request, application_id):
    logger.info(
        "Resume upload requested. candidate_id=%s application_id=%s",
        request.user.id,
        application_id,
    )

    application = get_object_or_404(
        Application,
        id=application_id,
        candidate=request.user,
    )

    resume = Resume.objects.filter(
        application=application,
    ).first()

    if request.method == "POST":

        form = ResumeForm(
            request.POST,
            request.FILES,
            instance=resume,
        )

        if form.is_valid():

            old_file = None

            if resume and resume.file:
                old_file = resume.file.path

            resume = form.save(commit=False)
            resume.application = application
            resume.save()

            if (
                old_file
                and os.path.exists(old_file)
                and old_file != resume.file.path
            ):
                os.remove(old_file)

            logger.info(
                "Resume saved successfully. resume_id=%s application_id=%s",
                resume.id,
                application.id,
            )

            try:

                logger.info(
                    "Starting AI resume matching. application_id=%s",
                    application.id,
                )

                result = calculate_match_score(
                    resume.file.path,
                    application.job.description,
                )

                application.match_score = result["score"]
                application.save(
                    update_fields=[
                        "match_score",
                    ]
                )

                resume.parsed_data = result
                resume.save(
                    update_fields=[
                        "parsed_data",
                    ]
                )

                logger.info(
                    "AI matching completed. application_id=%s score=%s",
                    application.id,
                    result["score"],
                )

                messages.success(
                    request,
                    f"Resume uploaded successfully. "
                    f"Match Score: {result['score']}%",
                )

            except Exception:
                logger.exception(
                    "AI resume matching failed. application_id=%s",
                    application.id,
                )

                messages.warning(
                    request,
                    "Resume uploaded successfully, "
                    "but AI matching could not be completed.",
                )

            return redirect("my-applications")

        logger.warning(
            "Resume validation failed. candidate_id=%s application_id=%s",
            request.user.id,
            application.id,
        )

    else:

        form = ResumeForm(
            instance=resume,
        )

    return render(
        request,
        "resumes/upload_resume.html",
        {
            "form": form,
            "application": application,
            "resume": resume,
        },
    )
@login_required
def view_resume(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    if application.job.company.owner != request.user:
        raise Http404("Resume not found.")

    try:
        resume = application.resume

    except Resume.DoesNotExist:
        messages.error(
            request,
            "Resume has not been uploaded."
        )
        return redirect(
            "recruiter-applications",
            job_id=application.job.id,
        )

    return redirect(resume.file.url)

@login_required
def download_resume(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    if application.job.company.owner != request.user:
        raise Http404("Resume not found.")

    try:
        resume = application.resume

    except Resume.DoesNotExist:

        messages.error(
            request,
            "Resume has not been uploaded.",
        )

        return redirect(
            "recruiter-applications",
            job_id=application.job.id,
        )

    file_path = resume.file.path

    if not os.path.exists(file_path):
        raise Http404("Resume file not found.")

    extension = os.path.splitext(file_path)[1]

    filename = (
        f"{application.candidate.username}_"
        f"{application.job.title.replace(' ', '_')}_Resume"
        f"{extension}"
    )

    content_type, _ = mimetypes.guess_type(file_path)

    response = FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=filename,
        content_type=content_type,
    )

    return response
@login_required
def resume_analysis(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    if application.job.company.owner != request.user:
        raise Http404("Resume not found.")

    try:
        resume = application.resume

    except Resume.DoesNotExist:

        messages.error(
            request,
            "Resume not uploaded."
        )

        return redirect(
            "recruiter-applications",
            job_id=application.job.id,
        )

    context = {
        "application": application,
        "resume": resume,
        "parsed": resume.parsed_data or {},
        "view_resume_url": "view-resume",
        "download_resume_url": "download-resume",
    }

    return render(
        request,
        "resumes/resume_analysis.html",
        context,
    )



