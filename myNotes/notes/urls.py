"""Define app url handlers"""
from django.urls import path

from .views import (
    DeleteNoteView,
    MainView,
    NoteCreateView,
    NoteDetailView,
    NoteListView,
    NoteUpdateView,
    TasksAllListView,
    TasksDayListView,
    get_day,
)

urlpatterns = [
    path("main/", MainView.as_view(), name="main"),
    path("main/next/<str:count>", MainView.as_view(), name="note-by-week-next"),
    path("main/prev/<str:count>", MainView.as_view(), name="note-by-week-prev"),
    path("day/", get_day, name="day"),
    path("note-create/", NoteCreateView.as_view(), name="note-create"),
    path("note/<int:pk>/", NoteDetailView.as_view(), name="note"),
    path("note-update/<int:pk>/", NoteUpdateView.as_view(), name="note-update"),
    path("note-delete/<int:pk>/", DeleteNoteView.as_view(), name="note-delete"),
    path("notes/<str:deadline>/", TasksDayListView.as_view(), name="tasks-day"),
    path("all/", TasksAllListView.as_view(), name="tasks-all"),
    path("", NoteListView.as_view(), name="notes"),
]
