from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),


    path(
        'profile/',
        views.profile_view,
        name='profile'
    ),

    path(
        'profile/edit/',
        views.profile_edit_view,
        name='profile_edit'
    ),


    path('articles/', views.articles_view, name='articles'),

    path('articles/<int:article_id>/', views.article_detail_view, name='article_detail'),

    path('specialists/', views.specialists_view, name='specialists'),

    path('specialists/<int:specialist_id>/', views.specialist_detail_view, name='specialists_detail'),

    path('forum/', views.forum_view, name='forum'),

    path('forum/topic/<int:topic_id>/', views.forum_topic_view, name='forum_topic'),

    path('forum/create/', views.forum_create_view, name='forum_create'),

]