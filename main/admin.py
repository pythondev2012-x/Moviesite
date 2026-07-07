from django.contrib import admin
from unfold.admin import ModelAdmin
from  . import models

@admin.register(models.Movie)
class MovieAdmin(ModelAdmin):
    list_display = ['title', 'year', 'genre', 'views', 'is_active']
    list_filter = ['genre', 'year', 'is_active']
    search_fields = ['title', 'description']

@admin.register(models.Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(models.Actor)
class ActorAdmin(ModelAdmin):
    list_display = ['name', 'year']
    search_fields = ['name']

@admin.register(models.Rejissor)
class RejissorAdmin(ModelAdmin):
    list_display = ['name', 'year']
    search_fields = ['name']

@admin.register(models.Comments)
class CommentsAdmin(ModelAdmin):
    list_display = ['name', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'text']