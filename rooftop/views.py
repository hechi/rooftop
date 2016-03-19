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
import json
import ldap
import ldap.modlist as modlist
from passlib.hash import ldap_md5 as lsm
from .forms import UserprofileForm, AddUserForm

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

class UserprofileView(View):
    form_class = UserprofileForm
    template_name = 'userprofile.html'

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

class AddUserView(View):
    form_class = AddUserForm
    template_name = 'adduser.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        return render(request, self.template_name, param)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        check=False
        param={}
        param=getHeaderParam(self.request)
        param['form']=form
        if form.is_valid() and isUserInGroup(request.user.username,settings.AUTH_LDAP_ADMIN_GROUP):
            # <process form cleaned data>
            uid= form['username'].value()
            cn= form['firstname'].value()
            sn= form['lastname'].value()
            mail= form['email'].value()
            password= form['password'].value()
            user = LdapUser(cn,sn,uid,mail,password)
            check=addUserToLdap(user)

        return HttpResponse(json.dumps(check), content_type="application/json")

def addUserToLdap(user):
    check = False
    try:
        # Open a connection
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)

        # Bind/authenticate with a user with apropriate rights to add objects
        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,str(settings.AUTH_LDAP_BIND_PASSWORD))

        # The dn of our new entry/object
        dn="uid="+user.getUid()+","+str(settings.AUTH_LDAP_BASE_USER_DN)

        # A dict to help build the "body" of the object
        # TODO: clean this
        attrs = {}
        attrs['objectclass'] = [str('inetOrgPerson'),str('top'),str('person'),str('shadowAccount'),str('posixAccount')]
        attrs['cn'] = user.getVorname()
        attrs['displayname'] = user.getDisplayname()
        attrs['mail'] = user.getMail()
        attrs['sn'] = user.getNachname()
        attrs['uid'] = user.getUid()
        attrs['userpassword'] = lsm.encrypt(user.getPassword())

        # necessary for posixAccount
        attrs['gidNumber']=str(1000)
        attrs['homeDirectory']=str(str('/home/').encode('utf-8'))+str(user.getUid())
        # TODO generate uniq uidNumber
        # TODO check if its uniq
        attrs['uidNumber']=str(1000)
        print(attrs)
        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        # Do the actual synchronous add-operation to the ldapserver
        print(dn)
        print(ldif)
        l.add_s(dn,ldif)

        # Its nice to the server to disconnect and free resources when done
        l.unbind_s()
        check = True
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)
    return check


def isUserInGroup(username,groupname):
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "(&(objectClass=groupOfNames)(CN="+groupname+"))"
    isInGroup=False

    try:
            ldap_result_id = l.search(settings.AUTH_LDAP_BASE_GROUP_DN, searchScope, searchFilter, retrieveAttributes)
            result_set = []
            res = {}
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                #print result_data
                if (result_data == []):
                    break
                else:
                    #print "check"
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        # find user in group
                        for u in result_data[0][1]['member']:
                            print(str(u).split("uid=")[1].split(",")[0])
                            if str(u).split("uid=")[1].split(",")[0] == username:
                                isInGroup=True
            l.unbind_s()
    except ldap.LDAPError:
        traceback.print_exc(file=sys.stdout)

    return isInGroup

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
