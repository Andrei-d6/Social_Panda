from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            messages.success(
                request, f"Your account has been created! You can now Log In"
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    valid = True
    old_image = settings.MEDIA_ROOT + "\\default.jpg"

    if request.method == "POST":
        old_image = f"{settings.MEDIA_URL}{request.user.profile.image}"

        # user Update Form
        u_form = UserUpdateForm(request.POST, instance=request.user)

        # profile Update Form
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect("profile")
        else:
            valid = False
            if u_form.is_valid() and p_form.is_valid():
                messages.warning(
                    request, f"The image does not contain a raccoon! Please be a raccoon"
                )
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "valid": valid,
        "old_image": old_image,
    }

    return render(request, "users/profile.html", context)
