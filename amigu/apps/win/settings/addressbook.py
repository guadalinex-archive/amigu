# -*- coding: utf-8 -*-

import os
import glob
import random
from os.path import expanduser, join, split, exists, dirname, getsize
from xml.dom import minidom
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _

class contacts(application):
    

    def initialize(self):
        self.name = _('Contactos de Windows')
        self.description = _('Contactos de Windows')
        self.size = 0.0
        self.cs = glob.glob(join(self.user.path, 'Contacts','*.contact'))
        if not self.cs:
            raise Exception
        for c in self.cs:
            self.size += getsize(c)/1024

    def do(self):
        import bsddb
        adb=join(expanduser('~'),'.evolution','addressbook','local','system','addressbook.db')
        folder(dirname(adb))
        db = bsddb.hashopen(adb,'w')
        if not 'PAS-DB-VERSION\x00' in db.keys():
            db['PAS-DB-VERSION\x00'] = '0.2\x00'
        for file in self.cs:
            c = contact(file)
            vcard = c.tovcard()
            if vcard:
                randomid = 'pas-id-' + str(random.random())[2:]
                vcard.insert(2, 'UID:'+randomid)
                db[randomid+'\x00'] = ''
                for l in vcard:
                    db[randomid+'\x00'] += l + '\r\n'
                db[randomid+'\x00'] += '\x00'
        db.sync()
        db.close()
        return 1


class contact:
    
    def __init__(self, file):
        self.xmldoc = minidom.parse(file)
        
    def get(self, name, node = None):
        s = ''
        if node:
            elems = node.getElementsByTagName('c:'+name)
        else:
            elems = self.xmldoc.getElementsByTagName('c:'+name)
        for e in elems:
            if e.hasChildNodes() and e.firstChild.nodeType == e.TEXT_NODE:
                 s = e.firstChild.data
        return s
            
    def getCollection(self, name, node = None):
        s = ''
        if node:
            elems = node.getElementsByTagName('c:'+name)
        else:
            elems = self.xmldoc.getElementsByTagName('c:'+name)
        for e in elems:
            yield e
            
    def getLabels(self, node):
        s = ''
        elems = node.getElementsByTagName('c:Label')
        for e in elems:
            yield e.firstChild.data

    def tovcard(self):
        vcard = ["BEGIN:VCARD", "VERSION:3.0"]
        vcard.append("FN:%s" % self.get("FormattedName"))
        vcard.append("N:%s;%s;%s;%s;%s" % (self.get("FamilyName"),self.get("GivenName"),self.get("MiddleName"),self.get("Prefix"),self.get("Suffix")))
        vcard.append("NICKNAME:%s" % self.get("NickName"))
        vcard.append("TITLE:%s" % self.get("Title"))
        for ad in self.getCollection("EmailAddress"):
            vcard.append("EMAIL;TYPE=INTERNET:%s" % self.get('Address', ad))
        for pn in self.getCollection("PhoneNumber"):
            labels = ""
            for lb in self.getLabels(pn):
                if lb == "Cellular":
                    lb = "Cell"
                elif lb == "Personal":
                    lb = "Home"
                labels += lb.upper()+','
            vcard.append("TEL;TYPE=%s:%s" % (labels[:-1], self.get('Number', pn)))
        for pa in self.getCollection("PhysicalAddress"):
            labels = ""
            for lb in self.getLabels(pa):
                if lb == "Personal":
                    lb = "Home"
                labels += lb.upper()+','
            vcard.append("ADR;TYPE=%s:%s;%s;%s;%s;%s;%s;%s" % (labels[:-1], self.get('POBox'), self.get('ExtendedAddress'),self.get('Street', pa), self.get('Locality', pa), self.get('Region', pa), self.get('PostalCode', pa), self.get('Country', pa)))
        for dt in self.getCollection("Date"):
            type, date = None, self.get('Value', dt)
            for lb in self.getLabels(dt):
                if lb == 'wab:Birthday':
                    type = "BDAY"
                elif lb == 'wab:Anniversary':
                    type = "X-EVOLUTION-ANNIVERSARY"
            if type and date:
                vcard.append("%s:%s" % (type, date))
        vcard.append("END:VCARD")
        return vcard
