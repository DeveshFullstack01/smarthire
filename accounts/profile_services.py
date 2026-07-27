"""Service helpers for candidate profiles."""

import logging

from .profile_models import CandidateProfile

logger = logging.getLogger(__name__)


def get_or_create_profile(user):
    """
    Return the user's CandidateProfile, creating a blank one if needed.

    Lets views assume a profile always exists instead of handling the
    "first visit, no row yet" case everywhere. Idempotent: safe to call
    on every page load.
    """
    profile, created = CandidateProfile.objects.get_or_create(user=user)

    if created:
        logger.info(
            "Created blank candidate profile. user_id=%s",
            user.id,
        )

    return profile