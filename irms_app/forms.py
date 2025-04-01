from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Role, PIDData

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
            'password1', 
            'password2', 
            'status'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.company_name = self.cleaned_data['company_name']
        user.role = self.cleaned_data['role']
        user.status = self.cleaned_data['status']
        
        if commit:
            user.save()
        return user
    
class PIDDataForm(forms.ModelForm):
    class Meta:
        model = PIDData
        fields = '__all__'