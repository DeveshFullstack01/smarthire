from .models import Application


ALLOWED_TRANSITIONS = {
    Application.Status.APPLIED: [
        Application.Status.SCREENING,
        Application.Status.REJECTED,
    ],
    Application.Status.SCREENING: [
        Application.Status.INTERVIEW,
        Application.Status.REJECTED,
    ],
    Application.Status.INTERVIEW: [
        Application.Status.OFFER,
        Application.Status.REJECTED,
    ],
    Application.Status.OFFER: [
        Application.Status.REJECTED,
    ],
    Application.Status.REJECTED: [],
}


def can_transition(current_status, new_status):
    """Return True if moving from current_status to new_status is allowed."""
    return new_status in ALLOWED_TRANSITIONS.get(current_status, [])


def get_allowed_next_statuses(current_status):
    """Return the list of (value, label) choices a recruiter may pick next."""
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    labels = dict(Application.Status.choices)
    return [(status, labels[status]) for status in allowed]