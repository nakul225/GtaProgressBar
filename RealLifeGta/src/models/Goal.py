'''
Created on Mar 20, 2017

@author: nakul
'''
from enum import Enum
from StepStatus import StepStatus
import uuid
import datetime

class Goal:
    class GoalStatus(Enum):
        INCOMPLETE = 1
        COMPLETE = 2
        IN_PROGRESS = 3

    def __init__(self, guid, creation_date, name, description):
        self.steps=[]
        self.id = str(guid)
        self.creation_date = str(creation_date)
        self.cost_in_hours = 0
        self.categories = []
        self.name = name
        self.description= description

    def _get_total_num_of_steps(self):
        return len(self.steps)

    def get_total_cost_in_hours(self):
        cost = 0
        for step in self.steps:
            cost += step.get_cost()
        return cost

    def _get_num_of_steps_completed(self):
        completed = 0
        for step in self.steps:
            if step.get_step_status() == StepStatus.COMPLETE:
                completed += 1
        return completed

    def get_progress_percentage(self):
        if self._get_total_num_of_steps() == 0:
            return 0.0
        return (self._get_num_of_steps_completed()*1.0 / self._get_total_num_of_steps()) * 100

    def print_details(self):
        print "\n=========================================================="
        print "Goal name: " + self.name,
        print " cost: " + str(self.get_total_cost_in_hours()),
        print " progress: " + str(self.get_progress_percentage()) + "%"

        if len(self.steps) != 0:
            print "Steps: "
        for step in self.steps:
            print "------------------------------------------------------"
            step.print_details()

        print "==========================================================\n"

    def put_step(self, step):
        self.steps.append(step)

    def get_steps(self):
        return self.steps

    def mark_step_complete(self, step_name):
        #Finds step by name and marks it complete
        for step in self.get_steps():
            if step.name == step_name:
                step.mark_step_complete()

    def mark_step_incomplete(self, step_name):
        #Finds step by name and marks it incomplete
        for step in self.get_steps():
            if step.name == step_name:
                step.mark_step_incomplete()

    @staticmethod
    def build_new_goal(name, description):
        guid = uuid.uuid4()
        creation_date = datetime.datetime.now()
        return Goal(guid, creation_date, name, description)

