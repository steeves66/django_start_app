from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import UpdateView

from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, board_id):
    # try:
    #     board = Board.objects.get(id=board_id)
    # except Board.DoesNotExist:
    #     raise Http404
    board = get_object_or_404(Board, id=board_id)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'topics.html', {'board': board, 'topics': topics})


# Old method without FormTopic
# def new_topic(request, board_id):
#     board = get_object_or_404(Board, id=board_id)
#     if request.method == 'POST':
#         subject = request.POST['subject']
#         message = request.POST['message']
#
#         user = User.objects.first()
#
#         topic = Topic.objects.create(
#             subject=subject,
#             board=board,
#             starter=user
#         )
#
#         post = Post.objects.create(
#             message=message,
#             topic=topic,
#             created_by=user
#         )
#
#         return redirect('board_topics', board_id=board.id)
#
#     return render(request, 'new_topic.html', {'board': board})


@login_required
def new_topic(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user  # request connected
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            # return redirect('board_topics', board_id=board.id)
            return redirect('topic_posts', pk=board_id, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, id=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, id=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


class PostUpdateView(UpdateView):
    model = Post
    fields = ('message')
    template_name = 'edit_post.html'
    pk_url_kwargs = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)