# ims/decorators.py
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from functools import wraps

def permission_required(perm_codename):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(perm_codename):
                # Render a template with a popup message
                return render(request, 'permission_denied.html', {
                    'message': "You don't have permission to view this page."
                })
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
