from django.urls import path
from accounts import views


urlpatterns = [
    path("choose_registration/", views.choose_registration, name="choose_registration"),
    path("customer_registration/", views.customer_registration, name="customer_registration"),
    path("seller_registration/", views.seller_registration, name="seller_registration"),
    path("login/", views.login_user, name="login_user"),
    path("logout/", views.logout_user, name="logout_user"),
    path("verify/", views.verify_payment, name="verify_payment"),
    

]