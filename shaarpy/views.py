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
from django.core.cache import caches
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.base import TemplateView
import pypandoc
from shaarpy.forms import LinksForm, LinksFormEdit, MeForm
from shaarpy.models import Links
from shaarpy import settings
from shaarpy.tools import grab_full_article, rm_md_file, create_md_file, _get_host, small_hash, url_cleaning
from simple_search import search_form_factory

# call the cache
shaarpy_cache = caches['default']


@login_required
def link_delete(request, pk):
    page = None
    if 'page' in request.GET:
        page = request.GET.get('page')
    link = Links.objects.get(pk=pk)
    if link.title is not None and settings.SHAARPY_LOCALSTORAGE_MD:
        rm_md_file(link.title)
    link.delete()
    if page:
        return redirect(reverse('home') + '?page=' + request.GET.get('page'))
    else:
        return redirect('home')


class SuccessMixin:
    """
        mixin to redirect to the view page once save
        use slug vs pk
    """
    def get_success_url(self):
        """
        that method returns to the following link once (Create|Update)View are saved
        """
        # clear the cache when creating/updating a note/link
        # otherwise, the update would have to wait the time of `CACHE_MIDDLEWARE_SECONDS`
        # to be available
        shaarpy_cache.clear()
        # then go back to ...
        return reverse('link_detail', kwargs={'slug': self.object.url_hashed})


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
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)

        SearchForm = search_form_factory(queryset, ['^title', 'text', 'tags'])

        search_form = SearchForm(self.request.GET or {})
        if self.request.GET.get("q"):
            if search_form.is_valid():
                queryset = search_form.get_queryset()

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


class PublicLinks(HomeView):
    """
        Public Links List
    """
    def get_queryset(self):
        queryset = Links.objects.none()
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(private=False)
        return queryset


class PrivateLinks(HomeView):
    """
        Private Links List
    """
    def get_queryset(self):
        queryset = Links.objects.none()
        if self.request.user.is_authenticated:
            queryset = Links.objects.filter(private=True)
        return queryset


class LinksCreate(SettingsMixin, SuccessMixin, LoginRequiredMixin, CreateView):
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
            url = url_cleaning(url)
            initial = {'url': url,
                       'title': self.request.GET.get('title')}
        return initial

    def form_valid(self, form):
        url = form.cleaned_data['url']
        url = url_cleaning(url)
        if url:
            try:
                # check if url already exist and then redirect to it
                links = Links.objects.get(url=url)
                return redirect('link_detail', **{'slug': links.url_hashed})
            except Links.DoesNotExist:
                pass

            self.object = form.save()
            self.object.title, self.object.text, self.object.image, self.object.video = grab_full_article(url)

        else:
            self.object = form.save()
            if self.object.title is None:
                self.object.title = "Note:"

        # generate the tiny url
        self.object.url_hashed = small_hash(self.object.date_created.strftime("%Y%m%d_%H%M%S"))

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
    slug_field = 'url_hashed'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LinksDetail, self).get_context_data(**kwargs)
        context['SHAARPY_DESCRIPTION'] = self.object.title

        return context


class LinksUpdate(SettingsMixin, SuccessMixin, LoginRequiredMixin, UpdateView):
    """
        Link Update
    """

    model = Links
    form_class = LinksFormEdit
    slug_field = 'url_hashed'

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
        """
            get the links with that tags
        """
        print(self.kwargs)
        tags = None if self.kwargs['tags'] == '0Tag' else self.kwargs['tags']
        # when tags is None
        # get the data with tags is null
        if tags:
            queryset = Links.objects.filter(tags__contains=tags)
        else:
            queryset = Links.objects.filter(tags__exact=None)

        if self.request.user.is_authenticated is False:
            queryset = queryset.filter(private=False)
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
        """
            get the tags and count of them
        """
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
    """
        user is logging out
    """
    logout(request)


class MeView(LoginRequiredMixin, TemplateView):

    """
        access to the profile page
    """

    template_name = "me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.request.user
        context['SHAARPY_NAME'] = settings.SHAARPY_NAME
        return context


class MeUpdate(SettingsMixin, LoginRequiredMixin, UpdateView):
    """
        Update the User profile
    """
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
    """
        Generate an RSS Feed
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
