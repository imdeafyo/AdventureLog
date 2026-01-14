# your_app/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import user_signed_up
from django.conf import settings
from django.urls import resolve, Resolver404
from invitations.models import Invitation


class CustomAccountAdapter(DefaultAccountAdapter):
    """Control regular signup based on DISABLE_REGISTRATION, but allow invites."""
    
    def is_open_for_signup(self, request):
        """
        Allow signup only if:
        - DISABLE_REGISTRATION is False, OR
        - the request is for the invitation acceptance URL, OR
        - there's a valid invitation key in the request parameters.
        """
        # If registration is globally open, allow as usual
        if settings.DISABLE_REGISTRATION is False:
            return True

        # If an invitation-verified email is stashed in the session, allow signup
        if hasattr(request, "session") and request.session.get("account_verified_email"):
            return True

        # When disabled, allow signups via invitation accept URL
        try:
            match = resolve(request.path_info)
            print("Resolved view name:", match.view_name)
            if match.view_name == "invitations:accept-invite":
                return True
        except Resolver404:
            pass
        

        # Block any other signup
        return False

    def get_user_signed_up_signal(self):
        """Return the allauth `user_signed_up` signal for compatibility with
        django-invitations which expects this method on the adapter.
        """
        return user_signed_up


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Control social signup based on SOCIALACCOUNT_ALLOW_SIGNUP setting"""
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Determines if social signup is allowed.
        Check SOCIALACCOUNT_ALLOW_SIGNUP env variable.
        
        Returning False shows the same 'signup_closed.html' template
        as regular signup, but only blocks NEW social signups.
        Existing users can still log in.
        """
        # If social signup is disabled, only allow existing users
        if not settings.SOCIALACCOUNT_ALLOW_SIGNUP:
            return sociallogin.is_existing
        
        return True
