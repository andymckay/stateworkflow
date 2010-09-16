# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.db import models
from stateworkflow.models.state import State

class WorkflowManager:
    """ The API for maintaining workflow can be a bit cumbersome
    and this makes it a little cleaner """
    def __init__(self, obj, fields=None):
        self.obj = obj
        self.workflows, self._names = self.findworkflows(fields)

    def findworkflows(self, fields=None):
        """ We try to figure out what is a workflow field for you
        if you know what they are and this bit of magic worries you
        then when you init, just pass through what they are eg:
        WorkflowManager(obj, ["publish_state",])
        """
        workflows = []
        names = {}
        if not fields:
            fields = []
            for field in self.obj._meta.fields:
                if isinstance(field, models.ForeignKey):
                    if field.rel.to == State:
                        fields.append(field.name)
        for field in self.obj._meta.fields:
            if field.name in fields:
                data = {
                    "field": field,
                    "state": getattr(self.obj, field.name),
                    "workflow": getattr(self.obj, field.name).workflow,
                }
                names[field.name] = data
                workflows.append(data)
        return (workflows, names)

    def _lookup(self, name=None):
        if name is None and len(self.workflows) > 1:
            raise AttributeError, "There are mutliple workflows on this object"\
               " please specify which one you'd like to use."
        workflow = None
        if name:
            return self._names[name]
        else:
            return self.workflows[0]

    def get_state(self, name=None):
        workflow = self._lookup(name)
        return workflow["state"]

    def get_transitions(self, name=None):
        workflow = self._lookup(name)
        return workflow["state"].get_transitions(self.obj)
   
    def do_transition_by_id(self, id, name=None):
        workflow = self._lookup(name)
        transitions = workflow["state"].get_transitions(self.obj)
        id = int(id)
        transition = None
        for tr in transitions:
            if tr.id == id:
                transition = tr
        if not transition:
            raise ValueError, "No transition"
        newstate = workflow["state"].do_transition(self.obj, transition)
        # and now set
        workflow["state"] = newstate
        setattr(self.obj, workflow["field"].name, newstate)

    def do_transition(self, transition, name=None):
        workflow = self._lookup(name)
        transitions = workflow["state"].get_transitions(self.obj)
        if isinstance(transition, str):
            for tr in transitions:
                if tr.name == transition:
                    transition = tr
        assert transition in transitions
        newstate = workflow["state"].do_transition(self.obj, transition)
        # and now set
        workflow["state"] = newstate
        setattr(self.obj, workflow["field"].name, newstate)
