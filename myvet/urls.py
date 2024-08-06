from django.urls import path
from . import views
from .views import Pets_ApiView, Pet_ApiView, Client_ApiView, Clients_ApiView, Product_ApiView, Products_ApiView, Vaccines_ApiView, Vaccine_ApiView, PetTypes_ApiView, PetType_ApiView, ProductTypes_ApiView, ProductType_ApiView, VaccineTypes_ApiView, VaccineType_ApiView

urlpatterns = [
    path('pets', Pets_ApiView.as_view()),
    path('pet/<int:id>', Pet_ApiView.as_view()),

    path('products', Products_ApiView.as_view()),
    path('product/<int:id>', Product_ApiView.as_view()),

    path('clients', Clients_ApiView.as_view()),
    path('client/<int:id>', Client_ApiView.as_view()),

    path('vaccines', Vaccines_ApiView.as_view()),
    path('vaccine/<int:id>', Vaccine_ApiView.as_view()),

    path('petTypes', PetTypes_ApiView.as_view()),
    path('petType/<int:id>', PetType_ApiView.as_view()),

    path('productTypes', ProductTypes_ApiView.as_view()),
    path('productType/<int:id>', ProductType_ApiView.as_view()),

    path('vaccineTypes', VaccineTypes_ApiView.as_view()),
    path('vaccineType/<int:id>', VaccineType_ApiView.as_view()),

    path('login', views.custom_login),
    path('logout', views.custom_logout),
    path('resetPassword', views.reset_password),
]