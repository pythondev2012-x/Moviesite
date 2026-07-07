import asyncio
import threading
import queue
import json
import datetime
from urllib.parse import unquote

from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files import File

from telethon import TelegramClient
from telethon.sessions import StringSession

from .models import Movie
from . import models


# ─── Telethon client ──────────────────────────────────────────────────────────
def get_client() -> TelegramClient:
    return TelegramClient(
        StringSession(settings.TELEGRAM_SESSION),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )


# ─── Fayl hajmini olish ───────────────────────────────────────────────────────
def get_file_size(message_id: int) -> int | None:
    """Telegram dan fayl hajmini oladi (keshlanadi)."""

    async def _get():
        async with get_client() as client:
            msg = await client.get_messages(settings.TELEGRAM_CHANNEL, ids=message_id)
            if msg and msg.media and hasattr(msg.media, "document"):
                return msg.media.document.size
        return None

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_get())
    finally:
        loop.close()


# ─── Real-time stream generator ───────────────────────────────────────────────
def telegram_stream(message_id: int, start: int, end: int):
    """
    Chunk kelishi bilan darhol yield qiladi.
    Alohida thread da async loop ishlatadi, queue orqali sync ga uzatadi.
    """
    q = queue.Queue(maxsize=4)  # 4 chunk bufer (4 MB)
    DONE = object()  # tugatish signali

    def run_loop():
        async def _stream():
            try:
                async with get_client() as client:
                    msg = await client.get_messages(
                        settings.TELEGRAM_CHANNEL, ids=message_id
                    )
                    if not msg or not msg.media:
                        q.put(DONE)
                        return

                    async for chunk in client.iter_download(
                            msg.media,
                            offset=start,
                            chunk_size=512 * 1024,  # 512 KB
                            limit=end - start + 1,
                    ):
                        q.put(chunk)

            except Exception as e:
                print(f"Stream xato: {e}")
            finally:
                q.put(DONE)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(_stream())
        loop.close()

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()

    while True:
        chunk = q.get()
        if chunk is DONE:
            break
        yield chunk


# ─── Stream view ─────────────────────────────────────────────────────────────
def stream_video(request, pk):
    movie = get_object_or_404(Movie, pk=pk, is_active=True)

    if not movie.telegram_message_id:
        return JsonResponse({"error": "Message ID yo'q"}, status=404)

    cache_key = f"movie_size_{pk}"
    file_size = cache.get(cache_key)

    if not file_size:
        file_size = get_file_size(movie.telegram_message_id)
        if file_size:
            cache.set(cache_key, file_size, timeout=60 * 60 * 24)

    if not file_size:
        return JsonResponse({"error": "Fayl topilmadi"}, status=404)

    range_header = request.META.get("HTTP_RANGE", "")
    start = 0
    end = file_size - 1
    status = 200

    if range_header:
        parts = range_header.replace("bytes=", "").split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        status = 206

    content_length = end - start + 1

    response = StreamingHttpResponse(
        telegram_stream(movie.telegram_message_id, start, end),
        status=status,
        content_type="video/mp4",
    )
    response["Content-Length"] = content_length
    response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    response["Accept-Ranges"] = "bytes"
    response["Cache-Control"] = "no-cache"

    return response


# ─── Bot API (ichki) ──────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def add_file(request):
    api_key = request.headers.get("X-API-KEY", "")
    if api_key != settings.INTERNAL_API_KEY:
        return JsonResponse({"error": "Ruxsat yo'q"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON xato"}, status=400)

    file_id = data.get("file_id")
    message_id = data.get("message_id")
    caption = data.get("caption", "")

    if not message_id:
        return JsonResponse({"error": "message_id kerak"}, status=400)

    lines = caption.strip().split("\n")
    title = lines[0] if lines and lines[0] else f"Kino #{message_id}"
    description = "\n".join(lines[1:]) if len(lines) > 1 else ""

    movie, created = Movie.objects.get_or_create(
        telegram_message_id=message_id,
        defaults={
            "title": title,
            "description": description,
            "telegram_file_id": file_id or "",
        },
    )

    return JsonResponse(
        {"id": movie.id, "title": movie.title, "created": created},
        status=201 if created else 200,
    )


# ─── Authentication Views ─────────────────────────────────────────────────────
def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    user = request.user
    profile_obj, _ = models.Profile.objects.get_or_create(user=user)

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile_obj.profile_picture = request.FILES['profile_picture']
        profile_obj.save()
        return redirect('profile')

    liked_movies = Movie.objects.filter(liked_by=user).order_by('-id')
    comments = models.Comments.objects.filter(name__iexact=user.username).order_by('-created_at')

    stats = {
        'watched': liked_movies.count(),
        'comments': comments.count(),
        'favorites': liked_movies.count(),
    }
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile_obj,
        'liked_movies': liked_movies,
        'comments': comments,
        'stats': stats,
    })


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


def custom_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        profile, _ = models.Profile.objects.get_or_create(user=user)

        if not profile.profile_picture or not profile.profile_picture.name:
            default_path = settings.BASE_DIR / 'media' / 'profile_pics' / 'default.png'
            if default_path.exists():
                with default_path.open('rb') as fh:
                    profile.profile_picture.save('default.png', File(fh), save=True)
            else:
                profile.profile_picture = 'profile_pics/default.png'
                profile.save(update_fields=['profile_picture'])

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')

    return render(request, 'signup.html')


# ─── Core Pages ───────────────────────────────────────────────────────────────
def home(request):
    banner_movie = Movie.objects.filter(is_active=True).order_by('-id').first()
    movies = Movie.objects.filter(is_active=True)

    q = request.GET.get("q", "")
    if q:
        movies = movies.filter(title__icontains=q)

    genre = request.GET.get("genre", "")
    if not genre:
        path = request.path or ""
        if path.startswith("/genre-"):
            genre = path.split("/genre-", 1)[1].rstrip('/').replace('%20', ' ')
            genre = unquote(genre)

    if genre:
        movies = movies.filter(genre__name__icontains=genre)

    genres = models.Category.objects.filter().order_by('?')[:6]
    latest_movies = Movie.objects.filter(is_active=True).order_by('-created_at')[:3]

    return render(request, "index.html", {
        "movies": movies,
        "genres": genres,
        "q": q,
        "genre": genre,
        "banner_movie": banner_movie,
        "latest_movies": latest_movies,
    })


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk, is_active=True)
    releted_movie = Movie.objects.filter(genre=movie.genre).exclude(pk=pk)
    comments = models.Comments.objects.filter(movie=movie).order_by('-created_at')

    # Ko'rishlar sonini xavfsiz oshirish (F5 bosganda crash bo'lmaydi)
    Movie.objects.filter(pk=pk).update(views=movie.views + 1)

    # Models.py munosabatiga ko'ra Like tekshiruvi:
    is_liked = False
    if request.user.is_authenticated:
        is_liked = movie.liked_by.filter(id=request.user.id).exists()

    like_count = movie.liked_by.count()

    if request.method == 'POST':
        name = request.POST.get('name')
        text = request.POST.get('text')
        if name and text:
            models.Comments.objects.create(movie=movie, name=name, text=text)
            return redirect(reverse('movie_detail', args=[movie.pk]) + '#tab-comments')

    context = {
        "movie": movie,
        "comments": comments,
        "releted_movie": releted_movie,
        "is_liked": is_liked,
        "like_count": like_count,
    }
    return render(request, "detail.html", context=context)


@login_required
def toggle_like(request, pk):
    movie = get_object_or_404(Movie, pk=pk, is_active=True)
    user = request.user

    # models.py dagi ManyToMany (liked_by) ga asosan logic:
    if movie.liked_by.filter(id=user.id).exists():
        movie.liked_by.remove(user)
    else:
        movie.liked_by.add(user)

    return redirect(request.META.get('HTTP_REFERER', reverse('movie_detail', args=[movie.pk])))


# ─── Filtrlangan kino ro'yxati ────────────────────────────────────────────────
def movie_list(request):
    # 'rejissor' prefetch_related ichiga o'tkazildi (select_related xatosi tuzatildi)
    movies = Movie.objects.filter(is_active=True).select_related('genre', 'last_episode').prefetch_related('actors',
                                                                                                           'rejissor').order_by(
        '-created_at')

    q = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    year = request.GET.get('year', '').strip()
    actors = request.GET.get('actors', '').strip()
    rejisor = request.GET.get('rejisor', '').strip()

    if q:
        movies = movies.filter(title__icontains=q)
    if genre:
        movies = movies.filter(genre_id=genre)
    if year:
        movies = movies.filter(year=year)
    if actors:
        movies = movies.filter(actors=actors)
    if rejisor:
        # ManyToMany field uchun filter to'g'rilandi
        movies = movies.filter(rejissor__id=rejisor)

    # Dinamik tarzda joriy yilni hisoblash (xavfsiz va dinamik)
    current_year = datetime.datetime.now().year
    endyear = current_year - 26

    context = {
        'year': range(current_year, endyear, -1),
        'genre': models.Category.objects.all(),
        'actors': models.Actor.objects.all(),
        'rejisor': models.Rejissor.objects.all(),
        'movie': movies,
        # Shablon (Template) holati saqlanib qolishi uchun o'zgaruvchilar:
        'q': q,
        'selected_genre': genre,
        'selected_year': year,
        'selected_actors': actors,
        'selected_rejisor': rejisor,
    }
    return render(request, 'movie_list.html', context=context)