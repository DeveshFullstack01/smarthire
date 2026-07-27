"""Signals for the accounts app."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .profile_models import CandidateProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_candidate_profile(sender, instance, created, **kwargs):
    """
    Give every newly created candidate a blank profile automatically.

    Only fires on creation (`created` is True) and only for candidates,
    so recruiters and admins don't get profiles they'd never use.
    """
    if created and instance.role == User.Role.CANDIDATE:
        CandidateProfile.objects.create(user=instance)
        logger.info(
            "Auto-created candidate profile via signal. user_id=%s",
            instance.id,
        )