# urls.py

from django.urls import path
from .views import ConfirmPaymentView

urlpatterns = [
    path('confirm_payment/', ConfirmPaymentView.as_view()),
]