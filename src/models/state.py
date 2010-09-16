# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.db import models
from django.contrib import admin
from stateworkflow.models.workflow import Workflow

class State(models.Model):
    name = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow)

    def get_transitions(self, obj):
        transitions = []
        possible = self.starting_state.all()
        for transition in possible:
            if transition.allowed(obj):
                transitions.append(transition)
        return transitions

    def do_transition(self, obj, transition):
        return transition.do(obj)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "stateworkflow"

class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "workflow")

admin.site.register(State, StateAdmin)