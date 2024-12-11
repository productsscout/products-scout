#=================================================DONE===================================================

from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.utils import timezone
import datetime
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import Cart  # Import the Cart model
from .serializers import CartSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from .utils import verify_captcha, send_email_smtp  # Assuming you have a verify_captcha utility

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from .serializers import UserSerializer
from .models import Cart
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterUserRateThrottle(UserRateThrottle):
    rate = '5/hour'

from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterUserRateThrottle])
def register_user(request):
    """
    Register a new user. The user remains inactive until email verification.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Save the user as inactive initially
            user = serializer.save(is_active=False)

            # Generate a unique verification code
            user.verification_code = get_random_string(64)
            user.save()

            # Generate email content
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.verification_code}"
            email_subject = 'Verify Your Products Scout Account'
            email_body = (
                f"Dear {user.first_name},<br><br>"
                f"Welcome to Products Scout! We’re thrilled to have you on board.<br><br>"
                f"To get started, please verify your email address. This step ensures your account’s security and enables full access to our product recommendations and features.<br><br>"
                f"Simply click the link below to verify your account:<br><br>"
                f'<a href="{verification_url}">{verification_url}</a><br><br>'
                f"If you didn’t sign up for Products Scout, please ignore this email—no further action is required.<br><br>"
                f"Thank you for choosing Products Scout to help you find the best products effortlessly. We’re here to assist you every step of the way.<br><br>"
                f"Warm regards,<br>"
                f"The Products Scout Team<br><br>"
                f"---<br>"
                f"Need help? Contact us anytime at <a href='mailto:support@productsscout.com'>support@productsscout.com</a><br>"
                f"Visit our website: <a href='https://productsscout.com'>https://productsscout.com</a><br>"
            )

            # Send the email using the no-reply alias
            email_sent = send_email_smtp(
                subject=email_subject,
                body=email_body,
                recipient_email=user.email,
                is_html=True,
                sender_email=settings.EMAIL_NO_REPLY
            )

            if email_sent:
                logger.info(f"Verification email sent to {user.email}")
                return Response(
                    {"message": "User registered successfully. Please check your email to verify your account."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                logger.error(f"Failed to send verification email to {user.email}")
                return Response(
                    {"error": "User registered, but verification email could not be sent. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred while registering the user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        logger.warning(f"Invalid registration attempt: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    """
    Check if the email is already registered.
    """
    email = request.data.get('email')

    if not email:
        logger.warning("Email check attempted without providing an email address.")
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the email already exists
    email_exists = User.objects.filter(email=email).exists()
    if email_exists:
        logger.info(f"Email check for registered email: {email}")
        # Generic response to avoid email enumeration
        return Response({"message": "If this email exists, instructions will be sent."}, status=status.HTTP_200_OK)

    logger.info(f"Email is valid and available for registration: {email}")
    return Response({"message": "Email is valid and available."}, status=status.HTTP_200_OK)


# (=================DONE==================)
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, code):
    """
    Verify the user's email based on the verification code.
    """
    try:
        user = User.objects.get(verification_code=code, is_active=False)
        user.is_active = True
        user.verification_code = ""
        user.save()

        logger.info(f"Email verified for user: {user.email}")
        return render(request, 'email_verification_success.html', {"message": "Email verified successfully!"})
    except User.DoesNotExist:
        logger.warning(f"Email verification failed for code: {code}")
        return render(request, 'email_verification_failed.html', {"error": "Invalid or expired verification link."})


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Handles the forgot password functionality by sending a reset code to the user's email.
    """
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        # Check if the account is verified
        if not user.is_active:
            logger.warning(f"Password reset attempted for unverified email: {email}")
            return Response(
                {"error": "Email is not verified.", "resend_verification": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check cooldown for sending reset codes
        if user.password_reset_code_expiry and timezone.now() < user.password_reset_code_expiry:
            time_left = (user.password_reset_code_expiry - timezone.now()).seconds
            logger.info(f"Password reset code request throttled for email: {email}")
            return Response(
                {"error": f"Please wait {time_left // 60} minutes and {time_left % 60} seconds before requesting a new code."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Generate a new password reset code and expiry time
        user.password_reset_code = get_random_string(6, allowed_chars="0123456789")
        user.password_reset_code_expiry = timezone.now() + timedelta(minutes=2)
        user.save()

        # Generate the email content
        email_subject = "Password Reset Request"
        email_body = (
            f"Hello {user.first_name},<br><br>"
            f"We’ve received your request to reset your password for your Products Scout account. Let’s get you back on track!<br><br>"
            f"Here’s your unique password reset code:<br><br>"
            f"<strong style='font-size: 18px;'>✨ {user.password_reset_code} ✨</strong><br><br>"
            f"🔒 <strong>This code is valid for only 2 minutes</strong>, so be sure to use it promptly. If the code expires, don’t worry—you can always request a new one.<br><br>"
            f"If you didn’t request a password reset, please disregard this email. Your account is secure, and no changes have been made.<br><br>"
            f"Need help? Our support team is just a click away and happy to assist you.<br><br>"
            f"Thank you for choosing Products Scout as your go-to platform for finding the best products and deals tailored to your needs.<br><br>"
            f"Best regards,<br>"
            f"The Products Scout Team<br><br>"
            f"---<br>"
            f"📩 <strong>Support</strong>: <a href='mailto:support@productsscout.com'>support@productsscout.com</a><br>"
            f"🌐 <strong>Visit us</strong>: <a href='https://productsscout.com'>https://productsscout.com</a><br>"
            f"✨ <strong>Explore smarter shopping today!</strong><br>"
        )

        # Send the email using the no-reply alias
        email_sent = send_email_smtp(
            subject=email_subject,
            body=email_body,
            recipient_email=user.email,
            is_html=True,
            sender_email=settings.EMAIL_NO_REPLY,
        )

        if email_sent:
            logger.info(f"Password reset code sent to: {email}")
            return Response({"message": "Password reset code sent successfully."}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send password reset code to: {email}")
            return Response({"error": "Failed to send password reset code. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except User.DoesNotExist:
        # Respond with a generic message to prevent email enumeration
        logger.warning(f"Password reset attempted for non-existent email: {email}")
        return Response({"message": "If this email exists, a password reset code has been sent."}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error during password reset request: {str(e)}")
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resends the email verification link if the user is not verified.
    """
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        if user.is_active:
            logger.info(f"Resend verification attempted for an already verified account: {email}")
            return Response({"error": "Account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new verification code
        user.verification_code = get_random_string(length=64)
        user.verification_code_expiry = timezone.now() + timedelta(hours=24)
        user.save()

        # Generate verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.verification_code}"

        # Create the email content
        email_subject = "Verify Your Products Scout Account"
        email_body = (
            f"Dear {user.first_name},<br><br>"
            f"We’re excited to have you as part of the Products Scout community!<br><br>"
            f"To activate your account and unlock personalized product recommendations, exclusive deals, and premium features, please verify your email address.<br><br>"
            f"Click the link below to complete your verification:<br><br>"
            f'<a href="{verification_url}">{verification_url}</a><br><br>'
            f"This link will remain valid for the next 24 hours. If you encounter any issues or the link expires, you can always request a new verification email.<br><br>"
            f"If you didn’t create this account, please disregard this email—your information is safe with us.<br><br>"
            f"Thank you for choosing Products Scout as your trusted partner for smarter shopping.<br><br>"
            f"Warm regards,<br>"
            f"The Products Scout Team<br><br>"
            f"---<br>"
            f"Need help? Contact us at <a href='mailto:support@productsscout.com'>support@productsscout.com</a><br>"
            f"Visit us: <a href='https://productsscout.com'>https://productsscout.com</a><br>"
        )

        # Send the verification email using the no-reply alias
        email_sent = send_email_smtp(
            subject=email_subject,
            body=email_body,
            recipient_email=user.email,
            is_html=True,
            sender_email=settings.EMAIL_NO_REPLY,
        )

        if email_sent:
            logger.info(f"Verification email resent to {email}")
            return Response({"message": "Verification email sent successfully."}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to resend verification email to {email}")
            return Response({"error": "Failed to resend verification email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except User.DoesNotExist:
        logger.warning(f"Resend verification attempt for non-existent user: {email}")
        # Respond with a generic message to prevent email enumeration
        return Response({"message": "If the email exists, a verification link has been sent."}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error during resend verification: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    """
    Verify the password reset code for the given email.
    """
    email = request.data.get("email")
    code = request.data.get("verification_code")

    if not email or not code:
        logger.warning("Code verification attempted with missing email or code.")
        return Response({"error": "Email and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email, password_reset_code=code)

        # Check if the password reset code has expired
        if user.password_reset_code_expiry and timezone.now() > user.password_reset_code_expiry:
            logger.info(f"Verification code expired for email: {email}")
            return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Extend the expiry time (e.g., set a 2-minute extension for user convenience)
        user.password_reset_code_expiry = timezone.now() + timedelta(minutes=2)
        user.save()

        logger.info(f"Verification code successfully verified for email: {email}")
        return Response({"message": "Verification code verified successfully."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        logger.warning(f"Invalid verification code attempt for email: {email}")
        return Response({"error": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Resets the user's password after verifying the email and ensuring all criteria are met.
    """
    email = request.data.get("email")
    new_password = request.data.get("new_password")
    verification_code = request.data.get("verification_code")

    # Validate input
    if not email or not new_password or not verification_code:
        logger.warning("Password reset attempted with missing fields.")
        return Response(
            {"error": "Email, new password, and verification code are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email, password_reset_code=verification_code)

        # Check if the verification code has expired
        if user.password_reset_code_expiry and timezone.now() > user.password_reset_code_expiry:
            logger.info(f"Expired verification code used for password reset: {email}")
            return Response(
                {"error": "Verification code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password strength (you can use Django's validators)
        if len(new_password) < 8:
            logger.warning(f"Weak password attempt for email: {email}")
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password.isnumeric() or new_password.isalpha():
            return Response(
                {"error": "Password must include both letters and numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset the password
        user.set_password(new_password)
        user.password_reset_code = ""  # Clear the reset code
        user.password_reset_code_expiry = None  # Clear the code expiry
        user.save()

        logger.info(f"Password reset successfully for email: {email}")
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        logger.warning(f"Password reset attempted for non-existent user: {email}")
        return Response({"error": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_user(request):
    """
    Check if a user exists and is active based on the provided email.
    """
    email = request.data.get('email', '').strip()

    if not email:
        logger.warning("User check attempted without providing an email address.")
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        # Provide a generic response while including active status
        logger.info(f"User check performed for email: {email}")
        return Response({"exists": True, "is_active": user.is_active}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Respond with a generic "not found" message to avoid email enumeration
        logger.info(f"User does not exist for email: {email}")
        return Response({"exists": False, "is_active": False}, status=status.HTTP_200_OK)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_password(request):
    """
    Check if the provided password is valid for the given email.
    """
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()

    if not email or not password:
        logger.warning("Password check attempted with missing email or password.")
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate the user
    user = authenticate(username=email, password=password)

    if user:
        logger.info(f"Password check successful for email: {email}")
        return Response({"valid": True}, status=status.HTTP_200_OK)
    else:
        logger.warning(f"Password check failed for email: {email}")
        # Provide a generic response to prevent leaking whether the email exists
        return Response(
            {"valid": False, "error": "Invalid email or password. Please try again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# from datetime import datetime, timedelta  # Correct import for datetime and timedelta
#
# @api_view(['POST'])
# @permission_classes([AllowAny])  # Ensure login endpoint is accessible to all
# def login_user(request):
#     """
#     Login a user and return JWT tokens.
#     """
#     email = request.data.get('email')
#     password = request.data.get('password')
#     captcha_token = request.data.get('captchaToken')
#
#     # Verify CAPTCHA (optional)
#     if captcha_token and not verify_captcha(captcha_token):
#         return JsonResponse(
#             {"error": "Invalid CAPTCHA. Please try again."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     # Authenticate the user
#     user = authenticate(request, email=email, password=password)
#
#     if user is not None:
#         if not user.is_active:
#             return JsonResponse(
#                 {"error": "Account is not active. Please verify your email."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         # Generate JWT tokens with custom access token lifetime
#         refresh = RefreshToken.for_user(user)
#         refresh.access_token.set_exp(lifetime=timedelta(days=2))  # Set access token lifetime to 2 days
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)
#
#             # Manually calculate expires_in based on the new access token expiration
#         access_token_exp = datetime.utcnow() + timedelta(days=2)  # Use correct timedelta
#         expires_in = (access_token_exp - datetime.utcnow()).total_seconds()
#
#         return JsonResponse(
#             {
#                 "message": "Login successful.",
#                 "access_token": access_token,
#                 "refresh_token": refresh_token,
#                 "expires_in": expires_in,
#                 "user": {
#                     "email": user.email,
#                     "first_name": user.first_name,
#                     "last_name": user.last_name,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )
#     else:
#         return JsonResponse(
#             {"error": "Invalid email or password."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def social_login_jwt(request):
#     """
#     Issue JWT tokens for users logging in via social accounts and set them as HTTP-only cookies.
#     """
#     try:
#         # Ensure the request contains the necessary session data
#         if not request.session.session_key:
#             return JsonResponse({"error": "No valid session found. Please log in again."}, status=401)
#
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             return JsonResponse({"error": "No valid session. Social login failed."}, status=401)
#
#         user = request.user
#
#         # Ensure the user has a linked social account
#         social_account = SocialAccount.objects.filter(user=user).first()
#         if not social_account:
#             return JsonResponse({"error": "Social account not linked. Please log in via social media."}, status=400)
#
#         # Generate JWT tokens for the user
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)
#
#         # Log in the user to establish a session
#         login(request, user)
#
#         # Prepare the response
#         response = JsonResponse({
#             "message": "Social login successful.",
#             "expires_in": refresh.access_token.lifetime.total_seconds(),
#             "user": {
#                 "email": user.email,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#             },
#         }, status=200)
#
#         # Set HTTP-only cookies
#         response.set_cookie(
#             key='access_token',
#             value=access_token,
#             httponly=True,  # HTTP-only flag
#             secure=True,  # Secure flag (use HTTPS in production)
#             max_age=refresh.access_token.lifetime.total_seconds(),  # Expiry time
#             samesite='Strict',  # Prevent cross-site cookie access
#         )
#         response.set_cookie(
#             key='refresh_token',
#             value=refresh_token,
#             httponly=True,  # HTTP-only flag
#             secure=True,  # Secure flag (use HTTPS in production)
#             max_age=refresh.lifetime.total_seconds(),  # Expiry time
#             samesite='Strict',  # Prevent cross-site cookie access
#         )
#
#         return response
#
#     except Exception as e:
#         return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_tokens(request):
    """
    Generate JWT access and refresh tokens for a valid user.
    """
    email = request.data.get('email', '').strip()

    if not email:
        logger.warning("Token generation attempted without providing an email.")
        return Response({"error": "Email is required."}, status=400)

    try:
        # Verify user exists and is active
        User = get_user_model()
        user = User.objects.get(email=email)

        if not user.is_active:
            logger.warning(f"Inactive user attempted token generation: {email}")
            return Response({"error": "Account is inactive. Please contact support."}, status=403)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        logger.info(f"Tokens successfully generated for email: {email}")

        return Response({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": refresh.access_token.lifetime.total_seconds(),
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }, status=200)

    except User.DoesNotExist:
        logger.warning(f"Token generation failed for non-existent user: {email}")
        return Response({"error": "Invalid email or password."}, status=404)

    except Exception as e:
        logger.error(f"Unexpected error during token generation: {str(e)}")
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=500)


# (=================DONE==================)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_email(request):
    """
    Fetch the authenticated user's email address.
    """
    try:
        email = request.user.email
        logger.info(f"User email fetched successfully for user: {email}")
        return Response({"email": email}, status=200)
    except Exception as e:
        logger.error(f"Error fetching user email: {str(e)}")
        return Response({"error": "Failed to fetch user email. Please try again later."}, status=500)


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow access without requiring user authentication
def logout_user(request):
    """
    Log out the user and blacklist the refresh token.
    """
    try:
        # Extract the refresh token from the request
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            logger.warning("Logout attempt without providing a refresh token.")
            return Response({"error": "Refresh token is required for logout."}, status=400)

        # Blacklist the provided refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Clear any cookies or session storage for the client
        response = Response({"message": "Logout successful."}, status=200)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        logger.info("User successfully logged out.")
        return response

    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return Response({"error": "Failed to log out. Please try again later."}, status=500)


# (=================DONE==================)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require JWT authentication
def user_first_name(request):
    """
    Fetch the authenticated user's first name.
    """
    try:
        first_name = request.user.first_name
        logger.info(f"Fetched first name for user: {first_name}")
        return Response({"first_name": first_name}, status=200)
    except Exception as e:
        logger.error(f"Failed to fetch user's first name: {str(e)}")
        return Response({"error": "Failed to fetch user details. Please try again later."}, status=500)


# (=================DONE==================)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Fetch authenticated user's profile details.
    """
    try:
        user = request.user
        serializer = UserSerializer(user)
        logger.info(f"Fetched profile for user: {user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        return Response({"error": "Failed to fetch profile. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# (=================DONE==================)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update authenticated user's profile details.
    """
    user = request.user
    data = request.data

    # Validate profile fields
    if "first_name" in data and len(data["first_name"].strip()) > 10:
        logger.warning(f"Invalid first name length for user: {user.email}")
        return Response(
            {"error": "First name cannot exceed 10 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "last_name" in data and len(data["last_name"].strip()) > 50:
        logger.warning(f"Invalid last name length for user: {user.email}")
        return Response(
            {"error": "Last name cannot exceed 50 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Allow partial updates
    serializer = UserSerializer(user, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        logger.info(f"Profile updated successfully for user: {user.email}")
        return Response(
            {"message": "Profile updated successfully."},
            status=status.HTTP_200_OK,
        )
    else:
        logger.warning(f"Profile update failed for user: {user.email} - Errors: {serializer.errors}")
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

# ============================================================================

# (=================DONE==================)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add a product to the user's cart or update the quantity if it already exists.
    """
    data = request.data
    user = request.user  # Get the logged-in user

    # Validate required fields
    product_name = data.get("product_name")
    product_quantity = data.get("product_quantity", 1)

    if not product_name:
        logger.warning(f"Add to cart failed: Missing product name for user {user.email}")
        return Response(
            {"error": "Product name is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(product_quantity, int) or product_quantity <= 0:
        logger.warning(f"Add to cart failed: Invalid product quantity for user {user.email}")
        return Response(
            {"error": "Product quantity must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Check if the product already exists in the cart
        existing_cart_item = Cart.objects.filter(user=user, product_name=product_name).first()

        if existing_cart_item:
            # If product already exists, update the quantity
            existing_cart_item.product_quantity += product_quantity
            existing_cart_item.save()
            logger.info(f"Updated quantity for {product_name} in cart for user {user.email}")
            return Response(
                {"message": "Product quantity updated in cart."},
                status=status.HTTP_200_OK,
            )

        # Create a new cart item
        serializer = CartSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=user)  # Associate the cart item with the logged-in user
            logger.info(f"Added {product_name} to cart for user {user.email}")
            return Response(
                {"message": "Product added to cart successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        logger.warning(f"Cart item creation failed for user {user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error adding to cart for user {user.email}: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# (=================DONE==================)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart_items(request):
    """
    Retrieve all cart items for the logged-in user.
    """
    user = request.user
    try:
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        logger.info(f"Cart items retrieved for user {user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error retrieving cart items for user {user.email}: {str(e)}")
        return Response(
            {"error": "Failed to retrieve cart items. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# (=================DONE==================)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_id):
    """
    Update the quantity or other details of a cart item.
    """
    user = request.user
    try:
        # Fetch the cart item belonging to the user
        cart_item = Cart.objects.get(id=cart_id, user=user)
    except Cart.DoesNotExist:
        logger.warning(f"Cart item not found for user {user.email} with ID {cart_id}")
        return Response(
            {"error": "Cart item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Validate updated quantity if provided
    updated_quantity = request.data.get("product_quantity")
    if updated_quantity is not None:
        if not isinstance(updated_quantity, int) or updated_quantity <= 0:
            logger.warning(f"Invalid quantity update for user {user.email}: {updated_quantity}")
            return Response(
                {"error": "Product quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Serialize and update the cart item
    serializer = CartSerializer(cart_item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Cart item with ID {cart_id} updated successfully for user {user.email}")
        return Response(
            {"message": "Cart item updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    logger.warning(f"Cart item update failed for user {user.email}: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# (=================DONE==================)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_id):
    """
    Remove a product from the cart.
    """
    user = request.user
    try:
        # Attempt to fetch the cart item for the logged-in user
        cart_item = Cart.objects.get(id=cart_id, user=user)
        cart_item.delete()
        logger.info(f"Cart item with ID {cart_id} removed for user {user.email}")
        return Response(
            {"message": "Product removed from cart successfully."},
            status=status.HTTP_200_OK,
        )
    except Cart.DoesNotExist:
        logger.warning(f"Cart item not found for user {user.email} with ID {cart_id}")
        return Response(
            {"error": "Cart item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error removing cart item for user {user.email} with ID {cart_id}: {str(e)}")
        return Response(
            {"error": "Failed to remove product from cart. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# ===================================================================================

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils.timezone import now
# from datetime import timedelta
# from .models import Conversation
# from .serializers import ConversationSerializer
# from rest_framework.permissions import IsAuthenticated
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def save_conversation(request):
#     """
#     Save a new conversation for the authenticated user.
#     """
#     conversation_data = request.data.get('conversation_data')
#
#     if not conversation_data:
#         return Response(
#             {"error": "Conversation data is required."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # Create and save the conversation
#     try:
#         conversation = Conversation.objects.create(
#             user=request.user,
#             conversation_data=conversation_data
#         )
#         serializer = ConversationSerializer(conversation)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response(
#             {"error": f"Failed to save conversation: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_conversations(request):
#     """
#     Fetch conversations for the authenticated user, limited to the last 2 days.
#     """
#     try:
#         two_days_ago = now() - timedelta(days=2)
#         conversations = Conversation.objects.filter(
#             user=request.user,
#             timestamp__gte=two_days_ago
#         )
#         serializer = ConversationSerializer(conversations, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response(
#             {"error": f"Failed to fetch conversations: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#
#
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_expired_conversations(request):
#     """
#     Delete conversations older than 2 days for the authenticated user.
#     """
#     try:
#         two_days_ago = now() - timedelta(days=2)
#         expired_conversations = Conversation.objects.filter(
#             user=request.user,
#             timestamp__lt=two_days_ago
#         )
#         count = expired_conversations.count()
#         expired_conversations.delete()
#         return Response(
#             {"message": f"{count} expired conversations deleted."},
#             status=status.HTTP_200_OK
#         )
#     except Exception as e:
#         return Response(
#             {"error": f"Failed to delete expired conversations: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
