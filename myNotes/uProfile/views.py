"""
    Define views for render pages
"""
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from uProfile.forms import ProfileForm, UserForm


@login_required
@transaction.atomic
def update_profile(request):
    """Shows and processes the combined form for updating data from the User and Profile models"""
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("main")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(
        request,
        "uProfile/templates/uProfile/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )
