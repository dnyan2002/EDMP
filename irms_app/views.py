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
from .serializers import LocaltoPIDDataSerializer
import requests

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


class LocalDataEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling local data entries
    """
    queryset = LocalData.objects.all()
    serializer_class = LocaltoPIDDataSerializer

    def create(self, request, *args, **kwargs):
        """
        Custom create method to process and redistribute data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the local data entry
        self.perform_create(serializer)
        
        # Process and redistribute data to PID system
        try:
            self.redistribute_data(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # If redistribution fails, still save the original entry
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def redistribute_data(self, data):
    #     """
    #     Redistribute data to PID system or other processing endpoints
    #     """
    #     # Example redistribution to a hypothetical PID data endpoint
    #     pid_endpoint = 'https://your-pid-system-endpoint.com/api/process-data/'
    #     try:
    #         response = requests.post(pid_endpoint, json=data)
    #         response.raise_for_status()
    #     except requests.RequestException as e:
    #         # Log the error or handle as needed
    #         print(f"Failed to redistribute data: {e}")