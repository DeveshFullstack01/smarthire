from django.test import TestCase

from applicants.models import Application
from applicants.services import (
    can_transition,
    get_allowed_next_statuses,
)


class ApplicationServiceTests(TestCase):

    def test_applied_to_screening_allowed(self):
        self.assertTrue(
            can_transition(
                Application.Status.APPLIED,
                Application.Status.SCREENING,
            )
        )

    def test_applied_to_rejected_allowed(self):
        self.assertTrue(
            can_transition(
                Application.Status.APPLIED,
                Application.Status.REJECTED,
            )
        )

    def test_screening_to_interview_allowed(self):
        self.assertTrue(
            can_transition(
                Application.Status.SCREENING,
                Application.Status.INTERVIEW,
            )
        )

    def test_interview_to_offer_allowed(self):
        self.assertTrue(
            can_transition(
                Application.Status.INTERVIEW,
                Application.Status.OFFER,
            )
        )

    def test_offer_to_rejected_allowed(self):
        self.assertTrue(
            can_transition(
                Application.Status.OFFER,
                Application.Status.REJECTED,
            )
        )

    def test_applied_to_offer_not_allowed(self):
        self.assertFalse(
            can_transition(
                Application.Status.APPLIED,
                Application.Status.OFFER,
            )
        )

    def test_screening_to_offer_not_allowed(self):
        self.assertFalse(
            can_transition(
                Application.Status.SCREENING,
                Application.Status.OFFER,
            )
        )

    def test_rejected_has_no_transitions(self):
        self.assertFalse(
            can_transition(
                Application.Status.REJECTED,
                Application.Status.APPLIED,
            )
        )

    def test_unknown_status_returns_false(self):
        self.assertFalse(
            can_transition(
                "unknown",
                Application.Status.APPLIED,
            )
        )

    def test_allowed_statuses_for_applied(self):
        expected = [
            (
                Application.Status.SCREENING,
                "Screening",
            ),
            (
                Application.Status.REJECTED,
                "Rejected",
            ),
        ]

        self.assertEqual(
            get_allowed_next_statuses(
                Application.Status.APPLIED
            ),
            expected,
        )

    def test_allowed_statuses_for_screening(self):
        expected = [
            (
                Application.Status.INTERVIEW,
                "Interview",
            ),
            (
                Application.Status.REJECTED,
                "Rejected",
            ),
        ]

        self.assertEqual(
            get_allowed_next_statuses(
                Application.Status.SCREENING
            ),
            expected,
        )

    def test_allowed_statuses_for_rejected(self):
        self.assertEqual(
            get_allowed_next_statuses(
                Application.Status.REJECTED
            ),
            [],
        )

    def test_unknown_status_returns_empty_list(self):
        self.assertEqual(
            get_allowed_next_statuses(
                "unknown"
            ),
            [],
        )