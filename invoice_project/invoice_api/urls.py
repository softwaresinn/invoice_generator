from django.urls import path
from .views import generate_invoice,invoice_form_view

urlpatterns = [
    path('', invoice_form_view, name='invoice-form'),
    path("generate-invoice/", generate_invoice, name='generate-invoice'),

]
