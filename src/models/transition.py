# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.db import models
from django.contrib import admin
from stateworkflow.models.state import State
from stateworkflow.models.script import Script

class Transition(models.Model):
    name = models.CharField(max_length=255)
    starting_state = models.ForeignKey(State, related_name="starting_state")
    ending_state = models.ForeignKey(State, related_name="ending_state")
    permission_scripts = models.ManyToManyField(Script, blank=True, null=True, related_name="permission_scripts")
    do_scripts = models.ManyToManyField(Script, blank=True, null=True, related_name="do_scripts")

    def __unicode__(self):
        return self.name

    def allowed(self, obj):
        for script in self.permission_scripts.all():
            result = script.do(obj, self)
            if not result:
                return False
        return True

    def do(self, obj):
        for script in self.do_scripts.all():
            script.do(obj, self)

        return self.ending_state

    class Meta:
        app_label = "stateworkflow"

class TransitionAdmin(admin.ModelAdmin):
    list_display = ("name", "starting_state", "ending_state")

admin.site.register(Transition, TransitionAdmin)
