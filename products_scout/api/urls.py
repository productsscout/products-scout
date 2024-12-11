#=================================================DONE===================================================

from django.urls import path
from . import views  # Import views from the `api` app

urlpatterns = [
    # Route to generate a response and optionally fetch products
    path('generate-response/', views.generate_response_view, name='generate_response_view'),

    # Route to fetch products from Amazon using extracted features (if needed for testing independently)
    path('fetch-products/', views.fetch_products, name='fetch_products'),

    # Route to validate if a query or response is product-related (if needed for debugging or testing)
    path('is-product-related/', views.is_product_related, name='is_product_related'),

    path('generate-response-main/', views.generate_response_view_main, name='generate_response_view_main'),

    path('fetch-products-main/', views.fetch_features_and_products_view, name='fetch_features_and_products_view'),

]


# from django.urls import path
# from . import views  # Import views from the `api` app
#
# urlpatterns = [
#     # Route to generate a response using OpenAI's API
#     path('generate-response/', views.generate_response_view, name='generate_response_view'),
#
#     # Route for the main page to generate a response
#     path('generate-response-main/', views.generate_response_view_main, name='generate_response_view_main'),
#
#     # Route to extract features and fetch products for the main page
#     path('fetch-features-and-products/', views.fetch_features_and_products_view, name='fetch_features_and_products_view'),
# ]

