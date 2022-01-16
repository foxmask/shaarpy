# coding: utf-8
"""
   ShaarPy
"""
from datetime import date
from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.contrib.syndication.views import Feed

from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.text import Truncator
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from newspaper import Article
import newspaper
import pypandoc

from shaarpy.forms import LinksForm, MeForm
from shaarpy.models import Links
from shaarpy import settings
from urllib.parse import urlparse


# Beginning of Handling content of Article with NewsPaPer
def get_host(url):
    o = urlparse(url)
    return o.scheme + '://' + o.hostname


def get_brand(url):
    brand = newspaper.build(get_host(url))
    brand.download()
    brand.parse()
    return brand.brand


def grab_full_article(url):
    """
        get the complete article page from the URL
    """
    # get the complete article
    r = Article(url, keep_article_html=True)
    r.download()
    r.parse()
    # convert into markdown
    output = Truncator(r.article_html).chars("400", html=False)
    text = pypandoc.convert_text(output, 'md', format='html')
    title = r.title + ' - ' + get_brand(url)
    return title, text
# End of Handling content of Article with NewsPaPer


@login_required
def link_delete(request, pk):
    link = Links.objects.get(pk=pk)
    link.delete()
    return redirect('home')


class SettingsMixin:
    """
        mixin to add settings data to the templates
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        # get only the unread articles of the folders
        context = super(SettingsMixin, self).get_context_data(**kwargs)
        context['SHAARPY_NAME'] = settings.SHAARPY_NAME
        context['SHAARPY_DESCRIPTION'] = settings.SHAARPY_DESCRIPTION

        return context


class HomeView(SettingsMixin, ListView):
    """
        Links List
    """

    queryset = Links.objects.none()
    paginate_by = 10
    ordering = ['-date_created']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Links.objects.all()
        else:
            queryset = Links.objects.filter(private=False)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        page_size = self.paginate_by
        context_object_name = self.get_context_object_name(queryset)

        context = super(HomeView, self).get_context_data(**kwargs)

        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        context['object_list'] = queryset

        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)

        return context


class LinksCreate(SettingsMixin, LoginRequiredMixin, CreateView):
    """
        Create Links
    """
    model = Links
    form_class = LinksForm

    def form_valid(self, form):
        url = form.cleaned_data['url']
        if url is None:
            self.object = form.save()
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            # just a note
            if url == '' and title == '' and text != '':
                self.object.title = "Note:"
        else:
            try:
                links = Links.objects.get(url=url)
                return redirect('link_detail', **{'pk': links.id})
            except Links.DoesNotExist:
                self.object = form.save()
                title = form.cleaned_data['title']
                text = form.cleaned_data['text']
                # just a note
                if url == '' and title == '' and text != '':
                    self.object.title = "Note:"
                # just an url
                elif url != '':
                    self.object.title, self.object.text = grab_full_article(url)

        return super().form_valid(form)


class LinksDetail(SettingsMixin, DetailView):
    """
        Link Detail
    """
    model = Links


class LinksUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    """
        Link Update
    """

    model = Links
    form_class = LinksForm

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context['edit'] = True
        context.update(kwargs)
        return super().get_context_data(**context)


class LinksByTagList(SettingsMixin, ListView):
    """
        LinksByTag List
    """

    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        tags = self.kwargs['tags']
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(tags__contains=tags)
        else:
            queryset = Links.objects.filter(tags__contains=tags, private=False)
        return queryset

    def get_context_data(self, **kwargs):
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
    ordering = ['-date_created']

    def get_context_data(self, *, object_list=None, **kwargs):

        queryset = object_list if object_list is not None else self.object_list
        context_object_name = self.get_context_object_name(queryset)
        tags = []
        for data in queryset:
            if data.tags is not None:
                for tag in data.tags.split(','):
                    tags.append(tag)
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
        Tags List
    """
    template_name = 'shaarpy/daily_list.html'
    queryset = Links.objects.none()
    ordering = ['-date_created']

    def get_queryset(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        if 'yesterday' in self.kwargs:
            yesterday = self.kwargs['yesterday']
        queryset = Links.objects.filter(date_created__date=yesterday)

        return queryset

# USERS

@login_required
def logout_view(request):
    logout(request)


@login_required()
def me(request):
    return render(request,
                  'me.html',
                  {'object': request.user,
                   'SHAARPY_NAME': settings.SHAARPY_NAME}
                  )


class MeUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = MeForm
    template_name = 'edit_me.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        """
        get only the data of the current user
        :param queryset:
        :return:
        """
        return User.objects.get(id=self.request.user.id)

# FEEDS


class LatestLinksFeed(Feed):
    title = "ShaarPy " + settings.SHAARPY_NAME
    link = "/"
    subtitle = settings.SHAARPY_DESCRIPTION

    def items(self):
        return Links.objects.filter(private=False).order_by('-date_created')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse('link_detail', args=[item.pk])