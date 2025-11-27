from django.urls import include, path
from .views import *

urlpatterns = [
    path('hello/', hello, name='hello'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('current_user/', current_user, name='current_user'),
    path('secret/', secret, name='secret'),
    path('tweets/', tweets_list, name='tweets_list'),
    path('tweets/<int:tweet_id>/like/', like_tweet, name='like_tweet'),
    path('profile/', get_profile, name='get_profile'),
    path('profile/<str:username>/follow/', follow_user, name='follow_user'),
    path('tweets/<int:tweet_id>/', tweet_detail, name='tweet_detail'),
]