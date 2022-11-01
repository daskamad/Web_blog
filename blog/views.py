from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from . import models
from .form import EmailPostForm, CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView

# Create your views here.
"""
Отображение списка всех постов из бд
"""


class PostListView(ListView):
    queryset = models.Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request):
    object_list = models.Post.published.all()
    paginator = Paginator(object_list, 3)  # По 3 статьи на каждой странице.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})


"""
Отображение деталей каждого поста
"""


class PostDetail(DetailView):
    queryset = models.Post.published.all()  # Мы можем получить доступ только к опубликованным постам
    # model = models.Post  # Доступ ко всем постам независимо от их состояния
    template_name = 'blog/post/detail.html'
    context_object_name = 'post'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(models.Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    # Возвращает объект, который подходит по указанным параметрам, или вызывает исключение 404, если не найдет
    object_list = post.comments.filter(active=True)
    # Обращаемся к определенной записи в бд (ее комментариям и фильтруем)
    new_comment = None
    comments_md = post.comments.filter(active=True)
    # Пагинация комментариев
    page = request.GET.get('page')
    paginator = Paginator(object_list, 5)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    # Сохранение комментариев
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)  # Если запрос Post то, заполняем форму данными из запроса
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)  # Объект будет создан, но не сохранен
            new_comment.post = post  # Указываем ссылку на объект статьи в комментарии
            new_comment.save()  # Сохраняем в бд
            messages.success(request, 'Your comment has been added.')
            # Если все хорошо и форма сохранена выводим сообщение вместо формы
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # Обновляем страницу для избежания повторной отправки формы
    else:  # Get запрос создает пустую форму
        comment_form = CommentForm()
    return render(request, template_name='blog/post/detail.html', context={'post': post,
                                                                           'comments': comments,
                                                                           'new_comment': new_comment,
                                                                           'comment_form': comment_form,
                                                                           'comments_md': comments_md})


"""
Обработка формы и отправка письма
"""


def post_share(request, post_slug):
    post = get_object_or_404(models.Post, slug=post_slug, status='published')  # Получение статьи или 404
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)  # Если Post, то создаем объект формы с данными из формы
        # Проверка данных
        if form.is_valid():
            cd = form.cleaned_data  # Берем все данные из объекта
            post_url = request.build_absolute_uri(post.get_absolute_url())  # Запись ссылки на пост
            subject = f'{cd["name"]} {cd["email"]} recommends you reading {post.title}'
            message = f'Read {post.title} at {post_url}\n\n{cd["name"]}\'s comments:{cd["comments"]}'
            send_mail(subject, message, 'admin@mail.ru', [cd['to']])  # Отправка сообщения
            sent = True

            messages.success(request, f"{cd['to']}")  # Если письмо отправлено выводит сообщение
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # Обновляет страницу для избежания повторной отправки сообщения
    else:
        form = EmailPostForm()
    return render(request, template_name='blog/post/share.html',
                  context={'post': post, 'form': form, 'sent': sent, })
