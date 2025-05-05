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
from .serializers import PIDDataSerializer, ReportSerializer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
import logging
from .forms import FeedstockCostForm, PowerCostForm, CBGSaleDispatchForm, FOMSaleDispatchForm, BiogasPlantReportForm
import random
from datetime import datetime
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


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

# def powerconsumption_report(request):
#     return render(request, 'powerconsumption_report.html')

from django.shortcuts import render
from django.db.models import Sum, Avg
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import BiogasPlantReport

def powerconsumption_report(request):
    # Initialize the context dictionary
    context = {}
    
    # Get date filter parameters
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    shift = request.GET.get('shift')
    filter_type = request.GET.get('filter_type')
    
    # Base queryset
    queryset = BiogasPlantReport.objects.all()
    
    # Apply filters if provided
    if date:
        queryset = queryset.filter(date=date)
    elif month and year:
        queryset = queryset.filter(date__month=month, date__year=year)
    elif year:
        queryset = queryset.filter(date__year=year)
    
    if shift:
        queryset = queryset.filter(shift=shift)
    
    # Get available years for the dropdown
    all_years = BiogasPlantReport.objects.dates('date', 'year')
    years = [date.year for date in all_years]
    
    # Get report data based on filtered queryset
    report_data = queryset.order_by('-date')
    
    # Calculate power and production metrics for charts
    monthly_data = []
    hourly_data = []
    
    if filter_type == 'day' and date:
        # Get hourly data for the selected day
        day_reports = queryset.filter(date=date).order_by('date')
        for report in day_reports:
            hourly_data.append({
                'hour': report.date.strftime('%H:00'),
                'bags': report.fom_bag_count,
                'power_consumption': report.power_consumption_kwh,
                'power_cost': report.total_power_cost
            })
    else:
        # Get monthly data for charts
        current_year = datetime.now().year if not year else int(year)
        for month_num in range(1, 13):
            monthly_report = queryset.filter(
                date__year=current_year, 
                date__month=month_num
            ).aggregate(
                avg_power=Avg('power_consumption_kwh'),
                avg_cost=Avg('total_power_cost'),
                total_bags=Sum('fom_bag_count')
            )
            
            if monthly_report['avg_power'] is not None:
                month_name = datetime(current_year, month_num, 1).strftime('%B')
                monthly_data.append({
                    'month': month_name,
                    'power_consumption': monthly_report['avg_power'],
                    'power_cost': monthly_report['avg_cost'],
                    'total_bags': monthly_report['total_bags'] or 0
                })
    
    # Calculate hourly bag production for the selected date (if available)
    if not hourly_data and date:
        # Simulate hourly data if not available
        for hour in range(24):
            hourly_data.append({
                'hour': f"{hour:02d}:00",
                'bags': 0
            })
    
    context = {
        'report_data': report_data,
        'years': years,
        'selected_shift': shift,
        'monthly_data': monthly_data,
        'hourly_data': hourly_data,
    }
    
    return render(request, 'powerconsumption_report.html', context)

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


# views.py
from django.shortcuts import render
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
import json
from .models import BiogasPlantReport

def dashboard(request):
    # Get the current hour
    now = timezone.now()
    start_of_hour = now.replace(minute=0, second=0, microsecond=0)
    
    # Try to get the current hour's report
    current_report = BiogasPlantReport.objects.filter(
        date=start_of_hour.date(),
        running_time__gte=timedelta(hours=start_of_hour.hour),
        running_time__lt=timedelta(hours=start_of_hour.hour+1)
    ).first()
    
    # If no report exists for current hour, get the most recent one
    if not current_report:
        current_report = BiogasPlantReport.objects.order_by('-date', '-running_time').first()
    
    # Get the last 6 reports for the chart data (up to 1 hour in 10-minute intervals)
    recent_reports = BiogasPlantReport.objects.order_by('-date', '-running_time')[:6]
    
    # Format data for charts
    biogas_data = []
    co2_data = []
    time_labels = []
    
    # Reverse to get chronological order
    for report in reversed(list(recent_reports)):
        # Calculate the approximate biogas production for 10 minutes (1/6 of hourly)
        biogas_value = round(report.raw_biogas_produced_nm3)
        biogas_data.append(biogas_value)
        
        # Calculate CO2 savings for 10 minutes (1/6 of hourly)
        co2_value = round(report.co2_savings_mt)
        co2_data.append(co2_value)

        total_seconds = report.running_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_labels.append(f"{hours}:{minutes:02d}")

        # Calculate running hours and stoppage hours (as float)
    if current_report:
        running_hours = current_report.running_time.total_seconds() / 3600
        stoppage_hours = current_report.stoppage_time.total_seconds() / 3600

        
        # Convert feedstock data to hourly
        hourly_feedstock = current_report.feedstock_used_ton
        hourly_feedstock_cost = current_report.total_feed_cost
        
        # Calculate hourly values
        context = {
            'expected_clean_gas': current_report.expected_clean_gas_nm3,
            'actual_clean_gas': current_report.actual_clean_gas_nm3,
            'expected_production': current_report.expected_production_kg,  # Convert to tons
            'actual_cbg_production': current_report.actual_cbg_production_kg,  # Convert to tons
            'hourly_feedstock': hourly_feedstock,
            'feedstock_cost': hourly_feedstock_cost,
            'hourly_raw_biogas': current_report.raw_biogas_produced_nm3,
            'hourly_co2_savings': current_report.co2_savings_mt,
            'power_consumption': current_report.power_consumption_kwh,
            'power_cost': current_report.total_power_cost,
            'fom_bags': current_report.fom_bag_count,
            'running_hours': running_hours,
            'stoppage_hours': stoppage_hours,
            'biogas_chart_data': json.dumps(biogas_data),
            'co2_chart_data': json.dumps(co2_data),
            'time_labels': json.dumps(time_labels),
        }
    else:
        # Default values if no report exists
        context = {
            'expected_clean_gas': 0,
            'actual_clean_gas': 0,
            'expected_production': 0,
            'actual_cbg_production': 0,
            'hourly_feedstock': 0,
            'feedstock_cost': 0,
            'hourly_raw_biogas': 0,
            'hourly_co2_savings': 0,
            'power_consumption': 0,
            'power_cost': 0,
            'fom_bags': 0,
            'running_hours': 0,
            'stoppage_hours': 0,
            'biogas_chart_data': json.dumps([0, 0, 0, 0, 0, 0]),
            'co2_chart_data': json.dumps([0, 0, 0, 0, 0, 0]),
            'time_labels': json.dumps(['0:00', '0:10', '0:20', '0:30', '0:40', '0:50']),
        }
    
    return render(request, 'dashboard.html', context)

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
    # report_data.append({
    #     'date': report.date.strftime('%Y-%m-%d'),
    #     'feedstock_used_ton': report.feedstock_used_ton,
    #     'total_feed_cost': report.total_feed_cost,
    #     'raw_biogas_produced_nm3': report.raw_biogas_produced_nm3,
    #     'co2_savings_mt': report.co2_savings_mt
    # })

    return render(request, 'feedstock_report.html', {
        # 'report_data': report_data,
        'report_data': query,
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

    feedstock_entries = FeedstockCost.objects.all().order_by('-date_recorded')[:5]
    power_entries = PowerCost.objects.all().order_by('-date_recorded')[:5]
    cbg_entries = CBGSaleDispatch.objects.all().order_by('-date_recorded')[:5]
    fom_entries = FOMSaleDispatch.objects.all().order_by('-date_recorded')[:5]
    
    context = {
        'feed_form': feed_form,
        'power_form': power_form,
        'cbg_form': cbg_form,
        'fom_form': fom_form,
        'feedstock_entries': feedstock_entries,
        'power_entries': power_entries,
        'cbg_entries': cbg_entries,
        'fom_entries': fom_entries,
    }
    
    return render(request, 'manual_entry.html', context)

def report(request):
    # Start with all reports
    reports_query = BiogasPlantReport.objects.all()
    print(reports_query)
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
        reports_query = reports_query.filter(shift=shift)
    
    # Order by date descending
    reports = reports_query.order_by('-date')
    print(reports)
    # Default values for charts
    expected_clean_gas_percentage = 0
    actual_production_percentage = 0
    
    # Calculate data for charts based on filtered reports
    if reports.exists():
        print(reports)
        # Calculate totals for all filtered reports
        total_expected_clean_gas = sum(report.expected_clean_gas_nm3 or 0 for report in reports)
        total_actual_clean_gas = sum(report.actual_clean_gas_nm3 or 0 for report in reports)
        
        total_expected_production = sum(report.expected_production_kg or 0 for report in reports)
        total_actual_production = sum(report.actual_cbg_production_kg or 0 for report in reports)
        
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
    
    # Get shifts from model choices
    shifts = [
        {'shift_name': 'General Shift'},
        {'shift_name': 'Night Shift'}
    ]
    
    # Calculate additional aggregated data for display
    total_feedstock = sum(report.feedstock_used_ton or 0 for report in reports)
    total_feed_cost = sum(report.total_feed_cost or 0 for report in reports)
    total_raw_biogas = sum(report.raw_biogas_produced_nm3 or 0 for report in reports)
    total_power_consumption = sum(report.power_consumption_kwh or 0 for report in reports)
    total_power_cost = sum(report.total_power_cost or 0 for report in reports)
    total_co2_savings = sum(report.co2_savings_mt or 0 for report in reports)
    total_cbg_dispatch = sum(report.cbg_sale_dispatch_ton or 0 for report in reports)
    
    context = {
        'reports': reports,
        'expected_clean_gas': expected_clean_gas_percentage,
        'actual_production': actual_production_percentage,
        'years': years,
        'shifts': shifts,
        'selected_shift': shift or '',
        'total_feedstock': round(total_feedstock, 2),
        'total_feed_cost': round(total_feed_cost, 2),
        'total_raw_biogas': round(total_raw_biogas, 2),
        'total_power_consumption': round(total_power_consumption, 2),
        'total_power_cost': round(total_power_cost, 2),
        'total_co2_savings': round(total_co2_savings, 2),
        'total_cbg_dispatch': round(total_cbg_dispatch, 2),
    }
    
    return render(request, 'report.html', context)

from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, fields, Avg
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime, timedelta
import calendar
from .models import BiogasPlantReport


def running_hours(request):
    # Get the current year and past 5 years for the dropdown
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 1)
    
    # Initialize filter variables
    date_filter = None
    month_filter = None
    year_filter = None
    shift_filter = None
    filter_type = request.GET.get('filter_type', 'day')  # Default to day view
    
    # Process filter parameters
    if 'date' in request.GET and request.GET['date']:
        date_filter = request.GET['date']
        queryset = BiogasPlantReport.objects.filter(date=date_filter)
    elif 'month' in request.GET and request.GET['month'] and 'year' in request.GET and request.GET['year']:
        month_filter = int(request.GET['month'])
        year_filter = int(request.GET['year'])
        queryset = BiogasPlantReport.objects.filter(
            date__month=month_filter,
            date__year=year_filter
        )
    else:
        # Default to current month if no filters applied
        today = datetime.now()
        queryset = BiogasPlantReport.objects.filter(
            date__month=today.month,
            date__year=today.year
        )
    
    # Apply shift filter if provided
    if 'shift' in request.GET and request.GET['shift']:
        shift_filter = request.GET['shift']
        queryset = queryset.filter(shift=shift_filter)
    
    # Process data based on filter type (day or month)
    if filter_type == 'month':
        # For monthly view, aggregate data by month
        if month_filter and year_filter:
            report_data = process_monthly_data(queryset, month_filter, year_filter)
        else:
            today = datetime.now()
            report_data = process_monthly_data(queryset, today.month, today.year)
    else:
        # For daily view, process individual entries
        report_data = process_daily_data(queryset)
    
    # Calculate chart data - aggregate running and stoppage hours
    chart_data = calculate_chart_data(queryset)
    
    context = {
        'years': years,
        'report_data': report_data,
        'selected_shift': shift_filter,
        'running_hours': chart_data['running_hours'],
        'stoppage_hours': chart_data['stoppage_hours'],
    }
    
    return render(request, 'Runninghours.html', context)


def process_daily_data(queryset):
    """Process data for daily view"""
    report_data = []
    
    for report in queryset:
        # Convert DurationField to hours for display
        running_hours = round(report.running_time.total_seconds() / 3600, 2)
        stoppage_hours = round(report.stoppage_time.total_seconds() / 3600, 2)
        
        report_data.append({
            'date': report.date,
            'shift': report.shift,
            'running_hours': running_hours,
            'stoppage_hours': stoppage_hours,
            'feedstock_used': report.feedstock_used_ton,
            'raw_biogas': report.raw_biogas_produced_nm3,
            'clean_gas': report.actual_clean_gas_nm3,
            'cbg_production': report.actual_cbg_production_kg,
            'gas_purity': report.gas_purity_percent,
            'power_consumption': report.power_consumption_kwh,
            'power_cost': report.total_power_cost,
            'co2_savings': report.co2_savings_mt,
            'bags_count': report.fom_bag_count
        })
    
    return report_data


def process_monthly_data(queryset, month, year):
    """Aggregate data by month"""
    # Get number of days in the month
    days_in_month = calendar.monthrange(year, month)[1]
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, days_in_month)
    
    # Aggregate data for the month
    monthly_data = queryset.aggregate(
        total_feedstock=Sum('feedstock_used_ton'),
        total_raw_biogas=Sum('raw_biogas_produced_nm3'),
        total_clean_gas=Sum('actual_clean_gas_nm3'),
        total_cbg_production=Sum('actual_cbg_production_kg'),
        avg_gas_purity=Avg('gas_purity_percent'),
        total_power_consumption=Sum('power_consumption_kwh'),
        total_power_cost=Sum('total_power_cost'),
        total_co2_savings=Sum('co2_savings_mt'),
        total_bags=Sum('fom_bag_count'),
    )
    
    # Calculate total running and stoppage hours for the month
    total_running_seconds = sum(report.running_time.total_seconds() for report in queryset)
    total_stoppage_seconds = sum(report.stoppage_time.total_seconds() for report in queryset)
    
    # Convert seconds to hours
    total_running_hours = round(total_running_seconds / 3600, 2)
    total_stoppage_hours = round(total_stoppage_seconds / 3600, 2)
    
    # Format for display with month name
    month_name = calendar.month_name[month]
    
    return [{
        'date': f"{month_name} {year}",
        'shift': 'Monthly Summary',
        'running_hours': total_running_hours,
        'stoppage_hours': total_stoppage_hours,
        'feedstock_used': monthly_data['total_feedstock'] or 0,
        'raw_biogas': monthly_data['total_raw_biogas'] or 0,
        'clean_gas': monthly_data['total_clean_gas'] or 0,
        'cbg_production': monthly_data['total_cbg_production'] or 0,
        'gas_purity': monthly_data['avg_gas_purity'] or 0,
        'power_consumption': monthly_data['total_power_consumption'] or 0,
        'power_cost': monthly_data['total_power_cost'] or 0,
        'co2_savings': monthly_data['total_co2_savings'] or 0,
        'bags_count': monthly_data['total_bags'] or 0
    }]


def calculate_chart_data(queryset):
    """Calculate data for the running vs stoppage chart"""
    # Calculate total running and stoppage hours
    total_running_seconds = sum(report.running_time.total_seconds() for report in queryset)
    total_stoppage_seconds = sum(report.stoppage_time.total_seconds() for report in queryset)
    
    # Convert seconds to hours (rounded to 2 decimal places)
    running_hours = round(total_running_seconds / 3600, 2)
    stoppage_hours = round(total_stoppage_seconds / 3600, 2)
    
    return {
        'running_hours': running_hours,
        'stoppage_hours': stoppage_hours
    }

class ReportViewset(ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    queryset = BiogasPlantReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['date', 'shift']
    filterset_fields = ['date', 'shift']
    ordering_fields = ['date', 'shift']
    # def get_queryset(self):
    #     queryset = BiogasPlantReport.objects.all()
    #     date = self.kwargs['date']
    #     if date is not None:
    #         queryset = queryset.filter(date__in=date)
    #     return queryset
