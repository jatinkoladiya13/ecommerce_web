from django.shortcuts import redirect
from datetime import datetime
import re

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.subscription_required_paths = [
            '/wishlist/', 
            # Add more paths that require a subscription
        ]

    def __call__(self, request):
        if request.user.is_authenticated:
            user_profile = request.user
            if not user_profile.is_subscrib:
                # List of paths that don't require subscription
                if  any(re.match(path, request.path) for path in self.subscription_required_paths):
                    return redirect('subscriptions')
        response = self.get_response(request)
        return response