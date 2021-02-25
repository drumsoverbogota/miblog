from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse

import fullurl

from blog.settings import TWITTER_CONSUMER_KEY
from blog.settings import TWITTER_CONSUMER_KEY_SECRET
from blog.settings import TWITTER_TOKEN
from blog.settings import TWITTER_TOKEN_SECRET

from entradas.templatetags.custom_tags import custom_tags_dictionary

from taggit.models import Tag

from .forms import CreateEntradaForm
from .forms import CreateDiarioForm
from .forms import TwitterForm
from .models import Entrada
from .models import Diario

from twitter import *

import logging

logger = logging.getLogger(__name__)

class IndexView(ListView):
    template_name = 'entradas/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 5

    def get_queryset(self):
        return Entrada.objects.order_by('-fecha_publicacion_entrada')


class DetailEntradaView(DetailView):
    model = Entrada
    template_name = 'entradas/detail.html'


class CreateEntradaView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'entradas/create.html'
    form_class = CreateEntradaForm
    success_url = '/'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["custom_tags"] = custom_tags_dictionary
        context["tags"] = Tag.objects.all()
        return context


    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.fecha_publicacion_entrada = timezone.now()
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entradas:detail', kwargs={
                                   'pk': nueva_entrada.id})
        return super().form_valid(form)


class EditEntradaView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'entradas/create.html'

    model = Entrada
    form_class = CreateEntradaForm
    success_url = '/entradas'
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["custom_tags"] = custom_tags_dictionary
        context["tags"] = Tag.objects.all()
        return context

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.fecha_edicion_entrada = timezone.now()
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entradas:detail', kwargs={
                                   'pk': nueva_entrada.id})
        return super().form_valid(form)


class DeleteEntradaView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'entradas/delete.html'
    model = Entrada
    success_url = '/'


class TagView(ListView):
    template_name = 'entradas/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 10

    def get_queryset(self):
        tag = self.kwargs.get("tag")
        return Entrada.objects.filter(tags_entrada__name__in=[tag]).order_by('-fecha_publicacion_entrada')


class DiarioTagView(ListView):
    template_name = 'entradas/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 10

    def get_queryset(self):
        tag = self.kwargs.get("tag")
        return Diario.objects.filter(tags_entrada__name__in=[tag]).order_by('-fecha_publicacion_entrada')


class DiarioIndexView(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name = 'entradas/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 5

    def get_queryset(self):
        return Diario.objects.order_by('-fecha_publicacion_entrada')


class DetailDiarioView(LoginRequiredMixin, DetailView):    
    login_url = '/login'
    model = Diario
    context_object_name = 'entrada'
    template_name = 'entradas/detail.html'


class CreateDiarioView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'entradas/create.html'
    form_class = CreateDiarioForm
    success_url = '/diario'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entradas:diariodetail', kwargs={
                                   'pk': nueva_entrada.id})
        return super().form_valid(form)


class EditDiarioView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'entradas/edit.html'

    model = Diario
    form_class = CreateDiarioForm
    success_url = '/diario'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.fecha_edicion_entrada = timezone.now()
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entradas:diariodetail', kwargs={
                                   'pk': nueva_entrada.id})
        print(self.success_url)
        return super().form_valid(form)


class DeleteDiarioView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'entradas/delete.html'
    model = Diario
    success_url = '/diario'


class TwitterView(LoginRequiredMixin, FormView):
    form_class = TwitterForm
    template_name = 'entradas/twitter.html'
    success_url = '/'

    def form_valid(self, form):
        id_entrada = str(self.kwargs.get('pk'))
        tweet = form.cleaned_data.get('tweet')
        if id_entrada and tweet:
            t = Twitter(
                auth=OAuth(
                    TWITTER_TOKEN,
                    TWITTER_TOKEN_SECRET,
                    TWITTER_CONSUMER_KEY,
                    TWITTER_CONSUMER_KEY_SECRET
                ))
            
            status = tweet + " " + self.request.build_absolute_uri('/entradas/'+id_entrada)
            logger.info("Prueba")
            logger.info(status)
            
        return super().form_valid(form)