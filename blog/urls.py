from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    # path('', views.post_list, name='post_list'),  # Через функцию
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),  # Через функцию
    # path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    # Через класс указываем slug a не post
    path('<slug:post_slug>/share/', views.post_share, name="post_share")
]
