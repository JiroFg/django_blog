from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    # unique for date hace que este campo solo pueda ser unico por la fecha guardada en publish
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # auto_now_add solo agrega la fecha cuando el archivo es creado
    created = models.DateTimeField(auto_now_add=True)
    # auto_now actualiza la fecha cuando el objeto es guardado con .save() por lo que cambiara cuando se actualiza
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    tags = TaggableManager()

    # MANAGERS
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish'])]

    def __str__(self):
        return self.title
    
    # esta funcion nos permite crear un url absoluto del objeto, para ello en el reverse le mandamos la url que se encargara de mostrar el elemento y el ID del elemento
    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])


class Comment(models.Model):
    # Creamos la llave foranea a los post, con related_name podemos declarar la manera en que accederemos a los comentarios desde los posts si no es agregado Django lo crea automaticamente con el nombre del model mas _set (en este caso comment_set)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["created"]
        indexes = [models.Index(fields=['created'])]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'