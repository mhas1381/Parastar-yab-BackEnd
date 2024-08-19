"""
Request app permiisions
"""
from rest_framework import permissions



class IsClient(permissions.BasePermission):
    '''Check if the user is client'''

    def has_permission(self, request, view):
        '''Getting user role from request.'''
        return request.user.role == 'CLIENT'
    


class IsNurse(permissions.BasePermission):
    '''Check if user in nurse.'''

    def has_permission(self, request, view):
        '''Getting user role from request.'''
        return request.user.role == 'NURSE'
    


    
            
    

