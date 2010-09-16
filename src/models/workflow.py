# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.db import models
from django.contrib import admin

class Workflow(models.Model):
    name = models.CharField(max_length=255)
    # prevents a circular import by using the string not importing object
    default_state = models.ForeignKey("State", blank=True, null=True, related_name="default_state")

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "stateworkflow"

class WorkflowAdmin(admin.ModelAdmin):
    pass

admin.site.register(Workflow, WorkflowAdmin)

