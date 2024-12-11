#=================================================DONE===================================================

from rest_framework import serializers
from .models import User, Cart
from datetime import datetime
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'date_of_birth', 'password',
            'signup_method', 'date_joined', 'is_active', 'terms_accepted'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'date_of_birth': {'required': True},  # Enforce this field as required
            'terms_accepted': {'required': True},  # Enforce this field as required
        }

    def validate_date_of_birth(self, value):
        """
        Ensure the date of birth is valid and not in the future.
        """
        if value > datetime.now().date():
            logger.warning("Invalid date of birth: cannot be in the future.")
            raise serializers.ValidationError("Date of Birth cannot be in the future.")
        return value

    def validate_terms_accepted(self, value):
        """
        Ensure the terms and conditions are accepted.
        """
        if not value:
            logger.warning("Terms and conditions not accepted.")
            raise serializers.ValidationError("You must accept the terms and conditions.")
        return value

    def validate_password(self, value):
        """
        Ensure the password meets minimum security requirements.
        """
        if len(value) < 8:
            logger.warning("Password validation failed: too short.")
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def create(self, validated_data):
        """
        Override create method to hash the password.
        """
        validated_data['password'] = make_password(validated_data['password'])
        logger.info(f"User created with email: {validated_data.get('email')}")
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    """
    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "product_name",
            "product_price",
            "product_quantity",
            "product_star_rating",
            "product_photo",
            "product_url",
            "created_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},  # Prevent user from being set directly
        }

    def validate_product_name(self, value):
        """
        Ensure the product name is not empty or too long.
        """
        if not value.strip():
            logger.warning("Validation failed: product name is empty.")
            raise ValidationError("Product name cannot be empty.")
        if len(value) > 1000:
            logger.warning("Validation failed: product name is too long.")
            raise ValidationError("Product name cannot exceed 1000 characters.")
        return value

    def validate_product_price(self, value):
        """
        Ensure the product price is valid.
        """
        if value <= Decimal(0):
            logger.warning("Validation failed: product price is invalid.")
            raise ValidationError("Product price must be greater than zero.")
        return value

    def validate_product_quantity(self, value):
        """
        Ensure the product quantity is a positive integer.
        """
        if value < 1:
            logger.warning("Validation failed: product quantity is invalid.")
            raise ValidationError("Product quantity must be at least 1.")
        return value

    def create(self, validated_data):
        """
        Override create method to set the user field.
        """
        user = self.context["request"].user  # Get the logged-in user from the context
        validated_data["user"] = user  # Add user to validated_data
        logger.info(f"Cart item created for user: {user.email}, product: {validated_data['product_name']}")
        return Cart.objects.create(**validated_data)
