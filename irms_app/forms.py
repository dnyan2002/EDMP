from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import (
    BiogasPlantReport, FeedstockCost, PowerCost, CBGSaleDispatch, FOMSaleDispatch, SetPoint,
    CustomUser, Role, PIDData, Plant, ExpectedHourlyProduction, HourlyExpectedCBGProduction
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=50, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter full name'})
    )
    company_name = forms.CharField(
        max_length=70, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter company name'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        required=True, 
        empty_label="Select a Role"
    )
    plant = forms.ModelChoiceField(
        queryset=Plant.objects.all(), 
        required=True, 
        empty_label="Select a Plant"
    )
    status = forms.ChoiceField(
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        initial='Active',
        required=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'full_name', 
            'company_name', 
            'role',
            'plant', 
            'password1', 
            'password2', 
            'status'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = CustomUser.objects.filter(username=username)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.company_name = self.cleaned_data['company_name']
        user.role = self.cleaned_data['role']
        user.plant = self.cleaned_data['plant']
        user.status = self.cleaned_data['status']
        
        if commit:
            user.save()
        return user
    
class PIDDataForm(forms.ModelForm):
    class Meta:
        model = PIDData
        fields = '__all__'

class BiogasPlantReportForm(forms.ModelForm):
    class Meta:
        model = BiogasPlantReport
        fields = [
            'feedstock_used_ton',
            'feedstock_cost_per_ton',
            'raw_biogas_produced_nm3',
            'methane_content_percent',
            'actual_clean_gas_nm3',
            'actual_cbg_production_kg',
            'gas_purity_percent',
            'power_consumption_kwh',
            'power_cost_per_unit',
            'co2_savings_mt',
            'fom_bag_count',
            'cbg_sale_dispatch_ton',
            'running_time',
            'stoppage_time',
        ]

class FeedstockCostForm(forms.ModelForm):
    class Meta:
        model = FeedstockCost
        fields = ['cost_per_ton']
        widgets = {
            'cost_per_ton': forms.NumberInput(attrs={'step': '0.01'}),
        }

class PowerCostForm(forms.ModelForm):
    class Meta:
        model = PowerCost
        fields = ['cost_per_unit']
        widgets = {
            'cost_per_unit': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CBGSaleDispatchForm(forms.ModelForm):
    class Meta:
        model = CBGSaleDispatch
        fields = ['dispatch_quantity', 'unit']
        widgets = {
            'dispatch_quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'unit': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class FOMSaleDispatchForm(forms.ModelForm):
    class Meta:
        model = FOMSaleDispatch
        fields = ['dispatch_quantity', 'unit']
        widgets = {
            'dispatch_quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'unit': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class SetPointForm(forms.ModelForm):
    class Meta:
        model = SetPoint
        fields = ['parameter_name', 'set_point_1', 'set_point_2']
        widgets = {
            'parameter_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Parameter Name'}),
            'set_point_1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Set Point 1'}),
            'set_point_2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Set Point 2'}),
        }

class CleanGasProductionForm(forms.ModelForm):
    class Meta:
        model = ExpectedHourlyProduction
        fields = ['clean_gas_production', 'unit']
        widgets = {
            'clean_gas_production': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class CBGProductionForm(forms.ModelForm):
    class Meta:
        model = HourlyExpectedCBGProduction
        fields = ['cbg_production', 'unit']
        widgets = {
            'cbg_production': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'readonly': 'readonly'}),
        }