# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

from django.test import TestCase

from stateworkflow.models.state import State
from stateworkflow.models.script import Script, register, admin_registry
from stateworkflow.models.transition import Transition
from stateworkflow.models.workflow import Workflow

from django.db import models
from django.db import connection

class Stub(models.Model):
    name = models.TextField(max_length=255)
    workflow = models.ForeignKey(Workflow)
    state = models.ForeignKey(State)

    class Meta:
        app_label = "stateworkflow"

def hello_world(*args, **kw):
    print "hello_world"

def null(*args, **kw):
    return True

def error(*args, **kw):
    raise WorkflowScriptError

register("null", "Null script, will do nothing", null)
register("error", "Error script, will just raise an error", null)

class basic(TestCase):
    fixtures = ["test.json", ]

    def setUp(self):
        self.workflow = Workflow.objects.get(id=1)
        self.states = {}
        for state in self.workflow.state_set.all():
            self.states[state.name] = state
        self.transitions = Transition.objects.all()

    def _create_workflow(self):
        workflow = Workflow()
        workflow.name = "Test"
        workflow.save()
        self.workflow = workflow

    def _create_states(self):
        self.states = {}
        for name in ["Active", "Inactive"]:
            state = State()
            state.name = name
            state.workflow = self.workflow
            state.save()
            self.states[name] = state

    def _create_transitions(self):
        self.transitions = {}
        transition = Transition()
        transition.name = "Deactivate"
        transition.starting_state = self.states["Active"]
        transition.ending_state = self.states["Inactive"]
        transition.save()
        self.transitions["Deactivate"] = transition

        transition = Transition()
        transition.name = "Activate"
        transition.starting_state = self.states["Inactive"]
        transition.ending_state = self.states["Active"]
        transition.save()
        self.transitions["Activate"] = transition

    def _create_basic(self):
        self._create_workflow()
        self._create_states()
        self._create_transitions()

    def _create_stub(self):
        stub = Stub()
        stub.name = "Test stub"
        stub.workflow = self.workflow
        stub.state = self.workflow.default_state
        stub.save()
        self.stub = stub

    def test_basic(self):
        # done by fixtures now
        # self._createBasic()
        pass

    def test_set_default_state(self):
        # done by fixtures now
        # self.workflow.default_state = self.states["Active"]
        # self.workflow.save()
        pass

    def test_stub(self):
        self._create_stub()
        assert self.stub.state.name == "Active"

    def test_states(self):
        assert [ s.name for s in self.workflow.state_set.all().order_by("name") ] == ["Active", "Inactive"]

    def test_transition(self):
        self.workflow.default_state = self.states["Active"]
        self._create_stub()
        transitions = self.stub.state.get_transitions(self.stub)
        assert len(transitions) == 1, "Got %s transitions" % len(transitions)
        self.stub.state = self.stub.state.do_transition(self.stub, transitions[0])
        assert self.stub.state == self.states["Inactive"]

    def test_script_registry(self):
        assert len(admin_registry) == 4
        register("hello", "hello world", hello_world)
        assert len(admin_registry) == 5




