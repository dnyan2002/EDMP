import io
import json
import base64
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from django.urls import reverse
from django.views import View
from django.db import connection
from django.contrib.auth.decorators import login_required
from datetime import datetime
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from django.http import JsonResponse
from django.db.models import Max
from .forms import LoginForm
from .models import User

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('leakapp_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


def home(request):
    return render(request, 'home.html')

def report(request):
    return render(request, "report.html")

def user_register(request):
    return render(request, "user.html")