# -*- coding: utf-8 -*-
from django import forms

class userprofileForm(forms.Form):
    oldPassword = forms.CharField(label='Old Password',widget=forms.PasswordInput())
    newPassword = forms.CharField(label='New Password',widget=forms.PasswordInput())
    confirmPassword = forms.CharField(label='Confirm Password',widget=forms.PasswordInput())
