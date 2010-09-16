# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.db import models
from django.contrib import admin
from stateworkflow.errors import WorkflowScriptAbsent, WorkflowScriptError

admin_registry = []
script_registry = {}

def register(id, name, script):
    # a nice mapping for the UI
    admin_registry.append([id, name])
    # a script mapping for actually doing the work
    script_registry[id] = script

def registry_iterator():
    for choice in admin_registry:
        yield choice

class Script(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    method = models.CharField(max_length=255, choices=registry_iterator())

    def do(self, obj, transition):
        if not script_registry.has_key(self.method):
            raise WorkflowScriptAbsent, "That script is not registered"
        # right lookup thing in registry
        methd = script_registry[self.method]
        return methd(obj, transition)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "stateworkflow"

class ScriptAdmin(admin.ModelAdmin):
    pass

admin.site.register(Script, ScriptAdmin)