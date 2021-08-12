from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from users.forms import CustomUserChangeForm
from .forms import PostForm, CommentForm, TagForm
from .models import Post, Comment, PostLike, PostDislike, Tag
from django.contrib import messages
from users.models import CustomUser
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def rest_post_list(request):
    if request.method == 'GET':
        posts = Post.objects.filter().order_by('-created_date')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def rest_post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views +=1
    post.save()
    liked = False
    disliked = False
    if request.user.is_authenticated:
        likes_count = PostLike.objects.filter(post_id=pk, user=request.user).count()
        dislikes_count = PostDislike.objects.filter(post_id=pk, user=request.user).count()

        if likes_count == 0 and dislikes_count == 0:
        	liked = False
        	disliked = False

       	elif likes_count == 1:
            liked = True
            disliked = False

        else:
            liked = False
            disliked = True
    
    if post.dislikes_count() == 0 and post.likes_count() == 0:
    	percent = 0

    else:
    	percent = (post.likes_count() / (post.dislikes_count() + post.likes_count())) * 100

    return render(request, 'blog/post_detail.html', {'post': post, 'liked': liked, 'disliked': disliked, 'percent': percent})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post adicionado com Sucesso!')
            logger.info()
            return redirect('post_detail', pk=post.pk)
        else:
            logger.error('Erro ao adicionar o post!')
            messages.error(request, 'Erro ao adicionar o post!')
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            form.save_m2m()
            logger.info()
            messages.success(request, 'Post alterado com sucesso!')
            return redirect('post_detail', pk=post.pk)
        else:
            logger.error('Erro ao alterar o post!')
            messages.error(request, 'Erro ao alterar o post!')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

def num_users(request):
    num = CustomUser.objects.count()
    return HttpResponse(num, content_type="text/html")

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    logger.info()
    messages.success(request, 'Post publicado!')
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    logger.info()
    messages.success(request, 'Post deletado!')
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            comment.post = post
            logger.info()
            messages.success(request, 'Comentario salvo!')
            return redirect('post_detail', pk=post.pk)
        else:
            logger.error('Erro ao salvar comentario!')
            messages.error(request, 'Erro ao salvar comentario!')
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    logger.info()
    messages.success(request, 'Comentario adicionado com Sucesso!')
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    logger.info()
    messages.success(request, 'Comentario deletado!')
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def post_like(request, pk):
    dislikes_count = PostDislike.objects.filter(post_id=pk, user=request.user).count()
    likes_count = PostLike.objects.filter(post_id=pk, user=request.user).count()

    if dislikes_count == 0 and likes_count == 0:
        post_like, created = PostLike.objects.get_or_create(post_id=pk, user=request.user)
    else:
        logger.warning('User trying to like/dislike again.')

    return redirect('post_detail', pk=pk)

@login_required
def post_dislike(request, pk):
    likes_count = PostLike.objects.filter(post_id=pk, user=request.user).count()
    dislikes_count = PostDislike.objects.filter(post_id=pk, user=request.user).count()

    if likes_count == 0 and dislikes_count == 0:
        post_dislike, created = PostDislike.objects.get_or_create(post_id=pk, user=request.user)
    else:
        logger.warning('User trying to like/dislike again.')

    return redirect('post_detail', pk=pk)

@login_required
def user_list(request):
    UserModel = get_user_model()
    users = UserModel.objects.all().order_by('birth_date')

    return render(request, 'blog/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_remove(request, pk):
    UserModel = get_user_model()
    user = get_object_or_404(UserModel, pk=pk)
    user.delete()
    logger.info()
    messages.success(request, 'Usuário removido!')

    return redirect('user_list')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, pk):
    UserModel = get_user_model()
    user = get_object_or_404(UserModel, pk=pk)
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            logger.info()
            messages.success(request, 'Usuário alterado!')
            return redirect('user_list')
        else:
            logger.error('Erro ao alterar usuario!')
            messages.error(request, 'Erro ao alterar usuario!')
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'blog/user_edit.html', {'form': form})
 
@login_required
def tag_new(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            posts = form.cleaned_data['posts']
            for post in posts:
                tag.post_set.add(post)
        logger.info()
        messages.success(request, 'Tag criada!')
        return redirect('tag_list')
    else:
        form = TagForm()
    return render(request, 'blog/tag_edit.html', {'form': form})

@login_required
def tag_list(request):
    tags = Tag.objects.all()

    return render(request, 'blog/tag_list.html', {'tags': tags})

