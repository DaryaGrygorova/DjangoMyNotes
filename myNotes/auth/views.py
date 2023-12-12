"""Define views for render pages"""
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView


class CustomLoginView(LoginView):
    """Show login form"""

    template_name = "auth/templates/auth/login.html"
    fields = "__all__"


class RegisterPage(FormView):
    """Show register form with auto logining"""

    template_name = "auth/templates/auth/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("main")
        return super().get(*args, **kwargs)
