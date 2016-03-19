# -*- coding: utf-8 -*-
class LdapUser:
    def __init__(self,firstname,lastname,uid,mail,password=""):
        self.firstname=firstname
        self.lastname=lastname
        self.uid=uid
        self.mail=mail
        self.displayname= str(firstname)+" "+ str(lastname)
        self.password=password

    def getFirstname(self):
        if self.firstname!=None and self.firstname != "" and self.firstname.strip():
            return str( (self.firstname) )
        else:
            return str( ("Firstname") )

    def getLastname(self):
        if self.lastname!=None and self.lastname != "" and self.lastname.strip():
            return str( (self.lastname) )
        else:
            return str( ("Lastname") )

    def getUid(self):
        return str(self.uid)

    def getMail(self):
        if self.mail!=None and self.mail != "" and self.mail.strip():
            return str( (self.mail) )
        else:
            return str( ("example@domain.com") )

    def getDisplayname(self):
        if self.displayname!=None and self.displayname != "" and self.displayname.strip():
            return str( (self.displayname) )
        else:
            return str( ("displayName") )

    def getPassword(self):
        return str( (self.password) )

    def getUidWithoutDots(self):
        return str(self.getUid().replace('.','_'))

    def display(self):
        print("==== "+ (self.firstname)+" "+ (self.lastname)+" ====")
        print("Firstname: "+ (self.firstname))
        print("Lastname: "+ (self.lastname))
        print("Username: "+ (self.uid))
        print("Email: "+ (self.mail))
        print("displayname: "+ (self.displayname))
