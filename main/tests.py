from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Movie, Profile


class ProfileAndLikeTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Action")
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="A sample movie",
            genre=self.category,
            telegram_file_id="movie-1",
        )

    def test_signup_creates_profile_with_default_picture(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "secret123",
                "password_confirm": "secret123",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.profile_picture.name.startswith("profile_pics/"))
        self.assertTrue(profile.profile_picture.name.endswith("default.png"))

    def test_like_toggle_adds_and_removes_like(self):
        user = User.objects.create_user(username="liker", password="secret123")
        self.client.force_login(user)

        response = self.client.post(reverse("toggle_like", args=[self.movie.pk]))

        self.assertRedirects(response, reverse("movie_detail", args=[self.movie.pk]))
        self.movie.refresh_from_db()
        self.assertTrue(self.movie.liked_by.filter(pk=user.pk).exists())
        self.assertEqual(self.movie.likes, 1)

        response = self.client.post(reverse("toggle_like", args=[self.movie.pk]))

        self.assertRedirects(response, reverse("movie_detail", args=[self.movie.pk]))
        self.movie.refresh_from_db()
        self.assertFalse(self.movie.liked_by.filter(pk=user.pk).exists())
        self.assertEqual(self.movie.likes, 0)
