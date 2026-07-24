from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Restrict a template view to specific user roles.

    This is a decorator FACTORY: it takes roles and returns a decorator.
    Do not decorate this function itself.

    Always stack `@login_required` ABOVE it on the view, so anonymous
    users get a friendly redirect to the login page instead of a 403:

        @login_required
        @role_required(User.Role.RECRUITER, User.Role.ADMIN)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.role not in roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator