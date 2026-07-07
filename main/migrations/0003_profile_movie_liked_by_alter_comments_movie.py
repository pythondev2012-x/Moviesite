from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_remove_movie_actors_remove_movie_rejissor_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("profile_picture", models.ImageField(blank=True, default="profile_pics/default.png", null=True, upload_to="profile_pics/")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="movie",
            name="liked_by",
            field=models.ManyToManyField(blank=True, related_name="liked_movies", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="comments",
            name="movie",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="main.movie", verbose_name="Kino"),
        ),
    ]
