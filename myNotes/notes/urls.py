"""Define app url handlers"""
from django.urls import path

from .views import (DeleteNoteView, MainView, NoteCreate, NoteDetail, NoteList,
                    NoteUpdate, TasksDayList, get_day)

urlpatterns = [
    path("main/", MainView.as_view(), name="main"),
    path("main/next/<str:count>", MainView.as_view(), name="note-by-week-next"),
    path("main/prev/<str:count>", MainView.as_view(), name="note-by-week-prev"),
    path("day/", get_day, name="day"),
    path("note/<int:pk>/", NoteDetail.as_view(), name="note"),
    path("notes/<str:deadline>/", TasksDayList.as_view(), name="tasks-day"),
    path("note-create/", NoteCreate.as_view(), name="note-create"),
    path("note-update/<int:pk>/", NoteUpdate.as_view(), name="note-update"),
    path("note-delete/<int:pk>/", DeleteNoteView.as_view(), name="note-delete"),
    path("", NoteList.as_view(), name="notes"),
]
