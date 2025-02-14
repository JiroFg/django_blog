from django.contrib import admin
from .models import Post, Comment

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # atributos que se mostraran en la lista
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    # filtros que se mostraran para la lista
    list_filter = ['status', 'created', 'publish', 'author']
    # campos en los que se aplicara el buscador
    search_fields = ['title', 'body']
    # agrega una barra de jerarquia en la fechas
    date_hierarchy = 'publish'
    # los ordena por estos dos atributos, el orden influye
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS

    # OPCIONES DEL FORM CHANGE Y ADD
    # lleva el campo slug con lo mismo que title, pero con el formato apropiado 
    prepopulated_fields = {'slug': ('title',)}
    # agrega un campo para buscar por ID al author
    raw_id_fields = ['author']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']