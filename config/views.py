import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    logger.debug("Health check endpoint called.")

    return JsonResponse(
        {
            "application": "SmartHire ATS",
            "status": "UP",
            "version": "1.0.0",
        }
    )