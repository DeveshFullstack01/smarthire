"""Tests for the notifications app (service, in-app, mark-read, email)."""

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User

from .models import Notification
from .services import notify, mark_all_read


class NotifyServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "u1", password="x", email="u1@example.com",
            role=User.Role.CANDIDATE,
        )

    def test_notify_creates_in_app(self):
        n = notify(self.user, "Hello", "/x/")
        self.assertIsNotNone(n)
        self.assertEqual(self.user.notifications.count(), 1)
        self.assertFalse(n.is_read)

    def test_notify_without_subject_sends_no_email(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            mail.outbox = []
            notify(self.user, "No email", "/x/")
            self.assertEqual(len(mail.outbox), 0)

    def test_notify_with_subject_sends_email(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            mail.outbox = []
            notify(self.user, "Ping", "/x/", email_subject="Subject here")
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["u1@example.com"])

    def test_notify_blank_email_no_send(self):
        no_email = User.objects.create_user(
            "u2", password="x", email="", role=User.Role.CANDIDATE,
        )
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            mail.outbox = []
            notify(no_email, "Ping", "/x/", email_subject="Subj")
            self.assertEqual(len(mail.outbox), 0)
            self.assertEqual(no_email.notifications.count(), 1)


class NotificationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "u1", password="x", role=User.Role.CANDIDATE,
        )
        cls.other = User.objects.create_user(
            "u2", password="x", role=User.Role.CANDIDATE,
        )

    def test_anonymous_redirected(self):
        r = self.client.get(reverse("notification-list"))
        self.assertEqual(r.status_code, 302)

    def test_list_renders(self):
        notify(self.user, "A", "/a/")
        self.client.force_login(self.user)
        r = self.client.get(reverse("notification-list"))
        self.assertEqual(r.status_code, 200)

    def test_open_marks_read_and_redirects(self):
        n = notify(self.user, "A", "/interviews/1/")
        self.client.force_login(self.user)
        r = self.client.get(reverse("notification-open", args=[n.id]))
        n.refresh_from_db()
        self.assertTrue(n.is_read)
        self.assertEqual(r.status_code, 302)

    def test_cannot_open_others_notification(self):
        n = notify(self.other, "A", "/a/")
        self.client.force_login(self.user)
        r = self.client.get(reverse("notification-open", args=[n.id]))
        self.assertEqual(r.status_code, 404)

    def test_mark_all_read(self):
        notify(self.user, "A", "/a/")
        notify(self.user, "B", "/b/")
        self.client.force_login(self.user)
        self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(
            self.user.notifications.filter(is_read=False).count(), 0
        )

    def test_mark_all_read_is_post_only(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse("notification-mark-all-read"))
        self.assertEqual(r.status_code, 405)