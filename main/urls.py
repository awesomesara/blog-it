from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from .views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='home'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category'),
    path('post-detail/<int:pk>/', PostDetailView.as_view(), name='detail'),
    path('add-post/', add_post, name='add-post'),
    path('update-post/<int:pk>/', update_post, name='update-post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete-post'),
    path('delete-comment/<int:pk>/', DeleteCommentView.as_view(), name='delete-comment'),
    path('favourite-post/<int:pk>/', favourite_post, name='favourite_post'),
    path('favourites/', favourite_post_list, name='favourite_post_list'),
    path('likes-post/<int:pk>/', likes_post, name='likes_post'),

]