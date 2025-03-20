import requests
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from accounts.models import User, city
from payment.models import Subscription, Payment
from datetime import datetime, timedelta


