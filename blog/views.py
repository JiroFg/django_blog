from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.db.models import Count
from taggit.models import Tag
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

from blog.forms import EmailPostForm, CommentForm, SearchForm
from .models import Post

# Create your views here.
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(
            Tag,
            slug=tag_slug
        )
        post_list = post_list.filter(tags__in=[tag])
    # creamos el paginator con la lista y la cantidad de elementos por pagina
    paginator = Paginator(post_list, 3)
    # obtenemos el numero de pagina
    page_number = request.GET.get('page', 1)
    # del paginator obtenemos la pagina deseada
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # si es un numero de pagina invalido vamos a obtener la ultima pagina
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'tag': tag 
    }
    return render(request, 'blog/post/list.html', context)


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()
    # post similares
    # obtenemos los id y lo ponemos ponemos en una lista simple
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(
        id=post.id
    )
    # con annotate creamos un nuevo campo con el nombre same_tags que guarda la cantidad de tags en comun
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts
    }
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd["comments"]}"
            )
            sent = True if send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            ) == 1 else False
    else:
        form = EmailPostForm()
    context = {
        'post': post,
        'form': form,
        'sent': sent
    }
    return render(request, 'blog/post/share.html', context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(
        request,
        'blog/post/comment.html',
        context
    )


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', weight='A', config='spanish') + SearchVector('body', weight='B', config='spanish')
            # search_query = SearchQuery(query, config='spanish')
            results = (Post.published.annotate(
                similarity=TrigramSimilarity('title', query)
                # search=search_vector,
                # rank=SearchRank(search_vector, search_query)
            )).filter(
                # rank__gte=0.3
                similarity__gt=0.1
            ).order_by(
                # '-rank'
                '-similarity'
            )
    context = {
        'form': form,
        'query': query,
        'results': results
    }
    return render(
        request,
        'blog/post/search.html',
        context
    )