"""shaarpy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include
from shaarpy.views import (HomeView, LinksCreate, LinksDetail, LinksUpdate, link_delete, TagsList, LinksByTagList)
from shaarpy.views import (DailyLinks, LatestLinksFeed, me, MeUpdate)
from shaarpy import settings


urlpatterns = [
    # MANAGE USERS
    path('accounts/login/', auth_views.LoginView.as_view(extra_context={'SHAARPY_NAME': settings.SHAARPY_NAME}), name="login"),
    path('accounts/profile/', me, name="me"),
    path('accounts/profile/edit/', MeUpdate.as_view(), name='edit_me'),
    path('accounts/', include('django.contrib.auth.urls')),
    # THE APP
    path('', HomeView.as_view(), name="home"),
    path('new/', LinksCreate.as_view(), name='link_create'),
    path('edit/<int:pk>/', LinksUpdate.as_view(), name='link_edit'),
    path('view/<int:pk>/', LinksDetail.as_view(), name='link_detail'),
    path('delete/<int:pk>/', link_delete, name='link_delete'),
    path('tags/', TagsList.as_view(), name='tags_list'),
    re_path('tags/(?P<tags>\w+)$', LinksByTagList.as_view(), name='links_by_tag_list'),
    path('daily/', DailyLinks.as_view(), name='daily'),
    re_path('daily/(?P<yesterday>\d\d\d\d-\d\d-\d\d)', DailyLinks.as_view(), name='daily'),
    # FEEDS
    path('feed/', LatestLinksFeed(), name='atom'),
    # ADMIN
    path('admin/', admin.site.urls),
]
