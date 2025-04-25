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
    # Get filter parameters
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    shift = request.GET.get('shift')
    
    # Initialize variables
    report_data = []
    feedstock_data = []
    feedstock_cost_data = []
    biogas_data = []
    co2_data = []
    labels = []
    selected_info = ""
    
    # Initialize query
    query = BiogasPlantReport.objects.all()
    
    # Apply filters
    if date:
        # Filter by specific date
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(date=selected_date)
        labels = [selected_date.strftime('%d %b %Y')]
        selected_info = f"Selected Date: {selected_date.strftime('%d %b %Y')}"
    elif month and year:
        # Filter by month and year
        query = query.filter(date__year=year, date__month=month)
        month_name = datetime(int(year), int(month), 1).strftime('%B')
        labels = [month_name]
        selected_info = f"Selected Month: {month_name} {year}"
    elif year:
        # Filter by year
        query = query.filter(date__year=year)
        # Group by month for year view
        months_data = {}
        for i in range(1, 13):
            months_data[i] = {'feedstock': 0, 'cost': 0, 'biogas': 0, 'co2': 0, 'count': 0}
        
        for report in query:
            month_num = report.date.month
            months_data[month_num]['feedstock'] += report.feedstock_used_ton
            months_data[month_num]['cost'] += report.total_feed_cost
            months_data[month_num]['biogas'] += report.raw_biogas_produced_nm3
            months_data[month_num]['co2'] += report.co2_savings_mt
            months_data[month_num]['count'] += 1
        
        # Create arrays for chart data
        months_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        labels = months_full
        
        for i in range(1, 13):
            if months_data[i]['count'] > 0:
                # Calculate averages if there are multiple entries per month
                feedstock_data.append(months_data[i]['feedstock'] / months_data[i]['count'])
                feedstock_cost_data.append(months_data[i]['cost'] / months_data[i]['count'])
                biogas_data.append(months_data[i]['biogas'] / months_data[i]['count'])
                co2_data.append(months_data[i]['co2'] / months_data[i]['count'])
            else:
                feedstock_data.append(0)
                feedstock_cost_data.append(0)
                biogas_data.append(0)
                co2_data.append(0)
        
        selected_info = f"Selected Year: {year}"
    else:
        # Default to current day if no filters selected
        today = datetime.now().date()
        query = query.filter(date=today)
        labels = [today.strftime('%d %b %Y')]
        selected_info = "Today's Report"
    
    # Apply shift filter if provided
    if shift:
        query = query.filter(shift=shift)
    
    # If we haven't populated data arrays yet (for date or month+year filters)
    if not feedstock_data:
        for report in query:
            report_data.append({
                'highest_value': report.raw_biogas_produced_nm3,
                'filter_no': report.power_consumption_kwh,
                'shift': report.shift,
                'date': report.date.strftime('%Y-%m-%d')
            })
            
            feedstock_data.append(report.feedstock_used_ton)
            feedstock_cost_data.append(report.total_feed_cost)
            biogas_data.append(report.raw_biogas_produced_nm3)
            co2_data.append(report.co2_savings_mt)
    
    # Get years for dropdown
    years = BiogasPlantReport.objects.dates('date', 'year').values_list('date__year', flat=True).distinct()
    years = sorted(years)
    
    # Get shifts for dropdown
    shifts = BiogasPlantReport.objects.values('shift').distinct()
    
    # Prepare chart data
    chart_data = {
        'feedstock': {
            'labels': labels,
            'feedstock_used': feedstock_data,
            'feedstock_cost': feedstock_cost_data
        },
        'biogas': {
            'labels': labels,
            'biogas_produced': biogas_data,
            'co2_savings': co2_data
        }
    }
    
    return render(request, 'feedstock_report.html', {
        'report_data': report_data,
        'chart_data': chart_data,
        'years': years,
        'shifts': shifts,
        'selected_info': selected_info,
        'selected_shift': shift
    })
from django.shortcuts import render, redirect
from .forms import FeedstockCostForm, PowerCostForm, CBGSaleDispatchForm

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

def report_list(request):
    # Start with all reports
    reports_query = BiogasPlantReport.objects.all()
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        reports_query = reports_query.filter(date=date_filter)
    
    # Filter by month and year if provided
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        reports_query = reports_query.filter(date__month=month, date__year=year)
    
    # Filter by shift if provided
    shift = request.GET.get('shift')
    if shift:
        # Assuming you have a shift field in your model or a related model
        # Modify this based on your actual model structure
        reports_query = reports_query.filter(shift=shift)
    
    # Order by date descending
    reports = reports_query.order_by('-date')
    
    # Default values for charts
    expected_clean_gas_percentage = 0
    actual_production_percentage = 0
    
    # Calculate data for charts based on filtered reports
    if reports.exists():
        # Calculate totals for all filtered reports
        total_expected_clean_gas = sum(report.expected_clean_gas_nm3 for report in reports)
        total_actual_clean_gas = sum(report.actual_clean_gas_nm3 for report in reports)
        
        total_expected_production = sum(report.expected_production_kg for report in reports)
        total_actual_production = sum(report.actual_cbg_production_kg for report in reports)
        
        # Calculate percentages
        if total_expected_clean_gas > 0:
            expected_clean_gas_percentage = (total_actual_clean_gas / total_expected_clean_gas) * 100
            expected_clean_gas_percentage = round(expected_clean_gas_percentage, 2)
        
        if total_expected_production > 0:
            actual_production_percentage = (total_actual_production / total_expected_production) * 100
            actual_production_percentage = round(actual_production_percentage, 2)
    
    # Get unique years for the year dropdown
    years = BiogasPlantReport.objects.dates('date', 'year')
    years = [date.year for date in years]
    
    # Define shifts (you might have a Shift model, but this is a simple example)
    shifts = [
        {'shift_name': 'General Shift'},
        {'shift_name': 'Night Shift'}
    ]
    
    context = {
        'reports': reports,
        'expected_clean_gas': expected_clean_gas_percentage,
        'actual_production': actual_production_percentage,
        'years': years,
        'shifts': shifts,
        'selected_shift': shift or ''
    }
    
    return render(request, 'report.html', context)