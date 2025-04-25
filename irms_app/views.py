import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.urls import reverse
from django.contrib.messages import success
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import matplotlib
matplotlib.use('agg')
from .forms import CustomUserCreationForm
from .models import *
from .permissions import role_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PIDDataSerializer
import logging
from .forms import FeedstockCostForm, PowerCostForm, CBGSaleDispatchForm, FOMSaleDispatchForm, BiogasPlantReportForm
import random
from datetime import datetime

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
    expected_clean_gas = 20
    actual_production = 10

    context = {
        'expected_clean_gas': expected_clean_gas,
        'actual_production': actual_production,
    }
    return render(request, "report.html", context)

@login_required
@role_required(['Admin', 'Manager'])
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # messages.success(request, f'User {user.username} created successfully!')
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

def feedstock_report(request):
    return render(request, 'feedstock_report.html')

def powerconsumption_report(request):
    return render(request, 'powerconsumption_report.html')

def dashboard(request):
    expected_clean_gas = 20
    actual_production = 10

    context = {
        'expected_clean_gas': expected_clean_gas,
        'actual_production': actual_production,
    }
    return render(request, 'dashboard.html', context)
def bagsgenerated_report(request):
    return render(request, 'bags.html')

def biogas_report_json(request):
    reports = BiogasPlantReport.objects.all().order_by('-date')
    
    data = []
    for report in reports:
        data.append({
            'date': report.date,
            'feedstock_used_ton': report.feedstock_used_ton,
            'total_feed_cost': report.total_feed_cost,
            'raw_biogas_produced_nm3': report.raw_biogas_produced_nm3,
            'actual_cbg_production_kg': report.actual_cbg_production_kg,
            'total_power_cost': report.total_power_cost,
            'cbg_sale_dispatch_ton': report.cbg_sale_dispatch_ton,
            'running_time': str(report.running_time),
            'stoppage_time': str(report.stoppage_time),
        })

    return JsonResponse({'reports': data})


def dashboard_view(request):
    return render(request, 'dashboard.html')

def feedstock_report(request):
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')

    selected_info = ""
    feedstock_data = []
    months_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = []

    if year and not date and not month:
        selected_info = f"Selected Year: {year}"
        months = months_full
        for _ in range(12):
            feedstock_data.append(random.randint(1000, 5000))  # Random feedstock values for each month

    elif month and year:
        selected_index = int(month) - 1
        months = [months_full[selected_index]]
        selected_info = f"Selected Month: {months[0]} {year}"
        feedstock_data = [random.randint(200, 800)]  # Random feedstock value for the month

    else:
        months = ['']
        selected_info = f"Selected Date: {date}" if date else "Default Day View"
        feedstock_data = [random.randint(50, 200)]  # Random feedstock value for a day

    years = range(2020, datetime.now().year + 1)

    return render(request, 'feedstock_report.html', {
        'feedstock_data_list': feedstock_data,
        'months': months,
        'years': years,
        'selected_info': selected_info
    })


def cost_entry_view(request):
    feed_form = FeedstockCostForm(prefix='feed')
    power_form = PowerCostForm(prefix='power')
    cbg_form = CBGSaleDispatchForm(prefix='cbg')
    fom_form = FOMSaleDispatchForm(prefix='fom')

    if request.method == 'POST':
        if 'feedstock_submit' in request.POST:
            feed_form = FeedstockCostForm(request.POST, prefix='feed')
            if feed_form.is_valid():
                feed_form.save()
                success(request, message="Form Submitted successfully!")
                return redirect('manual_entry')

        elif 'power_submit' in request.POST:
            power_form = PowerCostForm(request.POST, prefix='power')
            if power_form.is_valid():
                power_form.save()
                return redirect('manual_entry')

        elif 'cbg_submit' in request.POST:
            cbg_form = CBGSaleDispatchForm(request.POST, prefix='cbg')
            if cbg_form.is_valid():
                cbg_form.save()
                return redirect('manual_entry')
        
        elif 'fom_submit' in request.POST:
            fom_form = FOMSaleDispatchForm(request.POST, prefix='fom')
            if fom_form.is_valid():
                fom_form.save()
                return redirect('manual_entry')

    return render(request, 'manual_entry.html', {
        'feed_form': feed_form,
        'power_form': power_form,
        'cbg_form': cbg_form,
        'fom_form': fom_form
    })
