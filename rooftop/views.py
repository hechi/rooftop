# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
from django.template import Context
from django.template.response import TemplateResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.conf import settings
import ldap
import ldap.modlist as modlist
from passlib.hash import ldap_md5 as lsm

@login_required
def start(request):
    template = get_template('start.html')
    param = getHeaderParam(request)

    context = RequestContext(request,param)
    html = template.render(context) 
    return HttpResponse(html)

def getHeaderParam(request):
    param = {}
    groups=[]
    param['displayname'] = encMsg(request.user.first_name)

    profile={}
    profile['external']=False
    profile['icon']='glyphicon-user'
    profile['link']="/userprofile/"
    profile['name']="Profil"

    groups.append(profile)
    param['groups'] = groups
    
    return param

@login_required
def userprofile(request):
    template = get_template('userprofile.html')
    param = getHeaderParam(request)
    
    if request.method == 'POST' and 'passwdForm' in request.POST:
        user = request.user
        
        # Open a connection
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

        # The dn of our new entry/object
        dn="uid="+user.username+","+settings.AUTH_LDAP_BASE_USER_DN       

        if 'old_password' in request.POST and 'new_password1' in request.POST and 'new_password2' in request.POST:
            try:
                # Bind/authenticate with a user with apropriate rights to add objects
                l.simple_bind_s(dn,request.POST['old_password'])
                if request.POST['new_password1'] == request.POST['new_password2']:
                    l.passwd_s(dn,request.POST['old_password'],request.POST['new_password1'])
                    user.set_password(request.POST['new_password1'])
                    param['status']=encMsg("thanks, password has been changed")
                    user.save()
                else:
                    param['statusError']=encMsg("password has NOT been CHANGED, new password does not match")
            except:
                param['statusError']=encMsg("wrong password, please try again")
        else:
            param['statusError']=encMsg("password has NOT been CHANGED, wrong input")

        # Its nice to the server to disconnect and free resources when done
        l.unbind_s()

    passwdForm=PasswordChangeForm(user=request.user)
    param['passwd'] = passwdForm
    
    context = RequestContext(request,param)
    html = template.render(context)     
    return HttpResponse(html)

def encMsg(msg):
    dec=""
    try:
        dec = msg.decode('utf-8')
    except:
        try:
            msgA = unicode(msg.encode('iso-8859-1'),'iso-8859-1')
            dec = msgA
        except:
            dec = "ERROR CAN NOT BE PRINTED"
    return dec