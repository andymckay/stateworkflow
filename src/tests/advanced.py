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
from stateworkflow.workflowmanager import WorkflowManager

from django.db import models
from django.db import connection

def check_complete(obj, transition):
    for field in ["title", "description"]:
        if not getattr(obj, field):
            return False
    return True

def set_published_date(obj, transition):
    from datetime import datetime
    obj.published_date = datetime.now()
    obj.save()

register("check_complete", "Check news item is complete", check_complete)
register("set_published_date", "Set the published date on the news item", set_published_date)

class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    published_date = models.DateTimeField(blank=True, null=True)
    state = models.ForeignKey(State)

    class Meta:
        app_label = "stateworkflow"

class advanced(TestCase):
    fixtures = ["test.json", ]

    def setUp(self):
        self.one = NewsItem()
        self.one.state = Workflow.objects.get(id=2).default_state
        self.one.save()

        self.two = NewsItem()
        self.two.state = Workflow.objects.get(id=2).default_state
        self.two.save()

    def testCantWorkflow(self):
        assert self.one.state.name == "Private"
        assert len(self.one.state.get_transitions(self.one)) == 0
        self.one.title = "Hello"
        self.one.description = "This is a description"
        assert len(self.one.state.get_transitions(self.one)) == 1
        self.one.description = ""
        assert len(self.one.state.get_transitions(self.one)) == 0

    def testReview(self):
        self.one.title = "Hello"
        self.one.description = "This is a description"
        self.one.save()
        transitions = self.one.state.get_transitions(self.one)
        assert len(transitions) == 1
        # just to check its coping with objects in different states
        assert len(self.two.state.get_transitions(self.two)) == 0
        self.one.state = self.one.state.do_transition(self.one, transitions[0])
        assert self.one.state.name == "Pending"

    def testReviewAndPublish(self):
        self.testReview()
        self.one.save()
        transitions = self.one.state.get_transitions(self.one)
        assert len(transitions) == 2
        # just to check its coping with objects in different states
        assert len(self.two.state.get_transitions(self.two)) == 0
        assert not self.one.published_date
        self.one.state = self.one.state.do_transition(self.one, transitions[0])
        assert self.one.state.name == "Published"
        assert self.one.published_date

    def testReviewAndRetract(self):
        self.testReview()
        self.one.save()
        transitions = self.one.state.get_transitions(self.one)
        assert len(transitions) == 2
        # just to check its coping with objects in different states
        assert len(self.two.state.get_transitions(self.two)) == 0
        assert not self.one.published_date
        self.one.state = self.one.state.do_transition(self.one, transitions[1])
        assert self.one.state.name == "Private"
        assert not self.one.published_date

    def testWorkflowManagerBasic(self):
        self.one.title = "Hello"
        self.one.description = "This is a description"
        self.one.save()

        # this is a little bit cleaner imho
        wf = WorkflowManager(self.one)
        assert len(wf.get_transitions()) == 1
        wf.do_transition("Request review")

        assert wf.get_state() == self.one.state
        assert wf.get_state().name == "Pending"
