# -*- coding: utf-8 -*-

import os
import glob
from os.path import expanduser, join, split, exists, dirname, getsize
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _

class calendar(application):
    

    def initialize(self):
        self.name = _('Calendario de Windows')
        self.description = _('Calendario de Windows')
        self.size = 0
        self.icals = glob.glob(join(self.user.folders['Local AppData'].path, 'Microsoft', 'Windows Calendar', 'Calendars','*.ics'))
        if not self.icals:
            raise Exception
        for cal in self.icals:
            self.size += getsize(cal)

    def do(self):
        old = None
        evo_cal = join(expanduser('~'),'.evolution','calendar','local','system','calendar.ics')
        folder(dirname(evo_cal))
        dates = []
        if exists(evo_cal):
            old = backup(evo_cal)
            if old:
                new_cal = open(evo_cal, "w")
                old_cal = open(old, 'r')
                for l in old_cal.readlines():
                    if l.find('END:VCALENDAR') == -1:
                        new_cal.write(l)
                    if l.find('BEGIN:VEVENT') != -1:
                        dt, sum = None, None
                    elif l.find('END:VEVENT') != -1:
                        if dt and sum:
                            dates.append(dt+sum)
                    elif l.find('DTSTART') != -1:
                        dt = l.replace('DTSTART:', '')
                    elif l.find('SUMMARY') != -1:
                        sum = l.replace('SUMMARY:', '')
                old_cal.close()
        if not old:
            new_cal = open(evo_cal, "w")
            new_cal.write('BEGIN:VCALENDAR\n')
            new_cal.write('CALSCALE:GREGORIAN\n')
            new_cal.write('VERSION:2.0\n')
        for ical in self.icals:
            orig = open(ical,"r")
            buffer = ''
            for l in orig.readlines():
                buffer += l
                if l.find('BEGIN:VEVENT') != -1:
                    dt, sum = None, None
                    buffer = l
                elif l.find('END:VEVENT') != -1:
                    if dt and sum and not dt+sum in dates:
                        new_cal.write(buffer)
                elif l.find('DTSTART') != -1:
                    dt = l.replace('DTSTART:', '')
                elif l.find('SUMMARY') != -1:
                    sum = l.replace('SUMMARY:', '')
            orig.close()
        new_cal.write('END:VCALENDAR\n')
        return 1
