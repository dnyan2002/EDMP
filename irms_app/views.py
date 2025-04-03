import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import matplotlib
matplotlib.use('agg')
from .forms import CustomUserCreationForm
from .models import *
from .permissions import role_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PIDDataSerializer


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


def home(request):
    latest_data = PIDData.objects.last()
    
    context = {
        "data":latest_data
    }
    return render(request, 'home.html', context)

def pid_data(request):
    latest_data = PIDData.objects.last()
    context = {
        "data":latest_data
    }
    return render(request, 'pid_data.html', context)

def report(request):
    return render(request, "report.html")

@login_required
@role_required(['Admin', 'Manager'])
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'User {user.username} created successfully!')
                return redirect('create_user')  # Redirect back to the same page
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
    else:
        form = CustomUserCreationForm()
    
    # Fetch all users to display in the list
    users = CustomUser.objects.all()
    
    return render(request, 'user.html', {
        'form': form, 
        'users': users
    })

import logging

logger = logging.getLogger(__name__)

class PIDDataViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for directly handling PID data.
    """
    queryset = PIDData.objects.all()
    serializer_class = PIDDataSerializer

    def create(self, request, *args, **kwargs):
        """
        Custom create method to receive and process PID data directly.
        """
        logger.info(f"Received API Data: {request.data}")  # Log incoming data

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("PID Data successfully stored")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"PID Data validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
