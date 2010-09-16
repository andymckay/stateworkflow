# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

State Workflow
=======================

Is a simple rip off of the DCWorkflow that Plone uses, DCWorkflow originally coming from Digital Creations many moons ago. Anyway I always liked it because its very simple and abstracts quite a few things away from the class, letting admin's decide how things happen. The gaol of this state workflow is to:

- put any number of workflows on a model

- the workflow can contain mulitple states

- there can be multiple transitions between the workflows

- conditions (well scripts) are checked before a transition is run

- scripts are run in the transition 

Workflows can be constructed through the admin interface, or through scripts. The admin interface is a little rough and you can't actually workflow things in it. Since it doesn't check which scripts can be assigned to which workflow, or look for changes, but since I don't actually want to use the admin interface, I'm not too worried about that.

Users don't actually get to write any scripts. Scripts are created by the admin and given descriptions, the admins can then decide which script to assign to which transition and when. There are two kinds of (optional) scripts:

- permission: this is to check the object can be transitioned and gets passed the object and the transition. If you want other things like request or user, you might have to use threadlocals or other hacks to get them. If any of the assigned permission scripts does not return True (or anything evaluating as True), then it fails.

- do: this is what happens when the script is run and involves changing things, logging, emailing that sort of thing. Script gets passed the object and the transition. Returns ignored, if there's a problem raise an error.

The unit tests explain this better than some text, but here's a brief synopsis:

- news item workflow, three states: private, pending, published. Someone in the office needs to review it before it goes live. Also all the fields have to be filled out. If you'd like to see this, loaddata: test.json.

- example permission script assigned to the review transition, ie you can't workflow to review until you fill these out:

    def check_complete(obj, transition):
        for field in ["title", "description"]:
            if not getattr(obj, field):
                return False
        return True 

- so here's out news item:
                                       
    from stateworkflow.models.state import State

    class NewsItem(models.Model):
        title = models.CharField(max_length=255)
        description = models.TextField()
        published_date = models.DateTimeField(blank=True, null=True)
        state = models.ForeignKey(State)   

- you can do all this manually (see unit tests) or try the following WorkflowManager a nice wrapper around it all

    from stateworkflow.workflowmanager import WorkflowManager

    self.one = NewsItem()
    self.one.state = Workflow.objects.get(id=2).default_state # this is our news item worklow
    self.one.save()  
    assert self.one.state.name == "Private"
    assert len(self.one.state.get_transitions(self.one)) == 0 
    
    # hmm this is a bit cumbersome, flip to workflowmanager
    # at the moment we can't transition
    self.one.title = "Hello"
    self.one.description = "This is a description"
    self.one.save()
    
    # we should now be to transition
    wf = WorkflowManager(self.one)
    wf.do_transition("Request review")
    # we are now pending
    assert wf.get_state() == self.one.state
    assert wf.get_state().name == "Pending"
 
That's it, see unit tests for more.
   
Todo: 

- custom widget so it works nicely in admin

- allow setting of script order

- more will come as we use it I'm sure

