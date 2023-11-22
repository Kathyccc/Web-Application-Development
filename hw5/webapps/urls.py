"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from socialnetwork import views
from django.urls import path

urlpatterns = [
    path('', views.global_stream_action, name='home'),
    path('register/', views.register_action, name='register'),  
    path('login/', views.login_action, name='login'),  
    path('logout/', views.logout_action, name='logout'),
    path('profile/', views.profile_action, name='profile'),  
    path('global/', views.global_stream_action, name='global'),  
    path('follower/', views.follower_stream_action, name='follower'),  
    path('profile/<int:user_id>/', views.other_profile_action, name='other_profile'),
    path('follow/<int:user_id>/', views.follow, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow, name='unfollow'),
    path('photo/<int:user_id>', views.get_photo, name='photo'),

]

# When no username is provided in the URL, it means that the user is accessing their own profile
