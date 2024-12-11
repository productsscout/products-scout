#=================================================DONE===================================================

from django.urls import path
from .views import (
    register_user,
    check_email,
    verify_email,
    forgot_password,
    resend_verification_email,
    verify_code,
    reset_password,
    check_user,
    check_password,
    # login_user,
    logout_user,
    user_first_name,
    get_user_profile,
    update_user_profile,
    generate_tokens,
    user_email,
    add_to_cart,
    get_cart_items,
    update_cart_item,
    remove_from_cart,
    # save_conversation,
    # get_conversations,
    # delete_expired_conversations,
)

urlpatterns = [
    # Authentication & Registration
    path('register/', register_user, name='register_user'),
    path('check-email/', check_email, name='check_email'),
    path('verify-email/<str:code>/', verify_email, name='verify_email'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('resend-verification-email/', resend_verification_email, name='resend_verification_email'),
    path('verify-code/', verify_code, name='verify_code'),
    path('reset-password/', reset_password, name='reset_password'),
    path('check-user/', check_user, name='check_user'),
    path('check-password/', check_password, name='check_password'),
    # path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('generate-tokens/', generate_tokens, name='generate_tokens'),

    # User Details
    path('user-email/', user_email, name='user_email'),
    path('user-first-name/', user_first_name, name='user_first_name'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('profile-update/', update_user_profile, name='update_user_profile'),

    # Cart Management
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', get_cart_items, name='get_cart_items'),
    path('cart/update/<int:cart_id>/', update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),

    # # Conversations (if implemented)
    # path('conversation/save/', save_conversation, name='save_conversation'),
    # path('conversation/', get_conversations, name='get_conversations'),
    # path('conversation/delete-expired/', delete_expired_conversations, name='delete_expired_conversations'),
]

handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"

