from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('groups/', views.groups, name='groups'),
    path('authors/', views.authors_list, name='authors_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/like/', views.post_like, name='post_like'),
    path('posts/<int:post_id>/unlike/', views.post_unlike, name='post_unlike'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'comment/<int:comment_id>/del',
        views.del_comment,
        name='del_comment'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('search/', views.search, name='search_results'),
    path('tag/<tag_slug>', views.index, name='index_by_tag'),
    path('', views.index, name='index'),

]
