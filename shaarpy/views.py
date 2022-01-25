# coding: utf-8
"""
   ShaarPy :: Views
"""
from datetime import date, datetime, timedelta

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DetailView
import pypandoc
from shaarpy.forms import LinksForm, LinksFormEdit, MeForm, SearchForm
from shaarpy.models import Links
from shaarpy import settings
from shaarpy.tools import grab_full_article, rm_md_file, create_md_file, _get_host


def search(request):
    form = SearchForm(request.GET or {})
    if form.is_valid():
        results = form.get_queryset()
    else:
        results = Links.objects.none()

    data = {
        'form': form,
        'object_list': results,
    }
    return render(request, 'search.html', data)


@login_required
def link_delete(request, pk):
    page = None
    if 'page' in request.GET:
        page = request.GET.get('page')
    link = Links.objects.get(pk=pk)
    if link.title is not None:
        rm_md_file(link.title)
    link.delete()
    if page:
        return redirect(reverse('home') + '?page=' + request.GET.get('page'))
    else:
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
        context['SHAARPY_AUTHOR'] = settings.SHAARPY_AUTHOR
        context['SHAARPY_ROBOT'] = settings.SHAARPY_ROBOT

        return context


class HomeView(SettingsMixin, ListView):
    """
        Links List
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

        form = SearchForm(self.request.GET or {})
        if form.is_valid():
            queryset = form.get_queryset()

        page_size = self.paginate_by
        context_object_name = self.get_context_object_name(queryset)

        context = super(HomeView, self).get_context_data(**kwargs)

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


def clean_url(url):
    """
        drop unexpected content of the URL
    """
    for pattern in ('&utm_source=', '?utm_source=', '#xtor=RSS-'):
        pos = url.find(pattern)
        if pos > 0:
            url = url[0:pos]
    return url


class LinksCreate(SettingsMixin, LoginRequiredMixin, CreateView):
    """
        Create Links
    """
    model = Links
    form_class = LinksForm

    # to deal with the popup form trigger from a javascript bookmarklet
    def get_context_data(self, **kwargs):
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
    def get_initial(self):
        initial = {}
        if self.request.GET.get('post'):
            url = self.request.GET.get('post')
            url = clean_url(url)
            initial = {'url': url,
                       'title': self.request.GET.get('title')}
        return initial

    def form_valid(self, form):
        url = form.cleaned_data['url']

        if url:
            try:
                # check if url already exist and then redirect to it
                links = Links.objects.get(url=url)
                return redirect('link_detail', **{'pk': links.id})
            except Links.DoesNotExist:
                pass

            self.object = form.save()
            self.object.title, self.object.text, self.object.image, self.object.video = grab_full_article(url)

        else:
            self.object = form.save()
            if self.object.title is None:
                self.object.title = "Note:"

        self.object = form.save()

        if settings.SHAARPY_LOCALSTORAGE_MD:
            create_md_file(settings.SHAARPY_LOCALSTORAGE_MD,
                           self.object.title, self.object.url, self.object.text, self.object.tags,
                           self.object.date_created, self.object.private,
                           self.object.image, self.object.video)

        # to deal with the popup form trigger from a javascript bookmarklet
        if self.request.GET.get('source') == "bookmarklet":
            return HttpResponse('<script type="text/javascript">window.close();</script>')

        return super().form_valid(form)


class LinksDetail(SettingsMixin, DetailView):
    """
        Link Detail
    """
    model = Links

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LinksDetail, self).get_context_data(**kwargs)
        context['SHAARPY_DESCRIPTION'] = self.object.title

        return context


class LinksUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    """
        Link Update
    """

    model = Links
    form_class = LinksFormEdit

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context['edit_link'] = True
        context.update(kwargs)
        return super().get_context_data(**context)


class LinksByTagList(SettingsMixin, ListView):
    """
        LinksByTag List
    """

    queryset = Links.objects.none()
    paginate_by = 10

    def get_queryset(self):
        tags = None if self.kwargs['tags'] == '0Tag' else self.kwargs['tags']
        # when tags is None
        # get the data with tags is null
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(tags__exact=tags)
        else:
            queryset = Links.objects.filter(tags__exact=tags, private=False)
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

        previous_date = Links.objects.filter(date_created__lte=yesterday).order_by("-date_created").first()
        if previous_date:
            previous_date = previous_date.date_created.date()

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
        return reverse('link_detail', args=[item.pk])
