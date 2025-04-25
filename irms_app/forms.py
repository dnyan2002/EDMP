from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Role, PIDData, Plant
from .models import BiogasPlantReport, FeedstockCost, PowerCost, CBGSaleDispatch

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




# class BiogasPlantReportForm(forms.ModelForm):
#     class Meta:
#         model = BiogasPlantReport
#         fields = '__all__'
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'running_time': forms.TimeInput(attrs={'type': 'time'}),
#             'stoppage_time': forms.TimeInput(attrs={'type': 'time'}),
#         }


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
        fields = ['cost', 'cost_per_ton']
        widgets = {
            'cost': forms.NumberInput(attrs={'step': '0.01'}),
            'cost_per_ton': forms.NumberInput(attrs={'step': '0.01'}),
        }


class PowerCostForm(forms.ModelForm):
    class Meta:
        model = PowerCost
        fields = ['cost', 'cost_per_unit']
        widgets = {
            'cost': forms.NumberInput(attrs={'step': '0.01'}),
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
