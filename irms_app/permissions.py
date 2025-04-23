from functools import wraps
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=None):
    """
    Decorator to restrict view access based on user roles.
    
    :param allowed_roles: List of role names that are allowed to access the view
    :return: Decorated view function
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check if user is active
            if request.user.status != 'Active':
                messages.error(request, 'Your account is inactive. Please contact an administrator.')
                return redirect('login')
            
            # Check user's role
            user_role = request.user.role.role_name if request.user.role else None
            
            # If no roles specified, allow access
            if not allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Check if user's role is in allowed roles
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Deny access if role not in allowed roles
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        
        return wrapper
    return decorator


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Class-based view mixin to restrict access based on user roles.
    """
    allowed_roles = []
    permission_denied_message = 'You do not have permission to access this page.'

    def test_func(self):
        # Check if user is authenticated
        if not self.request.user.is_authenticated:
            return False
        
        # Check if user is active
        if self.request.user.status != 'Active':
            messages.error(self.request, 'Your account is inactive. Please contact an administrator.')
            return False
        
        # Check user's role
        user_role = self.request.user.role.role_name if self.request.user.role else None
        
        # If no roles specified, allow access
        if not self.allowed_roles:
            return True
        
        # Check if user's role is in allowed roles
        return user_role in self.allowed_roles

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('home')


def check_permission(user, permission_name):
    """
    Check if a user has a specific permission.
    
    :param user: CustomUser instance
    :param permission_name: Name of the permission to check
    :return: Boolean indicating if user has the permission
    """
    # Check if user has role and role has permissions
    if user.role:
        # Check direct user permissions
        if user.user_permissions.filter(codename=permission_name).exists():
            return True
        
        # Check role permissions
        if user.role.permissions.filter(codename=permission_name).exists():
            return True
    
    return False