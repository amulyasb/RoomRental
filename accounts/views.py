from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.validation import validate_custom_password
from RoomRental import settings
from accounts.models import *
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode



# Create your views here.
def choose_registration(request):
    return render(request, "registration/choose_registration.html")


# customer Registration
def customer_registration(request):
    # fetching city data
    cities = city.objects.all() 

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower()
        phone = request.POST.get("phone")
        city_id = request.POST.get("city")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password == confirm_password:
            # check phone exist or not
            if get_user_model().objects.filter(phone=phone).exists():
                messages.error(request, "Phone Number already taken")
                return redirect("customer_registration")
            
            # Check if the email already exists
            if get_user_model().objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('customer_registration')
            
            if len(phone)!= 10 or not phone.isdigit():
                messages.error(request, "Phone Number must be 10 digits and contain number only")
                return redirect('customer_registration')
            
            # Validate password
            errors = validate_custom_password(password)
            if errors:
                messages.error(request, errors[0])
                return redirect('customer_registration')   
            
            city_obj = city.objects.filter(id=city_id).first() if city_id else None
            
            user = get_user_model().objects.create_user(
                email=email,
                name=name,
                phone = phone,
                city=city_obj,
                password=password,
                user_type='customer',
                is_active=False  

            )
            # Send verification email
            mail_subject = 'Activate your account'
            email_template = 'registration/verification_email.html'
            if send_verification_email(request, user, mail_subject, email_template):
                messages.success(request, "Account created successfully! Please check your email to activate your account.")
                return redirect("customer_registration")

            else:
                user.delete()
                messages.error(request, "Account created but failed to send verification email. Please contact support.")
                return redirect("customer_registration")
        else:
            messages.error(request, "Passwords and Confirm Password need to match!")
            return redirect('customer_registration')

    return render(request, "registration/customer_registration.html", {'cities':cities})


def seller_registration(request):
    # Fetch city data
    cities = city.objects.all()
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower()
        phone = request.POST.get("phone")
        city_id = request.POST.get("city", "")
        photo = request.FILES.get("photo")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        amount = 500
        
        if password != confirm_password:
            messages.error(request, "Passwords and Confirm Password need to match!")
            return redirect('seller_registration')

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone Number already taken")
            return redirect("seller_registration")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("seller_registration")
        
        if len(phone)!= 10 or not phone.isdigit():
            messages.error(request, "Phone Number must be 10 digits and contain number only")
            return redirect('customer_registration')
        
        # Validate password
        errors = validate_custom_password(password)
        if errors:
            messages.error(request, errors[0])
            return redirect('seller_registration')
        
        city_obj = city.objects.filter(id=city_id).first() if city_id else None

        user = User.objects.create_user(
            email=email,
            name=name,
            phone=phone,
            city=city_obj,
            password=password,
            user_type='seller',
            is_active=False,
            is_subscribed=False
        )

        if photo:
            user.user_image = photo
            user.save()

        # Send verification email
        mail_subject = 'Verify your email to complete seller registration'
        email_template = 'registration/verification_email.html'
        if send_verification_email(request, user, mail_subject, email_template):
            messages.success(request, "Verification email sent. Please check your email to complete your seller registration.")
            return redirect("seller_registration")
        else:
            user.delete()
            messages.error(request, "Failed to send verification email. Please try again..")
            return render("seller_registration")
        
    return render(request, "registration/seller_registration.html", {'cities': cities})




# Login user
def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user:
            if user.is_active:

                login(request, user)

                if user.user_type == "seller":
                    return redirect("seller_dashboard")
                elif user.user_type == "customer":
                    return redirect("homepage")
                else:
                    messages.error(request, "Didnt Found Account")
                    return redirect("login_user")
            else:
                messages.error(request, "Your account is not active...")
                return redirect("login_user")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login_user")
                
    return render(request, "registration/login.html")

def logout_user(request):
    logout(request)
    return redirect('homepage')


def send_verification_email(request, user, mail_subject, email_template):
    try:
        current_site = get_current_site(request)
        message = render_to_string(email_template, {
            'user': user,
            'domain': current_site.domain,  # Use domain attribute
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def activate(request , uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.user_type == "customer":
            user.is_active = True
            user.save()
        elif user.user_type == "seller":
            user.is_active = False
            user.save()

        if user.user_type == 'seller':
            # For sellers, store info in session and redirect to payment
            request.session['verified_seller'] = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone': user.phone,
                'city_id': user.city.id if user.city else None,
                'photo': user.user_image.name if user.user_image else None,
                'password': user.password,
            }
            request.session.modified = True
            messages.success(request, 'Email verified! Please complete payment to activate your seller account.')
            return redirect('seller_payment')
        else:
            # For customers, just activate and redirect to login
            messages.success(request, 'Account activated! You can now login.')
            return redirect('login_user')
    else:
        messages.error(request, 'Invalid activation link')
        # Check if user exists before checking user_type
        if user is not None and hasattr(user, 'user_type') and user.user_type == 'seller':
            return redirect('seller_registration')
        else:
            return redirect('customer_registration')
        
