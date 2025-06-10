from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Role, CustomUser, Section, Equipment, Parameter, Plant,
    Connection, FieldLink, LocalData, PIDData, BiogasPlantReport
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'full_name', 'email', 'role', 'status')
    search_fields = ('username', 'full_name', 'email')
    list_filter = ('role', 'status')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'company_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('status',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'email', 'password1', 'password2', 'role', 'status'),
        }),
    )
    ordering = ('username',)

admin.site.register(Role)
# admin.site.register(Section)
# admin.site.register(Equipment)
# admin.site.register(Parameter)
admin.site.register(Plant)
admin.site.register(Connection)
admin.site.register(FieldLink)
admin.site.register(LocalData)
admin.site.register(PIDData)
admin.site.register(BiogasPlantReport)