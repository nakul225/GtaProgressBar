'''
Created on Mar 20, 2017

@author: nakul
'''
from StepStatus import StepStatus
import uuid
import datetime

class Step:
    def __init__(self, guid, name, description, creation_date, cost):
        self.id= str(guid) #UUID
        self.creation = str(creation_date)
        self.cost_in_hours = cost
        self.name = name
        self.description = description
        self.mark_step_incomplete()

    def get_step_status(self):
        return self.status

    def get_cost(self):
        return self.cost_in_hours

    def mark_step_incomplete(self):
        self.status = StepStatus.INCOMPLETE

    def mark_step_complete(self):
        self.status = StepStatus.COMPLETE

    def print_details(self):
        print " " + self.name,
        print " cost: " + str(self.cost_in_hours),
        print " status: " + self.status.name

    @staticmethod
    def build_new_step(name, description, cost_in_hours):
        guid = uuid.uuid4()
        creation_date = datetime.datetime.now()
        return Step(guid, name, description, creation_date, cost_in_hours)
