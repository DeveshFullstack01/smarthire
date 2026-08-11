"""Tests for the interviews module (scheduling, candidate response, scoping)."""

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from applicants.models import Application
from jobs.models import Company, Job

from .models import Interview


class InterviewBase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.recruiter = User.objects.create_user(
            "rec_a",
            password="pass12345",
            role=User.Role.RECRUITER,
            is_verified=True,
        )

        cls.rival = User.objects.create_user(
            "rec_b",
            password="pass12345",
            role=User.Role.RECRUITER,
            is_verified=True,
        )

        cls.candidate = User.objects.create_user(
            "cand_a",
            password="pass12345",
            role=User.Role.CANDIDATE,
            is_verified=True,
        )

        cls.company = Company.objects.create(
            name="Acme",
            owner=cls.recruiter,
        )

        cls.rival_company = Company.objects.create(
            name="Rival",
            owner=cls.rival,
        )

        cls.job = Job.objects.create(
            title="Dev",
            description="d",
            location="X",
            salary=1,
            company=cls.company,
            status=Job.JobStatus.PUBLISHED,
        )

        cls.rival_job = Job.objects.create(
            title="QA",
            description="d",
            location="Y",
            salary=1,
            company=cls.rival_company,
            status=Job.JobStatus.PUBLISHED,
        )

        cls.application = Application.objects.create(
            candidate=cls.candidate,
            job=cls.job,
        )

        cls.rival_application = Application.objects.create(
            candidate=cls.candidate,
            job=cls.rival_job,
        )

        cls.interview = Interview.objects.create(
            application=cls.application,
            scheduled_at=timezone.now()
            + datetime.timedelta(days=2),
            interviewer_name="Panel Lead",
        )

        cls.rival_interview = Interview.objects.create(
            application=cls.rival_application,
            scheduled_at=timezone.now()
            + datetime.timedelta(days=3),
            interviewer_name="Other Lead",
        )


# ==========================================================
# Interview Scoping
# ==========================================================

class InterviewScopingTests(InterviewBase):

    def test_anonymous_redirected(self):

        response = self.client.get(
            reverse("recruiter-interviews")
        )

        self.assertIn(
            response.status_code,
            (302, 403),
        )

    def test_candidate_blocked_from_recruiter_list(self):

        self.client.force_login(
            self.candidate
        )

        response = self.client.get(
            reverse("recruiter-interviews")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_recruiter_sees_only_own_interviews(self):

        self.client.force_login(
            self.recruiter
        )

        response = self.client.get(
            reverse("recruiter-interviews")
        )

        self.assertEqual(
            list(response.context["interviews"]),
            [self.interview],
        )

    def test_candidate_404_on_others_interview(self):

        other = User.objects.create_user(
            "cand_x",
            password="pass12345",
            role=User.Role.CANDIDATE,
        )

        self.client.force_login(other)

        response = self.client.get(
            reverse(
                "interview-detail",
                args=[self.interview.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


# ==========================================================
# Interview Scheduling
# ==========================================================

class InterviewSchedulingTests(InterviewBase):

    def test_schedule_moves_application_to_interview_stage(self):

        self.client.force_login(
            self.recruiter
        )

        new_cand = User.objects.create_user(
            "cand_b",
            password="pass12345",
            role=User.Role.CANDIDATE,
        )

        app = Application.objects.create(
            candidate=new_cand,
            job=self.job,
        )

        response = self.client.post(
            reverse(
                "schedule-interview",
                args=[app.id],
            ),
            {
                "interview_round": (
                    Interview.InterviewRound.TECHNICAL_1
                ),
                "interview_type": (
                    Interview.InterviewType.ONLINE
                ),
                "scheduled_at": "2026-09-01T10:00",
                "duration_minutes": 45,
                "meeting_link": (
                    "https://m.example.com/x"
                ),
                "interviewer_name": "Lead",
                "notes": "Round 1",
            },
        )

        app.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            app.status,
            Application.Status.INTERVIEW,
        )

    def test_cannot_schedule_on_rival_application(self):

        self.client.force_login(
            self.recruiter
        )

        response = self.client.get(
            reverse(
                "schedule-interview",
                args=[self.rival_application.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


# ==========================================================
# Candidate Interview Response
# ==========================================================

class CandidateResponseTests(InterviewBase):

    def test_candidate_can_accept(self):

        self.client.force_login(
            self.candidate
        )

        self.client.post(
            reverse(
                "interview-respond",
                args=[self.interview.id],
            ),
            {
                "response": (
                    Interview.CandidateResponse.ACCEPTED
                )
            },
        )

        self.interview.refresh_from_db()

        self.assertEqual(
            self.interview.candidate_response,
            Interview.CandidateResponse.ACCEPTED,
        )

        self.assertIsNotNone(
            self.interview.responded_at
        )

    def test_reschedule_sets_status(self):

        self.client.force_login(
            self.candidate
        )

        self.client.post(
            reverse(
                "interview-respond",
                args=[self.interview.id],
            ),
            {
                "response": (
                    Interview.CandidateResponse.RESCHEDULE
                ),
                "note": "exam",
            },
        )

        self.interview.refresh_from_db()

        self.assertEqual(
            self.interview.status,
            Interview.Status.RESCHEDULED,
        )

    def test_cannot_respond_twice(self):

        self.client.force_login(
            self.candidate
        )

        url = reverse(
            "interview-respond",
            args=[self.interview.id],
        )

        self.client.post(
            url,
            {
                "response": (
                    Interview.CandidateResponse.ACCEPTED
                )
            },
        )

        self.client.post(
            url,
            {
                "response": (
                    Interview.CandidateResponse.DECLINED
                )
            },
        )

        self.interview.refresh_from_db()

        self.assertEqual(
            self.interview.candidate_response,
            Interview.CandidateResponse.ACCEPTED,
        )