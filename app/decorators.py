from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
from  django.shortcuts import redirect


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_superuser:
            return HttpResponseRedirect(reverse('login'))
        return view_func(request, *args, **kwargs)

    return wrapper
    
def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect(reverse('login'))
        return view_func(request, *args, **kwargs)
    return wrapper

