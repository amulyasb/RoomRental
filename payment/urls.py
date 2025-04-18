from django.urls import path
from payment import views


urlpatterns = [
    path('seller_payment/', views.seller_payment, name='seller_payment'),
    path("verify/", views.verify_payment, name="verify_payment"),

    path('renew_subs/', views.renew_subs, name='renew_subs'),
    path('verify_renewal/', views.verify_renewal, name='verify_renewal'),

]