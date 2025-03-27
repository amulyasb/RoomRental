from django.urls import path
from payment import views


urlpatterns = [
    path('renew_subs/', views.renew_subs, name='renew_subs'),
    path('verify_renewal/', views.verify_renewal, name='verify_renewal'),

]