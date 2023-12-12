"""
    Define views for render pages
"""
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import CreateNoteForm, UpdateNoteForm
from .models import Note

from utils.constants import WEEK_DAYS
from utils.utils import get_last_monday, get_weather


class MainView(LoginRequiredMixin, ListView):
    """
    Show the page with entries excluding the type 'note'
    with isComplete status 'false'
    organized by week days and ordered by weight.
    """

    model = Note
    template_name = "notes/templates/notes/main.html"
    context_object_name = "notes"

    # get date of last Monday
    start_date = get_last_monday()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add to context weather info
        location = self.request.user.profile.location or "Kyiv"
        weather_info = get_weather(location)
        context["weather"] = weather_info

        context["notes"] = context["notes"].filter(user=self.request.user)

        # returns entries excluding the type 'note'
        context["notes"] = context["notes"].exclude(isComplete="True")

        # returns entries excluding the type 'note'
        context["notes"] = context["notes"].exclude(type="Note")

        # define dates of target week
        context["week_count"] = self.kwargs.get("count", 0)
        if "next" in self.request.path or "prev" in self.request.path:
            self.start_date += timedelta(days=7 * int(self.kwargs["count"]))
        context["start_date"] = self.start_date
        context["end_date"] = self.start_date + timedelta(days=6)

        # organizing data by week days with ordering it by weight
        notes_week = {value: {} for _, value in enumerate(WEEK_DAYS)}
        for i, day in enumerate(WEEK_DAYS):
            current_date = self.start_date + timedelta(days=i)
            notes_week[day]["date"] = current_date
            notes_week[day]["tasks"] = (
                context["notes"].filter(deadline=current_date).order_by("weight")
            )
            context["notes_week"] = notes_week

        return context


class NoteList(LoginRequiredMixin, ListView):
    """
    Show the page with all entries with type 'note' ordered by creation date.
    """

    model = Note
    context_object_name = "notes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notes"] = context["notes"].filter(user=self.request.user)

        # returns entries with type 'note' only
        context["notes"] = context["notes"].filter(type="Note")

        # filter data by search query
        search_input = self.request.GET.get("search-area") or ""
        if search_input != "":
            context["notes"] = context["notes"].filter(title__icontains=search_input)
        context["search_input"] = search_input

        # ordering data by creation date
        context["notes"] = context["notes"].order_by("-create_at")

        return context


class TasksDayList(LoginRequiredMixin, ListView):
    """
    Show the page with form for creating notes.
    Redirect user to page with notes on deadline day
    """

    model = Note
    context_object_name = "tasks"
    template_name = "notes/templates/notes/tasks_day_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)

        # returns entries excluding the type 'note'
        context["tasks"] = context["tasks"].exclude(type="Note")

        # filter data by target date with ordering by status
        target_date = self.kwargs["deadline"]
        context["by_date"] = target_date
        context["tasks"] = (
            context["tasks"].filter(deadline=target_date).order_by("isComplete")
        )

        # filter data by search query
        search_input = self.request.GET.get("search-area") or ""
        if search_input != "":
            context["tasks"] = context["tasks"].filter(title__icontains=search_input)
        context["search_input"] = search_input

        return context


class NoteDetail(LoginRequiredMixin, DetailView):
    """Show the page with notes details."""

    model = Note
    context_object_name = "note"
    template_name = "notes/note.html"


class NoteCreate(LoginRequiredMixin, CreateView):
    """
    Show the page with form for creating notes.
    Redirect user to page with notes on deadline day
    """

    model = Note
    form_class = CreateNoteForm
    template_name = "notes/templates/notes/note_create_form.html"
    # success_url = reverse_lazy('main')

    def get_success_url(self):
        current_date = self.request.POST.get(
            "deadline", datetime.today().strftime("%Y-%m-%d")
        )
        return f"/notes/notes/{current_date}/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.title:
            return self.form_invalid(form)
        return super().form_valid(form)


class NoteUpdate(LoginRequiredMixin, UpdateView):
    """
    Show the page with form for updating notes by id.
    Redirect user to page with notes on deadline day
    """

    model = Note
    form_class = UpdateNoteForm
    template_name = "notes/templates/notes/note_update_form.html"
    # success_url = reverse_lazy('main')

    def get_success_url(self):
        current_date = self.request.POST.get(
            "deadline", datetime.today().strftime("%Y-%m-%d")
        )
        return f"/notes/notes/{current_date}/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.title:
            return self.form_invalid(form)
        return super().form_valid(form)


class DeleteNoteView(LoginRequiredMixin, DeleteView):
    """
    Show the confirmation page before deleting notes by id.
    Redirect user to page with notes on deadline day
    """

    model = Note
    context_object_name = "note"

    def get_success_url(self):
        current_date = self.request.POST.get(
            "deadline", datetime.today().strftime("%Y-%m-%d")
        )
        return f"/notes/notes/{current_date}/"


@login_required
def get_day(request):
    """Redirect user to page with notes on target day"""
    current_date = request.POST.get("deadline", datetime.today().strftime("%Y-%m-%d"))
    return redirect(f"/notes/notes/{current_date}/")
