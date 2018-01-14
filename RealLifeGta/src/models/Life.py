'''
Created on Mar 20, 2017

@author: nakul
'''
class Life:
    def __init__(self):
        self.categories = []
        self.goals = []

    def put_goal(self, goal):
        goal_exists = self._search_goal(goal)
        if goal_exists:
            print "Goal ", goal.name, " already exists, won't create a new one"
        else:
            self.goals.append(goal)

    def put_category(self, category):
        self.categories.append(category)

    def get_goals(self):
        return self.goals

    def get_categories(self):
        return self.categories

    def _get_total_num_of_categories(self):
        return len(self.categories)

    def _get_total_num_of_goals(self):
        return len(self.goals)

    def _search_goal(self, goal):
        for g in self.goals:
            if g.name == goal.name:
                return True
        return False

    @staticmethod
    def build_new_life():
        return Life()
