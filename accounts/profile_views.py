"""Candidate profile web views."""

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .decorators import role_required
from .models import User
from .profile_services import get_or_create_profile

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .profile_forms import CandidateProfileForm
from .profile_models import Skill


@login_required
@role_required(User.Role.CANDIDATE)
def edit_profile(request):
    profile = get_or_create_profile(request.user)

    if request.method == "POST":
        form = CandidateProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("my-profile")

        messages.error(request, "Please correct the errors below.")
    else:
        form = CandidateProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "profile": profile,
            "skills": profile.skills.all(),
        },
    )


@login_required
@role_required(User.Role.CANDIDATE)
@require_POST
def add_skill(request):
    profile = get_or_create_profile(request.user)
    name = request.POST.get("name", "").strip()

    if name:
        # get_or_create respects the unique (profile, name) constraint,
        # so adding the same skill twice is a harmless no-op.
        Skill.objects.get_or_create(profile=profile, name=name)
        messages.success(request, f"Added skill: {name}")
    else:
        messages.error(request, "Skill name cannot be empty.")

    return redirect("edit-profile")


@login_required
@role_required(User.Role.CANDIDATE)
@require_POST
def delete_skill(request, skill_id):
    profile = get_or_create_profile(request.user)

    skill = get_object_or_404(Skill, id=skill_id, profile=profile)
    skill.delete()

    messages.success(request, "Skill removed.")
    return redirect("edit-profile")



logger = logging.getLogger(__name__)


@login_required
@role_required(User.Role.CANDIDATE)
def my_profile(request):
    profile = get_or_create_profile(request.user)

    context = {
        "profile": profile,
        "skills": profile.skills.all(),
        "experiences": profile.experiences.all(),
        "educations": profile.educations.all(),
    }

    return render(
        request,
        "accounts/profile_detail.html",
        context,
    )