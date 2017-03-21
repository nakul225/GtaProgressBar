'''
Created on Mar 20, 2017

@author: nakul
'''
import uuid

class Category:
    def __init__(self, guid, name):
        self.id=str(guid) #UUID
        self.name=name
        self.goals=[]

    def _get_total_number_of_goals(self):
        return len(self.goals)

    def _get_all_goals(self):
        return self.goals

    def get_progress_percentage(self):
        # Returns progress in percentage 
        total_progress = 0.0 # This will be percentage progress in each goal
        for goal in self._get_all_goals():
            total_progress += goal.get_progress_percentage()
            return total_progress/self._get_total_number_of_goals()

    @staticmethod
    def build_new_category(name):
        guid = uuid.uuid4()
        return Category(guid, name)
