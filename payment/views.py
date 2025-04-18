import requests
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from accounts.models import User, city
from payment.models import Subscription, Payment
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from payment.models import Subscription, Payment
import uuid
import json
from django.urls import reverse
from django.core.files.storage import default_storage




def seller_payment(request):
    if 'verified_seller' not in request.session:
        messages.error(request, "Please complete registration and email verification first.")
        return redirect('seller_registration')
    else:
        user_data = request.session['verified_seller']
        amount = 500

        if request.method == "POST":
            purchase_order_id = str(uuid.uuid4())  # Generate a unique ID

            url = "https://dev.khalti.com/api/v2/epayment/initiate/"

            payload = json.dumps({
                "return_url": "http://127.0.0.1:8000/verify",
                "website_url": "http://127.0.0.1:8000/",
                "amount": amount * 100,
                "purchase_order_id": purchase_order_id,
                "purchase_order_name": "Seller Subscription",
                "customer_info": {
                    "name": user_data.get('name'),
                    "email": user_data.get('email'),
                    "phone": user_data.get('phone'),
                }

            })
            headers = {
                'Authorization': 'key 4f4e21dc08e64b358065d5ac50ab8163',
                'Content-Type': 'application/json',
            }
            response = requests.post(url, headers=headers, data=payload)
            print(response.text)
            response_data = response.json()

            print("khalti api response:", response_data)
            print(response.status_code)

            if response.status_code == 200:
                request.session['payment_user_id'] = user_data['id']
                return redirect(response_data['payment_url'])
            else:
                messages.error(request, "Payment initialization failed. Please try again.")
                return redirect('seller_payment')
    
    return render(request, "seller_payment.html", {'amount': amount})



# For Verifying Payment and Create Seller
def verify_payment(request):
    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/" 
    
    if request.method == 'GET':
        headers = {
            'Authorization': 'key 4f4e21dc08e64b358065d5ac50ab8163',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        if not pidx:
            messages.error(request, "Payment Cancled")
            return redirect('seller_payment')

        data = json.dumps({
            'pidx': pidx
        })
        response = requests.post(lookup_url, headers=headers, data=data)
        print(response.text)

        new_response = json.loads(response.text)
        print(new_response)

        transaction_id = new_response.get('transaction_id', 'unkown transaction')
        print("transaction_id:", transaction_id)
        print(response.status_code)

        # if response.status_code == 200:
        if new_response['status'] == 'Completed':
            user_id = request.session.get('payment_user_id')
            print(user_id)
            if not user_id:
                messages.error(request, "Session expired. Try again.")
                return redirect('seller_registration')
            try:
                user = User.objects.get(id=user_id)

                start_date = datetime.now()
                end_date = start_date + timedelta(days=30)
                    
                user.is_subscribed=True
                user.is_active=True
                user.subscription_end_date=end_date

                Subscription.objects.create(
                    seller=user, 
                    transaction_id=transaction_id,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )

                payment_date = datetime.now()
                Payment.objects.create(
                    seller=user, 
                    amount = int(new_response.get('total_amount')) // 100,
                    transaction_id=transaction_id,
                    payment_date=payment_date,
                    status='success',
                    payment_title='Account Created'
                )
                user.save()
                # Clean up session
                if 'verified_seller' in request.session:
                    del request.session['verified_seller']
                if 'payment_user_id' in request.session:
                    del request.session['payment_user_id']

                messages.success(request, "Payment Successful! Your seller account is now active.")
                return redirect("login_user")
            except User.DoesNotExist:
                messages.error(request, "User not found. Please register again.")
                return redirect('seller_registration')
        else:
            messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
            return redirect('seller_payment')
        



def renew_subs(request):
    # Fetch city data
    cities = city.objects.all()
    if request.method == "POST":
        amount = 300
        # generate unique purchase id
        purchase_order_id = str(uuid.uuid4())

        url = "https://dev.khalti.com/api/v2/epayment/initiate/"

        payload = json.dumps({
            "return_url": "http://127.0.0.1:8000/verify_renewal",
            "website_url": "http://127.0.0.1:8000/",
            "amount": amount*100,   
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Seller Subscription Renewal",
        })

        headers = {
            'Authorization': 'key 4f4e21dc08e64b358065d5ac50ab8163',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, data=payload)
        print(response.text)

        # Store renewal intent in session
        request.session['renewal_info'] = {
            'seller_id': request.user.id,
            'purchase_order_id': purchase_order_id
        }

        if response.status_code == 200:
            response_data = response.json()
            return redirect(response_data['payment_url'])
        else:
            messages.error(request, "Payment Fail Status Code not 200!!. Please try again.")
            return redirect('seller_dashboard') 


# verify renew subscription
def verify_renewal(request):

    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/" 

    if request.method == 'GET':
        headers = {
            'Authorization': 'key 4f4e21dc08e64b358065d5ac50ab8163',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        if not pidx:
            messages.error(request, "Payment Cancled")
            return redirect("seller_dashboard")
        
        data = json.dumps({
            'pidx': pidx
        })
        response = requests.post(lookup_url, headers=headers, data=data)
        new_response = json.loads(response.text)

        transaction_id = new_response.get('transaction_id', 'unkown transaction')

        if new_response['status'] == 'Completed':
            renewal_info = request.session.get('renewal_info')
            print(renewal_info)
            if not renewal_info:
                messages.error(request, "Session expired. Try again.")
                return redirect('seller_dashboard') 
            
            seller = request.user
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)

            # Update subscription
            seller.is_subscribed = True
            seller.subscription_end_date = end_date
            seller.save()

            # Create Subscription records
            Subscription.objects.create(
                seller=seller, 
                transaction_id=transaction_id,
                start_date=start_date,
                end_date = end_date,
                is_active=True
            )
            payment_date = datetime.now()
            Payment.objects.create(
                seller=seller,
                amount = int(new_response.get('total_amount')) // 100,
                transaction_id=transaction_id,
                payment_date = payment_date,
                status='success',
                payment_title='Renew Subscription'
            )
            seller.save()
            messages.success(request, "Renew Account Successful.. Thank You")
            return redirect('seller_dashboard') 
        else:
            messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
            return redirect('seller_dashboard') 
    else:
        messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
        return redirect('seller_dashboard') 














