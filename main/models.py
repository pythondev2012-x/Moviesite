# movies/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Janr")
    icon = models.ImageField(upload_to="categories/", null=True, blank=True)

    def __str__(self):
        return self.name



class Actor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Actors")
    photo = models.ImageField(upload_to="rejissors/", null=True, blank=True)
    year = models.IntegerField(null=True, blank=True, verbose_name="Yili")

    def __str__(self):
        return self.name

class Rejissor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Actors")
    photo = models.ImageField(upload_to="rejissors/", null=True, blank=True)
    year = models.IntegerField(null=True, blank=True, verbose_name="Yili")

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    year = models.IntegerField(null=True, blank=True, verbose_name="Yili")
    genre = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Janr")
    poster = models.ImageField(upload_to="posters/", null=True, blank=True)
    actors = models.ManyToManyField(Actor, verbose_name="Actors", blank=True)
    rejissor = models.ManyToManyField(Rejissor, verbose_name="Rejissor", blank=True)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_movies')

    # Telegram ma'lumotlari
    telegram_file_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Telegram file_id"
    )
    telegram_message_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_episode = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Kino"
        verbose_name_plural = "Kinolar"

    def __str__(self):
        return self.title



class Comments(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Kino")
    text = models.TextField(verbose_name="Tug'ri")
    name = models.CharField(max_length=100, verbose_name="Ismi")
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"