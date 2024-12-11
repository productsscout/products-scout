#=================================================DONE===================================================

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.crypto import get_random_string
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with additional fields and methods for verification and reset.
    """
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, db_index=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # Optional DOB
    signup_method = models.CharField(
        max_length=20,
        choices=[
            ("email", "Email"),
            ("google", "Google"),
            ("microsoft", "Microsoft"),
        ],
        default="email",
    )
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)  # Requires email verification
    terms_accepted = models.BooleanField(default=False)

    # Fields for email verification
    verification_code = models.CharField(max_length=32, blank=True, null=True)
    verification_code_expiry = models.DateTimeField(blank=True, null=True)

    # Fields for password reset
    password_reset_code = models.CharField(max_length=6, blank=True, null=True)
    password_reset_code_expiry = models.DateTimeField(blank=True, null=True)

    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    # Helper Methods
    def set_verification_code(self):
        """
        Generate and set a new verification code with expiry.
        """
        self.verification_code = get_random_string(length=32)
        self.verification_code_expiry = timezone.now() + timedelta(hours=24)  # Valid for 24 hours
        self.save()
        logger.info(f"Verification code set for user {self.email}")

    def is_verification_code_valid(self):
        """
        Check if the verification code is valid.
        """
        valid = self.verification_code_expiry and timezone.now() <= self.verification_code_expiry
        if not valid:
            logger.warning(f"Verification code expired for user {self.email}")
        return valid

    def set_password_reset_code(self):
        """
        Generate and set a new password reset code with expiry.
        """
        self.password_reset_code = get_random_string(length=6)
        self.password_reset_code_expiry = timezone.now() + timedelta(minutes=2)  # Valid for 15 minutes
        self.save()
        logger.info(f"Password reset code set for user {self.email}")

    def is_password_reset_code_valid(self):
        """
        Check if the password reset code is valid.
        """
        valid = self.password_reset_code_expiry and timezone.now() <= self.password_reset_code_expiry
        if not valid:
            logger.warning(f"Password reset code expired for user {self.email}")
        return valid


class Cart(models.Model):
    """
    Model for storing items in a user's cart.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items"
    )
    product_name = models.CharField(max_length=1000)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.PositiveIntegerField(default=1)
    product_star_rating = models.FloatField(null=True, blank=True)  # Optional star rating
    product_photo = models.URLField(null=True, blank=True)  # Optional product image URL
    product_url = models.URLField(null=True, blank=True)  # Optional product page URL
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} (User: {self.user.email})"

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ["-created_at"]
