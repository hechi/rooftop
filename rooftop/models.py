# -*- coding: utf-8 -*-
class LdapUser:
    def __init__(self,vorname,nachname,uid,mail,password=""):
        self.vorname=vorname
        self.nachname=nachname
        self.uid=uid
        self.mail=mail
        self.displayname= str(vorname)+" "+ str(nachname)
        self.password=password

    def getVorname(self):
        if self.vorname!=None and self.vorname != "" and self.vorname.strip():
            return str( (self.vorname) )
        else:
            return str( ("Vorname") )

    def getNachname(self):
        if self.nachname!=None and self.nachname != "" and self.nachname.strip():
            return str( (self.nachname) )
        else:
            return str( ("Nachname") )

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
        print("==== "+ (self.vorname)+" "+ (self.nachname)+" ====")
        print("Vorname: "+ (self.vorname))
        print("Nachname: "+ (self.nachname))
        print("Username: "+ (self.uid))
        print("Email: "+ (self.mail))
        print("displayname: "+ (self.displayname))
