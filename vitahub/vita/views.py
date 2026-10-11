from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article, ArticleCategory, Specialist, ForumTopic, ForumPost

from .forms import RegisterForm, ProfileForm

from .models import Profile


def home(request):
    return render(request, 'vita/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('home')
    else:
        form = RegisterForm()

    return render(
        request,
        'vita/register.html',
        {'form': form}
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'vita/login.html',
            {
                'error': 'Неверный email или пароль.'
            }
        )

    return render(request, 'vita/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, 'vita/profile.html')

@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(request.user)

            return redirect('profile')

    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'vita/profile_edit.html', {'form': form})




def articles_view(request):
    articles = Article.objects.filter(is_published=True).select_related('category', 'author')
    categories = ArticleCategory.objects.all()
    category_id = request.GET.get('category')

    if category_id and category_id.isdigit():
        articles = articles.filter(category_id=int(category_id))

    return render(request, 'vita/articles.html', {'articles': articles, 'categories': categories,})


def article_detail_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id, is_published=True)

    return render(request, 'vita/article_detail.html', {'article': article})


def specialists_view(request):
    specialists = Specialist.objects.filter(is_available=True).select_related('user')

    return render(request, 'vita/specialists.html', {'specialists': specialists})


def specialist_detail_view(request, specialist_id):
    specialist = get_object_or_404(Specialist.objects.select_related('user'), pk=specialist_id, is_available=True)

    return render(request, 'vita/specialist_detail.html', {'specialist': specialist})


def forum_view(request):
    topics = ForumTopic.objects.select_related('author').all()

    return render(request, 'vita/forum.html', {'topics': topics})


def forum_topic_view(request, topic_id):
    topic = get_object_or_404(ForumTopic.objects.select_related('author'), pk=topic_id)
    posts = topic.posts.select_related('author').all()

    return render(request, 'vita/forum_topic.html', {'topic': topic, 'posts': posts})


@login_required
def forum_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if title and content:
            ForumTopic.objects.create(author=request.user, title=title, content=content)

            return redirect('forum')

        error = 'Заполните название темы и текст сообщения'

    else:
        error = ''

    return render(request, 'vita/forum_create.html', {'error': error})