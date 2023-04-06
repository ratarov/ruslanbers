# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, UserForm, ProfileForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class MyPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


@login_required
@transaction.atomic
def user_profile(request):
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(
        request.POST or None,
        files=request.FILES or None,
        instance=request.user.profile
    )
    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        return redirect('users:user_profile')
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/user_profile.html', context)
