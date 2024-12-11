#=================================================DONE===================================================

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for account-related configurations.
    """

    def is_open_for_signup(self, request):
        """
        Determine whether signup is allowed.
        """
        logger.info("Signup check triggered.")
        return True  # Allow signup for social accounts


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account login and linking.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Ensure the social login has an email and link accounts if necessary.
        """
        email = sociallogin.account.extra_data.get("email")

        if not email:
            logger.error("Social login failed: email is missing.")
            raise ValueError("Social login failed. Email is missing.")

        try:
            # Check if the user with the given email already exists
            user = User.objects.get(email=email)
            logger.info(f"User with email {email} found. Linking social account.")

            # Link the social account to the existing user if not already linked
            if not SocialAccount.objects.filter(user=user, provider=sociallogin.account.provider).exists():
                sociallogin.connect(request, user)

            # Activate the user if not already active
            if not user.is_active:
                user.is_active = True
                user.save()
                logger.info(f"User {email} activated via social login.")

            # Attach the existing user to the social login
            sociallogin.user = user

        except User.DoesNotExist:
            logger.info(f"No existing user found with email {email}. Proceeding with signup.")
            # Proceed with normal signup flow

        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            raise IntegrityError("A database error occurred while processing the social login.")

    def get_login_redirect_url(self, request):
        """
        Redirect after social login and include tokens in the query parameters.
        """
        user = request.user
        if user and user.is_authenticated:
            logger.info(f"Generating JWT tokens for user {user.email} after social login.")
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Include tokens in the redirect URL
            return (
                f"https://productsscout.com/signin?step=3"
                f"&email={user.email}"
                f"&access_token={access_token}"
                f"&refresh_token={refresh_token}"
            )
        logger.warning("Social login redirect triggered without an authenticated user.")
        return "https://productsscout.com/signin"

    def save_user(self, request, sociallogin, form=None):
        """
        Automatically activate users created via social login.
        """
        user = super().save_user(request, sociallogin, form)
        user.is_active = True  # Automatically activate the account
        user.save()
        logger.info(f"User {user.email} created and activated via social login.")
        return user
