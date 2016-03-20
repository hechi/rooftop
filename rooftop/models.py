# -*- coding: utf-8 -*-
class LdapUser:
    def __init__(self,firstname,lastname,uid,mail,password=""):
        self.firstname=firstname
        self.lastname=lastname
        self.uid=uid
        self.mail=mail
        self.displayname= encMsg(firstname)+" "+ encMsg(lastname)
        self.password=password

    def getFirstname(self):
        if self.firstname!=None and self.firstname != "" and self.firstname.strip():
            return encMsg( (self.firstname) )
        else:
            return encMsg( ("Firstname") )

    def getLastname(self):
        if self.lastname!=None and self.lastname != "" and self.lastname.strip():
            return encMsg( (self.lastname) )
        else:
            return encMsg( ("Lastname") )

    def getUid(self):
        return encMsg(self.uid)

    def getMail(self):
        if self.mail!=None and self.mail != "" and self.mail.strip():
            return encMsg( (self.mail) )
        else:
            return encMsg( ("example@domain.com") )

    def getDisplayname(self):
        if self.displayname!=None and self.displayname != "" and self.displayname.strip():
            return str( (self.displayname) )
        else:
            return str( ("displayName") )

    def getPassword(self):
        return str( (self.password) )

    def getUidWithoutDots(self):
        return encMsg(self.getUid().replace('.','_'))

    def display(self):
        print("==== "+ (self.firstname)+" "+ (self.lastname)+" ====")
        print("Firstname: "+ (self.firstname))
        print("Lastname: "+ (self.lastname))
        print("Username: "+ (self.uid))
        print("Email: "+ (self.mail))
        print("displayname: "+ (self.displayname))

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
