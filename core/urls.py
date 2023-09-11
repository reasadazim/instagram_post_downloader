"""
URL configuration for core project.

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
from django.urls import path
from instadownloadapp.views import *

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic.base import TemplateView #import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('dp/', download_dp, name='download_dp'),
    path('photos/', download_photo_video_reel, name='download_photo_video_reel'),
    path('video/', download_photo_video_reel, name='download_photo_video_reel'),
    path('reel/', download_photo_video_reel, name='download_photo_video_reel'),
    path('story/', download_story, name='download_story'),
    path('highlights/', download_highlight, name='download_highlight'),
    path('instagram_private_downloader/', instagram_private_downloader, name='instagram_private_downloader'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('contact/', contact, name='contact'),
    path('sitemap/', sitemap, name='sitemap'),
    # add the robots.txt file
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

