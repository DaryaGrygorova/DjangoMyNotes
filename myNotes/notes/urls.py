from django.urls import path
from django.views.generic import TemplateView

from .views import NoteDetail, NoteCreate, NoteUpdate, DeleteView, MainView, NoteList, TasksDayList, getDay

urlpatterns = [
    path("main/", MainView.as_view(), name='main'),
    path("main/next/<str:count>", MainView.as_view(), name='note-by-week-next'),
    path("main/prev/<str:count>", MainView.as_view(), name='note-by-week-prev'),
    path("day/", getDay, name='day'),
    path("note/<int:pk>/", NoteDetail.as_view(), name='note'),
    path("notes/<str:deadline>/", TasksDayList.as_view(), name='tasks-day'),
    path("note-create/", NoteCreate.as_view(), name='note-create'),
    path("note-update/<int:pk>/", NoteUpdate.as_view(), name='note-update'),
    path("note-delete/<int:pk>/", DeleteView.as_view(), name='note-delete'),
    path("", NoteList.as_view(), name='notes'),
]
