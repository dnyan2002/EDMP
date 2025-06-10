import json
import calendar
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from django.urls import reverse
from django.contrib.messages import success
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .permissions import role_required
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .serializers import PIDDataSerializer, ReportSerializer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
import logging
from collections import defaultdict
from .forms import *
from datetime import datetime
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Max, Min, Count
from datetime import datetime, timedelta, date
from django.utils import timezone


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


class DataWrapper:
    """Wrapper class to handle data display logic with formatting"""
    def __init__(self, data, is_recent):
        self._data = data
        self._is_recent = is_recent
    
    def __getattr__(self, name):
        if not self._is_recent:
            return "?"
        
        if self._data and hasattr(self._data, name):
            value = getattr(self._data, name)
            
            # Apply formatting based on field name
            if value is not None:
                # Fields that need 2 decimal places
                if name in ['crusher1_naphier_tph', 'water_flow_meter1', 'water_flow_meter2', 
                           'pt_slurry_flowmeter2', 'pt_slurry_flowmeter1', 'baloon1_pressure', 
                           'baloon1_lvl', 'baloon2_pressure', 'baloon2_lvl', 'sls_slurry_flowmeter',
                           'baloon3_pressure', 'baloon3_lvl', 'crusher2_naphier_tph', 
                           'dt1_pr_tx_1', 'dt1_pr_tx_2']:
                    return f"{float(value):.2f}"
                
                # Fields that need no decimal places (integers)
                elif name in ['bagging_unit']:
                    return f"{int(value)}"
                
                # Default formatting for other numeric fields
                else:
                    try:
                        return f"{float(value):.2f}"
                    except (ValueError, TypeError):
                        return str(value)
            
            return value
        
        return "?"

@login_required
def home(request):
    # Check for data within the last 10 minutes
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    recent_data = PIDData.objects.filter(created_at__gte=ten_minutes_ago).last()
    print(recent_data)
    # Use recent data if available, otherwise use latest data
    latest_data = recent_data if recent_data else PIDData.objects.last()
    
    # Flag to indicate if data is recent (within 10 minutes)
    is_data_recent = recent_data is not None
    
    # Wrap the data to handle "?" display logic
    wrapped_data = DataWrapper(latest_data, is_data_recent)
    
    # Calculate totals and wrap them too
    crusher1_total = defaultdict(float)
    for entry in PIDData.objects.all():
        day = entry.created_at.date()
        value = 0.0 if entry.crusher1_naphier_tph is None else entry.crusher1_naphier_tph
        crusher1_total[day] += value
        print(crusher1_total[day])
    
    # Apply "?" logic to totals if data is not recent
    if is_data_recent:
        today = timezone.now().date()
        crusher1_total = [
            {"day": day, "total_crusher": f"{total:.2f}"}
            for day, total in crusher1_total.items() if day == today
        ]
    else:
        crusher1_total = [{"day": day, "total_crusher": "?"} for day, total in crusher1_total.items()]
    
    crusher2_total = defaultdict(float)
    for entry in PIDData.objects.all():
        day = entry.created_at.date()
        value = 0.0 if entry.crusher2_naphier_tph is None else entry.crusher2_naphier_tph
        crusher2_total[day] += value
    
    if is_data_recent:
        crusher2_total = [
            {"day": day, "total_crusher": f"{total:.2f}"}
            for day, total in crusher2_total.items() if day == today
        ]
    else:
        crusher2_total = [{"day": day, "total_crusher": "?"} for day, total in crusher2_total.items()]
    
    fom_bag_total = defaultdict(float)
    for entry in PIDData.objects.all():
        day = entry.created_at.date()
        value = 0.0 if entry.bagging_unit is None else entry.bagging_unit
        fom_bag_total[day] += value
    
    if is_data_recent:
        fom_bag_total = [
            {"day": day, "fom_bag_total": f"{total:.0f}"}
            for day, total in fom_bag_total.items() if day == today
        ]
    else:
        fom_bag_total = [{"day": day, "fom_bag_total": "?"} for day, total in fom_bag_total.items()]
    
    context = {
        "data": wrapped_data,
        "crusher1_total": crusher1_total,
        "crusher2_total": crusher2_total,
        "fom_bag_total": fom_bag_total,
    }
    return render(request, 'home.html', context)

@login_required
def pid_data(request):
    # Check for data within the last 10 minutes
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    recent_data = PIDData.objects.filter(created_at__gte=ten_minutes_ago).last()
    
    # Use recent data if available, otherwise use latest data
    latest_data = recent_data if recent_data else PIDData.objects.last()
    
    # Flag to indicate if data is recent (within 10 minutes)
    is_data_recent = recent_data is not None
    
    # Wrap the data to handle "?" display logic
    wrapped_data = DataWrapper(latest_data, is_data_recent)
    
    context = {
        "data": wrapped_data
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
        'users': users,
        'editing': False
    })

@login_required
@role_required(['Admin', 'Manager'])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.user == user:
        messages.error(request, "You can't delete yourself.")
        return redirect('create_user')
    try:
        user.delete()
        messages.success(request, f'User {user.username} deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
    return redirect('create_user')

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('create_user')
    else:
        form = CustomUserCreationForm(instance=user)

    try:
        users = CustomUser.objects.all()
    except Exception as e:
        users = []
        messages.error(request, f'Error fetching users: {str(e)}')

    context = {
        'form': form,
        'users': users,
        'editing': True,
        'edit_user_id': user.id,
    }
    return render(request, 'user.html', context)



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

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def powerconsumption_report(request):
    context = {}

    # Get filters
    filter_type = request.GET.get('filter_type', 'individual')
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    shift = request.GET.get('shift')
    limit = int(request.GET.get('limit', 50))

    # Today and current month values
    today = timezone.localdate()
    current_month = today.month
    current_year = today.year

    # Base queryset
    queryset = BiogasPlantReport.objects.all().order_by("-report_time")

    # Filter by shift if provided
    if shift:
        queryset = queryset.filter(shift=shift)

    # Handle button filters
    if filter_type == "day":
        queryset = queryset.filter(date=today)
    elif filter_type == "month":
        queryset = queryset.filter(date__month=current_month, date__year=current_year)
    else:
        # Manual date/month/year filters
        if date:
            queryset = queryset.filter(date=date)
        elif month and year:
            queryset = queryset.filter(date__month=int(month), date__year=int(year))
        elif year:
            queryset = queryset.filter(date__year=int(year))

    # Get years for dropdown
    all_years = BiogasPlantReport.objects.dates('date', 'year')
    years = sorted([dt.year for dt in all_years], reverse=True)

    # Main data table
    report_data = queryset.order_by('-date', '-id')

    # Limit for chart data
    individual_reports = report_data[:limit]

    # Chart data
    monthly_data = []
    hourly_data = []

    for i, report in enumerate(individual_reports):
        date_label = report.date.strftime('%m/%d')
        shift_short = report.shift[:1] if report.shift else "?"
        point_label = f"{date_label}-{shift_short}{i+1}"

        monthly_data.append({
            'month': point_label,
            'power_consumption': float(report.power_consumption_kwh or 0),
            'power_cost': float(report.total_power_cost or 0),
            'gas_purity': float(report.gas_purity_percent or 0),
        })

        hourly_data.append({
            'hour': point_label,
            'bags': int(report.fom_bag_count or 0),
        })

    if not monthly_data:
        monthly_data = [{'month': 'No Data', 'power_consumption': 0, 'power_cost': 0}]
    if not hourly_data:
        hourly_data = [{'hour': 'No Data', 'bags': 0}]

    # Summary statistics
    summary_stats = queryset.aggregate(
        total_records=Count('id'),
        avg_power=Avg('power_consumption_kwh'),
        max_power=Max('power_consumption_kwh'),
        min_power=Min('power_consumption_kwh'),
        total_bags=Sum('fom_bag_count'),
        avg_bags=Avg('fom_bag_count'),
        avg_gas_purity=Avg('gas_purity_percent'),
    )
    monthly_data.reverse()
    hourly_data.reverse()

    # Context to template
    context.update({
        'report_data': report_data,
        'years': years,
        'selected_shift': shift,
        'monthly_data': monthly_data,
        'hourly_data': hourly_data,
        'selected_date': date,
        'selected_month': month,
        'selected_year': year,
        'filter_type': filter_type,
        'limit': limit,
        'summary_stats': summary_stats,
    })

    return render(request, 'powerconsumption_report.html', context)

@login_required
def bagsgenerated_report(request):
    return render(request, 'bags.html')

@login_required
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
            'report_time': str(report.report_time),
            'stoppage_time': str(report.stoppage_time),
        })

    return JsonResponse({'reports': data})

@login_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    one_hour_ago = now - timedelta(hours=1)

    # Determine current shift and time window
    current_hour = now.hour
    if current_hour < 8:
        current_shift = "Night Shift"
        window_start = 0
        window_name = "Night Shift (00:00 - 08:00)"
    elif current_hour < 16:
        current_shift = "General Shift"
        window_start = 8
        window_name = "Day Shift (08:00 - 16:00)"
    else:
        current_shift = "Evening Shift"
        window_start = 16
        window_name = "Evening Shift (16:00 - 24:00)"

    window_end = window_start + 8

    window_start_time = timezone.make_aware(
        datetime.combine(today, datetime.min.time()) + timedelta(hours=window_start)
    )
    window_end_time = timezone.make_aware(
        datetime.combine(today, datetime.min.time()) + timedelta(hours=window_end)
    )

    # Reports in window
    reports_in_window = BiogasPlantReport.objects.filter(
        date=today,
        shift=current_shift
    ).order_by('report_time')

    # Current latest report (used for expected values)
    current_report = BiogasPlantReport.objects.order_by('-date', '-report_time').first()

    # Use RawSQL to get report from last 1 hour
    previous_hour_report = BiogasPlantReport.objects.extra(
        where=["report_time BETWEEN %s AND %s"],
        params=[one_hour_ago, now]
    ).order_by('-report_time').first()

    # Group reports by hour
    hourly_data = {}
    for report in reports_in_window:
        if report.report_time:
            report_hour = report.report_time.hour
            if report_hour not in hourly_data or report.report_time > hourly_data[report_hour].report_time:
                hourly_data[report_hour] = report

    # Chart data
    time_labels = []
    expected_clean_gas_data = []
    actual_clean_gas_data = []
    expected_production_data = []
    actual_cbg_production_data = []
    biogas_data = []
    co2_data = []
    feedstock_data = []

    if current_report:
        expected_clean_gas_value = float(current_report.expected_clean_gas_nm3)
        expected_production_value = float(current_report.expected_production_kg)
    else:
        expected_clean_gas_value = 0
        expected_production_value = 0

    for hour_offset in range(8):
        hour = window_start + hour_offset
        time_labels.append(f"{hour:02d}:00")
        expected_clean_gas_data.append(expected_clean_gas_value)
        expected_production_data.append(expected_production_value)

        if hour in hourly_data:
            report = hourly_data[hour]
            actual_clean_gas_data.append(float(report.actual_clean_gas_nm3))
            actual_cbg_production_data.append(float(report.actual_cbg_production_kg))
            biogas_data.append(float(report.raw_biogas_produced_nm3))
            co2_data.append(float(report.co2_savings_mt))
            feedstock_data.append(float(report.feedstock_used_ton))
        else:
            actual_clean_gas_data.append(None)
            actual_cbg_production_data.append(None)
            biogas_data.append(None)
            co2_data.append(None)
            feedstock_data.append(None)
    all_drivers_status = DriverStatus.objects.all().order_by('-time_stamp')
    latest_status = {}
    for status in all_drivers_status:
        if status.driver_name not in latest_status:
            latest_status[status.driver_name] = status

    failed_drivers = [ds.driver_name for ds in latest_status.values() if ds.driver_status != '1']
    any_failed = bool(failed_drivers)
    # Status Cards Context
    if previous_hour_report:
        running_hours = previous_hour_report.running_time.total_seconds() / 3600
        stoppage_hours = previous_hour_report.stoppage_time.total_seconds() / 3600
        context = {
            'expected_clean_gas': previous_hour_report.expected_clean_gas_nm3,
            'actual_clean_gas': previous_hour_report.actual_clean_gas_nm3,
            'expected_production': previous_hour_report.expected_production_kg,
            'actual_cbg_production': previous_hour_report.actual_cbg_production_kg,
            'hourly_feedstock': previous_hour_report.feedstock_used_ton,
            'feedstock_cost': previous_hour_report.total_feed_cost,
            'hourly_raw_biogas': previous_hour_report.raw_biogas_produced_nm3,
            'hourly_co2_savings': previous_hour_report.co2_savings_mt,
            'power_consumption': previous_hour_report.power_consumption_kwh,
            'power_cost': previous_hour_report.total_power_cost,
            'fom_bags': previous_hour_report.fom_bag_count or 0,
            'running_hours': running_hours,
            'stoppage_hours': stoppage_hours,
        }
    else:
        context = {
            'expected_clean_gas': "?",
            'actual_clean_gas': "?",
            'expected_production': "?",
            'actual_cbg_production': "?",
            'hourly_feedstock': "?",
            'feedstock_cost': "?",
            'hourly_raw_biogas': "?",
            'hourly_co2_savings': "?",
            'power_consumption': "?",
            'power_cost': "?",
            'fom_bags': "?",
            'running_hours': "?",
            'stoppage_hours': "?",
        }

    # Add chart data and metadata to context
    context.update({
        'expected_clean_gas_data': json.dumps(expected_clean_gas_data),
        'actual_clean_gas_data': json.dumps(actual_clean_gas_data),
        'expected_production_data': json.dumps(expected_production_data),
        'actual_cbg_production_data': json.dumps(actual_cbg_production_data),
        'biogas_chart_data': json.dumps(biogas_data),
        'co2_chart_data': json.dumps(co2_data),
        'feedstock_chart_data': json.dumps(feedstock_data),
        'time_labels': json.dumps(time_labels),
        'current_window': window_name,
        'current_shift': current_shift,
        'window_start_hour': window_start,
        'window_end_hour': window_end,
        'total_reports_in_window': len(reports_in_window),
        'hours_with_data': len(hourly_data),
        'all_drivers_status': all_drivers_status,
        'failed_drivers': failed_drivers,
        'any_failed': any_failed,
    })

    return render(request, 'dashboard.html', context)


@login_required
def feedstock_report(request):

    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    shift = request.GET.get('shift')
    filter_type = request.GET.get('filter_type')

    
    # Initialize variables
    report_data = []
    feedstock_data = []
    feedstock_cost_data = []
    biogas_data = []
    co2_data = []
    labels = []
    selected_info = ""
    
    today = timezone.localdate()
    current_month = today.month
    current_year = today.year

    # Initialize query
    query = BiogasPlantReport.objects.all().order_by("-report_time")
    if filter_type == "day":
        query = query.filter(date=today)
    elif filter_type == "month":
        query = query.filter(date__month=current_month, date__year=current_year)

    if date:
        # Filter by specific date
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(date=selected_date)
        selected_info = f"Selected Date: {selected_date.strftime('%d %b %Y')}"
        
        # For single date, show each record
        for report in query:
            labels.append(report.date.strftime('%d %b %Y'))
            feedstock_data.append(float(report.feedstock_used_ton))
            feedstock_cost_data.append(float(report.total_feed_cost))
            biogas_data.append(float(report.raw_biogas_produced_nm3))
            co2_data.append(float(report.co2_savings_mt))
            
    elif month and year:
        # Filter by month and year
        query = query.filter(date__year=year, date__month=month)
        month_name = datetime(int(year), int(month), 1).strftime('%B')
        selected_info = f"Selected Month: {month_name} {year}"
        
        # Group by day for month view
        daily_data = {}
        for report in query:
            day_key = report.date.strftime('%d %b')
            if day_key not in daily_data:
                daily_data[day_key] = {
                    'feedstock': 0, 'cost': 0, 'biogas': 0, 'co2': 0, 'count': 0
                }
            daily_data[day_key]['feedstock'] += report.feedstock_used_ton
            daily_data[day_key]['cost'] += report.total_feed_cost
            daily_data[day_key]['biogas'] += report.raw_biogas_produced_nm3
            daily_data[day_key]['co2'] += report.co2_savings_mt
            daily_data[day_key]['count'] += 1
        
        # Prepare data for charts
        for day_key, data in daily_data.items():
            labels.append(day_key)
            # Calculate averages if multiple entries per day
            feedstock_data.append(data['feedstock'] / data['count'])
            feedstock_cost_data.append(data['cost'] / data['count'])
            biogas_data.append(data['biogas'] / data['count'])
            co2_data.append(data['co2'] / data['count'])
            
    elif year:
        # Filter by year
        query = query.filter(date__year=year)
        selected_info = f"Selected Year: {year}"
        
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
    else:
        selected_info = "All Available Data"
        
        for report in query:
            labels.append(report.date.strftime('%d %b %Y'))
            feedstock_data.append(float(report.feedstock_used_ton))
            feedstock_cost_data.append(float(report.total_feed_cost))
            biogas_data.append(float(report.raw_biogas_produced_nm3))
            co2_data.append(float(report.co2_savings_mt))

    
    # Apply shift filter if provided
    if shift:
        query = query.filter(shift=shift)
        
        # Recalculate chart data after applying shift filter
        feedstock_data = []
        feedstock_cost_data = []
        biogas_data = []
        co2_data = []
        labels = []
        
        if date:
            # For single date with shift filter
            for report in query:
                labels.append(f"{report.date.strftime('%d %b %Y')} - {report.shift}")
                feedstock_data.append(float(report.feedstock_used_ton))
                feedstock_cost_data.append(float(report.total_feed_cost))
                biogas_data.append(float(report.raw_biogas_produced_nm3))
                co2_data.append(float(report.co2_savings_mt))
        elif month and year:
            # For month/year with shift filter - group by day
            daily_data = {}
            for report in query:
                day_key = report.date.strftime('%d %b')
                if day_key not in daily_data:
                    daily_data[day_key] = {
                        'feedstock': 0, 'cost': 0, 'biogas': 0, 'co2': 0, 'count': 0
                    }
                daily_data[day_key]['feedstock'] += report.feedstock_used_ton
                daily_data[day_key]['cost'] += report.total_feed_cost
                daily_data[day_key]['biogas'] += report.raw_biogas_produced_nm3
                daily_data[day_key]['co2'] += report.co2_savings_mt
                daily_data[day_key]['count'] += 1
            
            for day_key, data in daily_data.items():
                labels.append(day_key)
                feedstock_data.append(data['feedstock'] / data['count'])
                feedstock_cost_data.append(data['cost'] / data['count'])
                biogas_data.append(data['biogas'] / data['count'])
                co2_data.append(data['co2'] / data['count'])
        elif year:
            # For year with shift filter - group by month
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
            
            months_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            labels = months_full
            
            for i in range(1, 13):
                if months_data[i]['count'] > 0:
                    feedstock_data.append(months_data[i]['feedstock'] / months_data[i]['count'])
                    feedstock_cost_data.append(months_data[i]['cost'] / months_data[i]['count'])
                    biogas_data.append(months_data[i]['biogas'] / months_data[i]['count'])
                    co2_data.append(months_data[i]['co2'] / months_data[i]['count'])
                else:
                    feedstock_data.append(0)
                    feedstock_cost_data.append(0)
                    biogas_data.append(0)
                    co2_data.append(0)
        else:
            # For today with shift filter
            for report in query:
                labels.append(f"{report.date.strftime('%d %b %Y')} - {report.shift}")
                feedstock_data.append(float(report.feedstock_used_ton))
                feedstock_cost_data.append(float(report.total_feed_cost))
                biogas_data.append(float(report.raw_biogas_produced_nm3))
                co2_data.append(float(report.co2_savings_mt))
    
    # Prepare report data for table display
    report_data = []
    for report in query:
        report_data.append({
            'date': report.date.strftime('%Y-%m-%d'),
            'feedstock_used_ton': report.feedstock_used_ton,
            'total_feed_cost': report.total_feed_cost,
            'raw_biogas_produced_nm3': report.raw_biogas_produced_nm3,
            'co2_savings_mt': report.co2_savings_mt
        })
    
    # Get years for dropdown
    years = BiogasPlantReport.objects.dates('date', 'year').values_list('date__year', flat=True).distinct()
    years = sorted(years, reverse=True)  # Most recent years first
    
    # Get shifts for dropdown
    shifts = BiogasPlantReport.objects.values('shift').distinct()
    labels.reverse()
    feedstock_data.reverse()
    feedstock_cost_data.reverse()
    biogas_data.reverse()
    co2_data.reverse()
    # Prepare chart data as JSON
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
    
    # Convert chart_data to JSON string for template
    chart_data_json = json.dumps(chart_data)
    
    return render(request, 'feedstock_report.html', {
        'report_data': report_data,
        'chart_data': chart_data_json,
        'years': years,
        'shifts': shifts,
        'selected_info': selected_info,
        'selected_shift': shift
    })


@login_required
def cost_entry_view(request):
    feed_form = FeedstockCostForm(prefix='feed')
    power_form = PowerCostForm(prefix='power')
    cbg_form = CBGSaleDispatchForm(prefix='cbg')
    fom_form = FOMSaleDispatchForm(prefix='fom')
    expected_cbg_form = CBGProductionForm(prefix='expected_cbg')
    expected_cleangas_production_form = CleanGasProductionForm(prefix='expected_clean_gas')

    if request.method == 'POST':
        if 'feedstock_submit' in request.POST:
            feed_form = FeedstockCostForm(request.POST, prefix='feed')
            if feed_form.is_valid():
                feed_form.save()
                success(request, message="Feedstock Cost Submitted successfully!")
                return redirect('manual_entry')

        elif 'power_submit' in request.POST:
            power_form = PowerCostForm(request.POST, prefix='power')
            if power_form.is_valid():
                power_form.save()
                success(request, message="Power Cost Submitted successfully!")
                return redirect('manual_entry')

        elif 'cbg_submit' in request.POST:
            cbg_form = CBGSaleDispatchForm(request.POST, prefix='cbg')
            if cbg_form.is_valid():
                cbg_form.save()
                success(request, message="CBG Sale & Dispatch Submitted successfully!")
                return redirect('manual_entry')
        
        elif 'fom_submit' in request.POST:
            fom_form = FOMSaleDispatchForm(request.POST, prefix='fom')
            if fom_form.is_valid():
                fom_form.save()
                success(request, message="FOM Sale & Dispatch Submitted successfully!")
                return redirect('manual_entry')
        
        elif 'expected_cbg_submit' in request.POST:
            expected_cbg_form = CBGProductionForm(request.POST, prefix='expected_cbg')
            if expected_cbg_form.is_valid():
                expected_cbg_form.save()
                success(request, message="Expected Hourly CBG Production Submitted successfully!")
                return redirect('manual_entry')
        
        elif 'expected_clean_gas_submit' in request.POST:
            expected_cleangas_production_form = CleanGasProductionForm(request.POST, prefix='expected_clean_gas')
            if expected_cleangas_production_form.is_valid():
                expected_cleangas_production_form.save()
                success(request, message="Expected Hourly Clean Gas Production Submitted successfully!")
                return redirect('manual_entry')
        
    feedstock_entries = FeedstockCost.objects.all().order_by('-date_recorded')[:5]
    power_entries = PowerCost.objects.all().order_by('-date_recorded')[:5]
    cbg_entries = CBGSaleDispatch.objects.all().order_by('-date_recorded')[:5]
    fom_entries = FOMSaleDispatch.objects.all().order_by('-date_recorded')[:5]
    expected_cbg_entries = HourlyExpectedCBGProduction.objects.all().order_by('-date_recorded')[:5]
    expected_cleangas_entries = ExpectedHourlyProduction.objects.all().order_by('-date_recorded')[:5]                              

    return render(request, 'manual_entry.html', {
        'feed_form': feed_form,
        'power_form': power_form,
        'cbg_form': cbg_form,
        'fom_form': fom_form,
        'expected_cbg_form': expected_cbg_form,
        'expected_cleangas_production_form': expected_cleangas_production_form,
        'feedstock_entries': feedstock_entries,
        'power_entries': power_entries,
        'cbg_entries': cbg_entries,
        'fom_entries': fom_entries,
        'expected_cbg_entries': expected_cbg_entries,
        'expected_cleangas_entries': expected_cleangas_entries,
    })

@login_required
def report(request):
    # Start with all reports
    reports_query = BiogasPlantReport.objects.all()
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        reports_query = reports_query.filter(date=date_filter)

    # Filter by day (today)
    if request.GET.get('day'):
        reports_query = reports_query.filter(date=date.today())

    # Filter by this month
    if request.GET.get('this_month'):
        today = date.today()
        reports_query = reports_query.filter(date__month=today.month, date__year=today.year)

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
    
    # Default values for charts
    expected_clean_gas_percentage = 0
    actual_production_percentage = 0
    
    # Prepare data for line charts
    chart_data = {
        'dates': [],
        'expected_clean_gas_data': [],
        'actual_clean_gas_data': [],
        'expected_production_data': [],
        'actual_production_data': [],
    }
    
    # Calculate data for charts based on filtered reports
    if reports.exists():
        # Calculate totals for all filtered reports
        total_expected_clean_gas = sum(report.expected_clean_gas_nm3 or 0 for report in reports)
        total_actual_clean_gas = sum(report.actual_clean_gas_nm3 or 0 for report in reports)
        
        total_expected_production = sum(report.expected_production_kg or 0 for report in reports)
        total_actual_production = sum(report.actual_cbg_production_kg or 0 for report in reports)
        
        # Calculate percentages for pie charts
        if total_expected_clean_gas > 0:
            expected_clean_gas_percentage = (total_actual_clean_gas / total_expected_clean_gas) * 100
            expected_clean_gas_percentage = round(expected_clean_gas_percentage, 2)
        
        if total_expected_production > 0:
            actual_production_percentage = (total_actual_production / total_expected_production) * 100
            actual_production_percentage = round(actual_production_percentage, 2)
        
        # Prepare data for line charts (ordered by date for proper timeline)
        ordered_reports = reports.order_by('date')
        print(ordered_reports)
        
        for report in ordered_reports:
            chart_data['dates'].append(report.date.strftime('%Y-%m-%d'))
            chart_data['expected_clean_gas_data'].append(float(report.expected_clean_gas_nm3 or 0))
            chart_data['actual_clean_gas_data'].append(float(report.actual_clean_gas_nm3 or 0))
            chart_data['expected_production_data'].append(float(report.expected_production_kg or 0))
            chart_data['actual_production_data'].append(float(report.actual_cbg_production_kg or 0))
    
    # Get unique years for the year dropdown
    years = BiogasPlantReport.objects.dates('date', 'year')
    years = [date.year for date in years]
    
    # Get shifts from model choices
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
        'selected_shift': shift or '',
        
        # Chart data for JavaScript
        'chart_dates': json.dumps(chart_data['dates']),
        'expected_clean_gas_data': json.dumps(chart_data['expected_clean_gas_data']),
        'actual_clean_gas_data': json.dumps(chart_data['actual_clean_gas_data']),
        'expected_production_data': json.dumps(chart_data['expected_production_data']),
        'actual_production_data': json.dumps(chart_data['actual_production_data']),
    }
    
    return render(request, 'report.html', context)


@login_required
def running_hours(request):
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 1)
    
    # Get filter parameters
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    shift = request.GET.get('shift')
    
    # Start with all reports
    queryset = BiogasPlantReport.objects.all()
    
    # Apply date filters
    if date:
        # Filter by specific date
        queryset = queryset.filter(date=date)
    elif month and year:
        # Filter by month and year
        queryset = queryset.filter(date__month=int(month), date__year=int(year))
    else:
        # Default to current month if no filters
        today = datetime.now()
        queryset = queryset.filter(date__month=today.month, date__year=today.year)
    
    # Apply shift filter if selected
    if shift:
        queryset = queryset.filter(shift=shift)
    
    # Order by date and time
    queryset = queryset.order_by("date", "report_time")
    
    # Process data for table display
    report_data = []
    for report in queryset:
        report_data.append({
            'date': report.date,
            'shift': report.shift,
            'running_hours': round(report.running_time.total_seconds() / 3600, 2),
            'stoppage_hours': round(report.stoppage_time.total_seconds() / 3600, 2),
        })
    
    # Process data for chart - group by date
    daily_data = defaultdict(lambda: {'running': 0, 'stoppage': 0})
    
    for report in queryset:
        date_str = report.date.strftime('%d/%m')
        daily_data[date_str]['running'] += report.running_time.total_seconds() / 3600
        daily_data[date_str]['stoppage'] += report.stoppage_time.total_seconds() / 3600
    
    # Prepare chart data
    chart_data = {
        'labels': [],
        'running_hours': [],
        'stoppage_hours': []
    }
    
    # Sort dates and prepare chart data
    sorted_dates = sorted(daily_data.keys(), key=lambda x: datetime.strptime(x, '%d/%m'))
    
    for date_str in sorted_dates:
        chart_data['labels'].append(date_str)
        chart_data['running_hours'].append(round(daily_data[date_str]['running'], 2))
        chart_data['stoppage_hours'].append(round(daily_data[date_str]['stoppage'], 2))
    
    # Calculate totals for summary
    total_running = sum(chart_data['running_hours'])
    total_stoppage = sum(chart_data['stoppage_hours'])
    
    chart_data['total_running'] = round(total_running, 2)
    chart_data['total_stoppage'] = round(total_stoppage, 2)
    
    context = {
        'years': years,
        'report_data': report_data,
        'selected_shift': shift,
        'chart_data': chart_data,
    }
    
    return render(request, 'Runninghours.html', context)

class ReportViewset(ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    def get_queryset(self):
        return BiogasPlantReport.objects.order_by('-id')[:1]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['date', 'shift']
    filterset_fields = ['date', 'shift']
    ordering_fields = ['date', 'shift']

@login_required
def set_point_view(request):
    if request.method == 'POST':
        form = SetPointForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('set_point_list') 
    else:
        form = SetPointForm()
    return render(request, 'set_point.html', {'form': form})

@login_required
def set_point_list_view(request):
    set_points = SetPoint.objects.all()
    return render(request, 'list.html', {'set_points': set_points})

@login_required
def edit_set_point(request, id):
    point = get_object_or_404(SetPoint, id=id)
    if request.method == 'POST':
        form = SetPointForm(request.POST, instance=point)
        if form.is_valid():
            form.save()
            return redirect('set_point_list')
    else:
        form = SetPointForm(instance=point)
    return render(request, 'list.html', {'form': form})

@login_required
def delete_set_point(request, id):
    point = get_object_or_404(SetPoint, id=id)
    point.delete()
    return redirect('set_point_list')

def driver_status(request):
    all_drivers_status = DriverStatus.objects.all()

    context = {
        'all_drivers_status': all_drivers_status,
    }
    return render(request, 'driver_status.html', context)