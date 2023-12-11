from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin

from utils.constants import WEEK_DAYS
from .models import Note
from utils.utils import get_weather, get_last_monday



class MainView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/templates/notes/main.html'
    context_object_name = 'notes'

    # get date of last Monday
    start_date = get_last_monday()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get weather info
        location = self.request.user.profile.location or 'Kyiv'
        weather_info = get_weather(location)

        context['weather'] = weather_info
        context['notes'] = context['notes'].filter(user=self.request.user)
        context['notes'] = context['notes'].exclude(isComplete='True')
        context['notes'] = context['notes'].exclude(type='Note')

        context['week_count'] = self.kwargs.get('count', 0)
        if 'next' in self.request.path or 'prev' in self.request.path:
            self.start_date += timedelta(days=7*int(self.kwargs['count']))

        context['start_date'] = self.start_date
        context['end_date'] = self.start_date + timedelta(days=6)

        notes_week = {value: {} for _, value in enumerate(WEEK_DAYS)}
        for i,  day in enumerate(WEEK_DAYS):
            current_date = self.start_date + timedelta(days=i)
            notes_week[day]['date'] = current_date
            notes_week[day]['tasks'] = context['notes'].filter(deadline=current_date).order_by("weight")
            context['notes_week'] = notes_week

        return context


class NoteList(LoginRequiredMixin, ListView):
    model = Note
    context_object_name = 'notes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = context['notes'].filter(user=self.request.user)

        # returns entries with type 'note' only
        context['notes'] = context['notes'].filter(type="Note")
        search_input = self.request.GET.get('search-area') or ''

        if search_input != '':
            context['notes'] = context['notes'].filter(title__icontains=search_input)

        context['search_input'] = search_input
        context['notes'] = context['notes'].order_by("-create_at")
        return context


class TasksDayList(LoginRequiredMixin, ListView):
    model = Note
    context_object_name = 'tasks'
    template_name = 'notes/templates/notes/tasks_day_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['tasks'] = context['tasks'].exclude(type="Note")

        current_date = self.kwargs['deadline']
        context['by_date'] = current_date
        context['tasks'] = context['tasks'].filter(deadline=current_date).order_by("weight").order_by("isComplete")

        search_input = self.request.GET.get('search-area') or ''
        if search_input != '':
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)
        context['search_input'] = search_input

        return context


class NoteDetail(LoginRequiredMixin, DetailView):
    model = Note
    context_object_name = 'note'
    template_name = 'notes/note.html'


class NoteCreate(LoginRequiredMixin, CreateView):
    model = Note
    fields = ['title', 'desc', 'deadline', 'weight', 'type']
    template_name = 'notes/templates/notes/note_create_form.html'
    # success_url = reverse_lazy('main')

    def get_success_url(self):
        current_date = self.request.POST.get('deadline', datetime.today().strftime("%Y-%m-%d"))
        return f'/notes/notes/{current_date}/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteUpdate(LoginRequiredMixin, UpdateView):
    model = Note
    fields = ['title', 'desc', 'deadline', 'weight', 'type', 'isComplete']
    template_name = 'notes/templates/notes/note_update_form.html'
    # success_url = reverse_lazy('main')

    def get_success_url(self):
        current_date = self.request.POST.get('deadline', datetime.today().strftime("%Y-%m-%d"))
        return f'/notes/notes/{current_date}/'

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    context_object_name = 'note'
    # success_url = reverse_lazy('main')

    def get_success_url(self):
        current_date = self.request.POST.get('deadline', datetime.today().strftime("%Y-%m-%d"))
        return f'/notes/notes/{current_date}/'

@login_required
def getDay(request):
    current_date = request.POST.get('deadline', datetime.today().strftime("%Y-%m-%d"))
    return redirect(f'/notes/notes/{current_date}/')
