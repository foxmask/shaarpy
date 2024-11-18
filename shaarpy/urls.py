"""
URL configuration for shaarpy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path
from django.views.static import serve

from shaarpy import settings
from shaarpy.views.daily import DailyLinks
from shaarpy.views.feeds import LatestLinksFeed
from shaarpy.views.links import LinksCreate, LinksDelete, LinksDetail, LinksList, LinksUpdate
from shaarpy.views.me import Me, MeUpdate
from shaarpy.views.pub_priv_links import PrivateLinks, PublicLinks
from shaarpy.views.tags import LinksByTagList, TagsList

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(extra_context={"SHAARPY_NAME": settings.SHAARPY_NAME}),
        name="login",
    ),
    path("accounts/profile/", Me.as_view(), name="me"),
    path("accounts/profile/edit/", MeUpdate.as_view(), name="edit_me"),
    path("", LinksList.as_view(), name="home"),
    path("new/", LinksCreate.as_view(), name="link_create"),
    path("edit/<int:pk>/", LinksUpdate.as_view(), name="link_edit"),
    path("link/<slug:slug>/", LinksDetail.as_view(), name="link_detail"),
    re_path(r"delete/(?P<pk>\d+)$", LinksDelete.as_view(), name="link_delete"),
    path("tags/", TagsList.as_view(), name="tags_list"),
    re_path(r"tags/(?P<tags>\w+)$", LinksByTagList.as_view(), name="links_by_tag_list"),
    path("daily/", DailyLinks.as_view(), name="daily"),
    path("links/private/", PrivateLinks.as_view(), name="link_private"),
    path("links/pubic/", PublicLinks.as_view(), name="link_public"),
    re_path(r"daily/(?P<yesterday>\d\d\d\d-\d\d-\d\d)", LinksList.as_view(), name="daily"),
    path("feed/", LatestLinksFeed(), name="feed"),
]

urlpatterns += (
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
)

handler403 = "shaarpy.views.error_403"
handler404 = "shaarpy.views.error_404"
handler500 = "shaarpy.views.error_500"
