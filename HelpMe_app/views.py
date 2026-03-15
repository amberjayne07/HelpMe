from http.client import HTTPResponse

from django.shortcuts import render

from HelpMe_app.forms import *
from HelpMe_app.models import *
from django.shortcuts import get_object_or_404


def home(request):
    categories = Category.objects.prefetch_related('question_set').all()
    return render(request, 'home.html', {'categories': categories})

def post_overview(request, question_id):
    question = get_object_or_404(Question, questionID=question_id)
    return render(request, 'post_overview.html', {'question': question})

def about(request):
    return render(request, 'about_us.html')

def sign_up(request):
    form = RegistrationForm()
    return render(request, 'authentication/sign_up.html', {'form': form})

def login(request):
    return render(request, 'authentication/login.html')

def my_account(request):
    return render(request, 'authentication/my_account.html')

def test_everything(request):
    context = {
        'users': User.objects.all(),
        'categories': Category.objects.all(),
        'questions': Question.objects.all(),
        'comments': Comment.objects.all(),
        'notifications': Notification.objects.all(),
        'polls': Poll.objects.all(),
        'poll_items': PollItem.objects.all(),
    }
    return render(request, 'testing_only/test_everything.html', context)
