# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.template import Context
from django.template.response import TemplateResponse
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.conf import settings
import ldap
import ldap.modlist as modlist
from passlib.hash import ldap_md5 as lsm

from .forms import userprofileForm
from .models import LdapUser

import sys, traceback


@login_required
def start(request):
    template = get_template('start.html')
    param = getHeaderParam(request)

    context = Context(param)
    html = template.render(context)
    return HttpResponse(html)

def getHeaderParam(request):
    param = {}
    groups=[]
    param['displayname'] = request.user.first_name

    profile={}
    profile['external']=False
    profile['icon']='glyphicon-user'
    profile['link']="/userprofile/"
    profile['name']="Profil"

    groups.append(profile)
    param['groups'] = groups
    return param

class userprofileView(View):
    form_class = userprofileForm
    template_name = 'userprofile.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        return render(request, self.template_name, param)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        if form.is_valid():
            # <process form cleaned data>
            if form['newPassword'].value() != form['confirmPassword'].value():
                # print("not the same")
                param['form']=form
                param['statusError']=str("password has NOT been CHANGED, new password does not match")
                return render(request, self.template_name, param)
            param['form'] = self.form_class()
            if changePassword(request,form['oldPassword'].value(),form['newPassword'].value()):
                param['status']=("thanks, password has been changed")
            else:
                param['statusError']=("wrong password, please try again")
            return render(request, self.template_name, param)

        return render(request, self.template_name, param)

def changePassword(request,oldPassword,newPassword):
    retValue = False
    user = request.user

    # Open a connection
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

    # The dn of our new entry/object
    dn="uid="+user.username+","+settings.AUTH_LDAP_BASE_USER_DN

    try:
        # Bind/authenticate with a user with apropriate rights to add objects
        l.simple_bind_s(dn,oldPassword)
        l.passwd_s(dn,oldPassword,newPassword)
        user.set_password(newPassword)
        user.save()
        retValue=True
    except:
        traceback.print_exc(file=sys.stdout)
        retValue=False

    # Its nice to the server to disconnect and free resources when done
    print(retValue)
    l.unbind_s()
    return retValue
