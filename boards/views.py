from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.models import User
from .models import Board, Topic, Post
from .forms import NewTopicForm


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, board_id):
    # try:
    #     board = Board.objects.get(id=board_id)
    # except Board.DoesNotExist:
    #     raise Http404
    board = get_object_or_404(Board, id=board_id)
    return render(request, 'topics.html', {'board': board})

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


def new_topic(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect('board_topics', board_id=board.id)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})
