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
            print "Goal",goal.name,"already exists, won't create a new one"
        else:
            self.goals.append(goal)

    def remove_goal(self, goal_name):
        goal_exists = self._search_goal_by_name(goal_name)
        if goal_exists:
            print "Goal",goal_name,"exists, removing"
            for goal in self.goals:
                if goal.name == goal_name:
                    self.goals.remove(goal)
                    print "Goal removed from goals list, now removing from categories"
                    for c in self.categories:
                        c.remove_goal(goal)
        else:
            print "Goal",goal_name,"doesn't exist, nothing to remove"

    def put_category(self, category):
	category_exists = self._search_category(category)
	if category_exists:
	    print "Category",category.name,"already exists, won't create a new one"
        else:
            self.categories.append(category)

    def remove_category(self, category_name):
        category_exists = self._search_category_by_name(category_name)
        if category_exists:
            print "Category",category_name,"exists, removing"
            for category in self.categories:
                if category.name == category_name:
                    self.categories.remove(category)
                    print "Category removed"
        else:
            print "Category",category_name,"doesn't exist"

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

    def _search_goal_by_name(self, name):
        for g in self.goals:
            if g.name == name:
                return True
        return False

    def _search_category(self, category):
	for c in self.categories:
	    if c.name == category.name:
		return True
	return False

    def _search_category_by_name(self, category_name):
        for c in self.categories:
            if c.name == category_name:
                return True
        return False

    def add_goal_to_category(self, goalname, categoryname):
	# Verify goal and category exists
	goal_exists = False
	category_exists = False
	for g in self.goals:
		if g.name == goalname:
			goal_exists = True
	for c in self.categories:
		if c.name == categoryname:
			category_exists = True
	
	if not goal_exists and not category_exists:
		print "Either goal or category doesn't exist, goal_exists:" + goal_exists + " and category_exists:" + category_exists
	else:
		# Both exist, so create the connection
		goal=None
		for g in self.goals:
			if g.name == goalname:
				goal = g		

		for c in self.categories:
			if c.name == categoryname:
				c.add_goal(goal)

    def remove_goal_from_category(self, goalname, categoryname):
        goal_exists = self._search_goal_by_name(goalname)
        category_exists = self._search_category_by_name(categoryname)
        if goal_exists and category_exists:
            for c in self.categories:
                if c.name == categoryname:
                    c.remove_goal(goalname)
                    print "Removed goal:",goalname,"from category:",categoryname
        else:
            print "Either goal or category doesn't exist"

    @staticmethod
    def build_new_life():
        return Life()
