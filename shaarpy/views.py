# coding: utf-8
"""
   ShaarPy :: Views
"""
from datetime import date, datetime, timedelta, timezone
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (ListView, CreateView, UpdateView, DetailView, DeleteView)
from django.views.generic.base import TemplateView

import logging
import pypandoc

from shaarpy import settings
from shaarpy.forms import LinksForm, MeForm
from shaarpy.models import Links
from shaarpy.tools import (grab_full_article, small_hash, url_cleaning, _get_host)
from simple_search import search_form_factory

logger = logging.getLogger("shaarpy.views")


class SuccessMixin:
    """
    back to detail
    """
    def get_success_url(self) -> str:
        """
        redirect to the Detail object page
        """
        return reverse('link_detail', kwargs={'slug': self.object.url_hashed})


class SettingsMixin:
    """
        mixin to add settings related app data to the templates
    """
    def get_context_data(self, *, object_list=None, **kwargs):
        """
        return settings
        """
        context = super(SettingsMixin, self).get_context_data(**kwargs)
        context['SHAARPY_NAME'] = settings.SHAARPY_NAME
        context['SHAARPY_DESCRIPTION'] = settings.SHAARPY_DESCRIPTION
        context['SHAARPY_AUTHOR'] = settings.SHAARPY_AUTHOR
        context['SHAARPY_ROBOT'] = settings.SHAARPY_ROBOT

        return context


class LinksList(SettingsMixin, ListView):
    """
    home page
    """

    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Links.objects.all()
        else:
            queryset = Links.objects.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)

        SearchForm = search_form_factory(queryset, ['^title', 'text', 'tags'])

        search_form = SearchForm(self.request.GET or {})
        if self.request.GET.get("q"):
            if search_form.is_valid():
                queryset = search_form.get_queryset()

        context = super(LinksList, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        context['object_list'] = queryset
        context['form_search'] = SearchForm
        context['q'] = self.request.GET.get('q')
        # this will be used for the URL in the bookmarklet
        context['hostname'] = _get_host(self.request.build_absolute_uri())

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class LinksCreate(SuccessMixin, SettingsMixin, CreateView):
    """
    add a link / note
    """
    model = Links
    form_class = LinksForm

    # to deal with the popup form trigger from a javascript bookmarklet
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context['add_link'] = True
        context.update(kwargs)
        return super().get_context_data(**context)

    # to deal with the popup form trigger from a javascript bookmarklet

    def get_initial(self) -> dict[str, Any]:
        initial = {}
        if self.request.GET.get('post'):
            url = self.request.GET.get('post')
            url = url_cleaning(url)
            initial = {'url': url,
                       'title': self.request.GET.get('title')}
        return initial

    def form_valid(self, form):
        url = form.cleaned_data['url']
        title = form.cleaned_data['title']
        text = form.cleaned_data['text']
        url = url_cleaning(url)
        if url:
            try:
                # check if url already exist and then redirect to it
                links = Links.objects.get(url=url)
                msg = f"ShaarPy :: link already exists {url}"
                logger.debug(msg)
                return redirect('link_detail', **{'slug': links.url_hashed})
            except Links.DoesNotExist:
                pass

            # when you just want to save the URL and keep the title and body you entered
            # do not go to grab the article content at all
            if title is None and text == '':
                self.object = form.save()
                self.object.title, self.object.text, self.object.image, self.object.video = grab_full_article(url)

        else:
            self.object = form.save()
            if self.object.title is None:
                self.object.title = "Note:"

        self.object = form.save()

        # generate the tiny url
        self.object.url_hashed = small_hash(self.object.date_created.strftime("%Y%m%d_%H%M%S"))

        self.object = form.save()

        # to deal with the popup form trigger from a javascript bookmarklet
        if self.request.GET.get('source') == "bookmarklet":
            return HttpResponse('<script type="text/javascript">window.close();</script>')

        return super().form_valid(form)


class LinksUpdate(SuccessMixin, SettingsMixin, UpdateView):
    """
    update a link / note
    """

    model = Links
    form_class = LinksForm
    slug_field = 'url_hashed'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context['edit_link'] = True
        context.update(kwargs)
        return super().get_context_data(**context)


class LinksDelete(SettingsMixin, DeleteView):
    """
    delete a link / note
    """

    model = Links
    success_url = reverse_lazy("home")


class LinksDetail(SettingsMixin, DetailView):
    """
    view a link / note
    """

    model = Links
    slug_field = 'url_hashed'


class PublicLinks(SettingsMixin, ListView):
    """
        Public Links List
    """
    def get_queryset(self):
        queryset = Links.objects.none()
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        context = super(PublicLinks, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size or 1)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        context['object_list'] = queryset
        context['audience'] = 'public'

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class PrivateLinks(SettingsMixin, ListView):
    """
        Private Links List
    """
    def get_queryset(self):
        queryset = Links.objects.none()
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(private=True)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        context = super(PrivateLinks, self).get_context_data(**kwargs)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size or 1)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        context['object_list'] = queryset
        context['audience'] = 'private'

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class LinksByTagList(SettingsMixin, ListView):
    """
        LinksByTag List
    """
    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        """
            get the links with that tags
        """
        tags = None if self.kwargs['tags'] == '0Tag' else self.kwargs['tags']
        # when tags is None
        # get the data with tags is null
        if tags:
            queryset = Links.objects.filter(tags__contains=tags)
        else:
            queryset = Links.objects.filter(tags__exact=None)

        # to not return private links, reduce the queryset to public links only
        if self.request.user.is_authenticated is False:
            queryset = queryset.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LinksByTagList, self).get_context_data(**kwargs)
        context['tag'] = self.kwargs['tags']
        context.update(kwargs)
        return super().get_context_data(**context)


class TagsList(SettingsMixin, ListView):
    """
        Tags List
    """
    template_name = 'shaarpy/tags_list.html'
    queryset = Links.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)
        tags = []
        for data in queryset:
            if data.tags is not None:
                for tag in data.tags.split(','):
                    tags.append(tag)
            else:
                tags.append('0Tag')
        tags = sorted(tags)
        tags_dict = {}
        for my_tag in tags:
            tags_dict.update({my_tag: tags.count(my_tag)})

        context = {
            'object_list': queryset,
            'tags': tags_dict
        }

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)


class DailyLinks(SettingsMixin, ListView):
    """
        Daily Links List
    """
    template_name = 'shaarpy/daily_list.html'
    queryset = Links.objects.none()

    def get_queryset(self):
        """
        by default, get the "yesterday" links
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        if 'yesterday' in self.kwargs:
            yesterday = self.kwargs['yesterday']

        # do not return private links
        if self.request.user.is_authenticated is False:
            queryset = Links.objects.filter(date_created__date=yesterday, private=False)
        else:
            queryset = Links.objects.filter(date_created__date=yesterday)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """
            checkout which "yesterday" it is
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        if 'yesterday' in self.kwargs:
            yesterday = self.kwargs['yesterday']
            yesterday = datetime.strptime(yesterday, '%Y-%m-%d').replace(tzinfo=timezone.utc)

        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)

        # do not return private links
        if self.request.user.is_authenticated is False:
            previous_date = Links.objects.filter(date_created__lte=yesterday,
                                                 private=False).order_by("-date_created").first()
        else:
            previous_date = Links.objects.filter(date_created__lte=yesterday).order_by("-date_created").first()

        if previous_date:
            previous_date = previous_date.date_created.date()

        # do not return private links
        if self.request.user.is_authenticated is False:
            next_date = Links.objects.filter(date_created__date__gt=yesterday,
                                             private=False).order_by("date_created").first()
        else:
            next_date = Links.objects.filter(date_created__date__gt=yesterday).order_by("date_created").first()
        if next_date:
            next_date = next_date.date_created.date()

        context = {
            'object_list': queryset,
            'previous_date': previous_date,
            'next_date': next_date,
            'current_date': yesterday
        }

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)


# the user
class Me(SettingsMixin, LoginRequiredMixin, TemplateView):

    """
        access to the profile page
    """

    template_name = "me.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.request.user
        return context


class MeUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    """
        Update the User profile
    """
    model = User
    form_class = MeForm
    template_name = 'edit_me.html'
    success_url = reverse_lazy('me')

    def get_object(self, queryset=None):
        """
        get only the data of the current user
        :param queryset:
        :return:
        """
        return User.objects.get(id=self.request.user.id)


# the feeds
class LatestLinksFeed(SettingsMixin, Feed):
    """
        Generate an RSS Feed
        https://docs.djangoproject.com/en/5.0/ref/contrib/syndication/
    """
    title = settings.SHAARPY_NAME
    link = "/"
    description = settings.SHAARPY_DESCRIPTION

    def items(self):
        return Links.objects.filter(private=False).order_by('-date_created')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return pypandoc.convert_text(item.text, 'html', format='gfm')

    def item_link(self, item):
        return reverse('link_detail', args=[item.url_hashed])

    def item_pubdate(self, item):
        return item.date_created


def error_403(request, exception):
    data = {'SHAARPY_AUTHOR': settings.SHAARPY_AUTHOR,
            'SHAARPY_NAME': settings.SHAARPY_NAME,
            'SHAARPY_DESCRIPTION': settings.SHAARPY_DESCRIPTION,
            'SHAARPY_ROBOT': settings.SHAARPY_ROBOT}

    return render(request, 'shaarpy/403.html', data)


def error_404(request, exception):
    data = {'SHAARPY_AUTHOR': settings.SHAARPY_AUTHOR,
            'SHAARPY_NAME': settings.SHAARPY_NAME,
            'SHAARPY_DESCRIPTION': settings.SHAARPY_DESCRIPTION,
            'SHAARPY_ROBOT': settings.SHAARPY_ROBOT}
    return render(request, 'shaarpy/404.html', data)


def error_500(request):
    data = {'SHAARPY_AUTHOR': settings.SHAARPY_AUTHOR,
            'SHAARPY_NAME': settings.SHAARPY_NAME,
            'SHAARPY_DESCRIPTION': settings.SHAARPY_DESCRIPTION,
            'SHAARPY_ROBOT': settings.SHAARPY_ROBOT}
    return render(request, 'shaarpy/500.html', data)
