import threading

_thread_local = threading.local()


def get_current_user():
    """Return the user attached to the current request thread, or None."""
    return getattr(_thread_local, "user", None)


class CurrentUserMiddleware:
    """Stores the current request user on thread-local for audit fields."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.user = getattr(request, "user", None)
        response = self.get_response(request)
        # Clean up
        _thread_local.user = None
        return response
