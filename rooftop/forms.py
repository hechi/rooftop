# -*- coding: utf-8 -*-
from django import forms

class UserprofileForm(forms.Form):
    oldPassword = forms.CharField(label='Old Password',widget=forms.PasswordInput())
    newPassword = forms.CharField(label='New Password',widget=forms.PasswordInput())
    confirmPassword = forms.CharField(label='Confirm Password',widget=forms.PasswordInput())

class AddUserForm(forms.Form):
    username = forms.CharField(label='Username')
    firstname = forms.CharField(label='Firstname')
    lastname = forms.CharField(label='Lastname')
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password',widget=forms.PasswordInput())

class AddGroupForm(forms.Form):
    groupname = forms.CharField(label='Groupname')
    description = forms.CharField(label='description')
