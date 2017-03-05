
# coding: utf-8

# # Idea:
# * Classes that provide a way to create/update/remove goals. 
# * Every goal is comprised of steps and step forms the smallest possible action that be taken towards completion of a goal. 
# * Each goal can have multiple categories it fulfills.   
#      * For example, a goal can be fulfilling Health category and Social category at the same time.

# In[ ]:

from enum import Enum
import uuid
import datetime
import sys
import os
import traceback
import pickle


# In[ ]:

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
        print "=========================================================="
        print "id: " + self.id
        print "name: " + self.name
        print "description: " + self.description
        print "creation_date: " + self.creation_date
        print "cost: " + str(self.get_total_cost_in_hours())
        print "progress: " + str(self.get_progress_percentage()) + "%" 
        
        if len(self.steps) != 0:
            print "Steps: "
        for step in self.steps:
            print "------------------------------------------------------"
            step.print_details()
            
        print "=========================================================="
            
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


# In[ ]:

class StepStatus(Enum):
    INCOMPLETE = 1
    COMPLETE = 2
    IN_PROGRESS = 3

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
        print "id: " + self.id
        print "name: " + self.name
        print "description: " + self.description
        print "creation_date: " + self.creation
        print "cost: " + str(self.cost_in_hours)
        print "status: " + self.status.name
    
    @staticmethod
    def build_new_step(name, description, cost_in_hours):
        guid = uuid.uuid4()
        creation_date = datetime.datetime.now()
        return Step(guid, name, description, creation_date, cost_in_hours)


# In[ ]:

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
            return total_progress/_get_total_number_of_goals()
        
    @staticmethod
    def build_new_category(name):
        guid = uuid.uuid4()
        return Category(guid, name)


# In[ ]:

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
        
    def add_category(self, category):
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


# In[ ]:

class Operation(Enum):
    EXIT = 0
    PUT_GOAL = 1
    GET_GOALS = 2
    PUT_STEP = 3
    GET_STEP = 4
    GET_PROGRESS_SUMMARY = 5
    MARK_STEP_COMPLETE = 6
    MARK_STEP_INCOMPLETE = 7
    
class CommandLineInterface:
    # Implementation that provides cmd line input/response interaction
    def __init__(self, providedLife):
        self.life = providedLife
    
    def _show_usage(self):
        print "\n==========================================================="
        print "Supported commands are:"
        print "put_goal <lowercase_goal_name_without_spaces> <lowercase_description_without_spaces>"
        print "put_step <goal_name> <name> <cost_in_hours>"
        print "get_goals"
        print "mark_step_complete <goal_name> <step_name>"
        print "mark_step_incomplete <goal_name> <step_name>"
        print "get_progress_summary"
        print "exit : to exit program"
        print "===========================================================\n"
        
    def _show_progress(self):
        #Iterates through each goal/category and shows progress for each one
        self._show_progress_for_goals()
        self._show_progress_for_categories()
        
    def _show_progress_for_goals(self):
        #Iterates through each goal and shows progress for each one
        for goal in self.life.get_goals():
            print "Goal " + goal.name + " has completed " + str(goal.get_progress_percentage())
    
    def _show_progress_for_categories(self):
        #Iterates through each goal and shows progress for each one
        for category in self.life.get_categories():
            print "Category " + category.name + "has completed " + str(category.get_progress_percentage())
    
    def _read_input_and_process(self):
        command = raw_input("Please enter choice of action: ")
	os.system('clear') 
        lowercase_command = command.lower()
        operation = lowercase_command.split()[0]
        continue_program = True
        if operation == Operation.EXIT.name.lower():
            continue_program  = False
        elif operation == Operation.PUT_GOAL.name.lower():
            self.put_goal(lowercase_command)
        elif operation == Operation.GET_GOALS.name.lower():
            self.get_goals(lowercase_command)
        elif operation == Operation.PUT_STEP.name.lower():
            self.put_step(lowercase_command)
        elif operation == Operation.GET_PROGRESS_SUMMARY.name.lower():
            self.show_progress_summary()
        elif operation == Operation.MARK_STEP_COMPLETE.name.lower():
            self.mark_step_complete(lowercase_command)
        elif operation == Operation.MARK_STEP_INCOMPLETE.name.lower():
            self.mark_step_incomplete(lowercase_command)
        return continue_program 
    
    def show_progress_summary(self):
        self._show_progress()
    
    def put_goal(self, command):
        #PutGoal <lowercase_goal_name_without_spaces> <lowercase_description_without_spaces>
        elements = command.split()
        name = elements[1].lower()
        description = elements[2].lower()
        goal = Goal.build_new_goal(name, description)
        self.life.put_goal(goal)
        
    def get_goals(self, command):
        print "You have following goals in the system: "
        for goal in self.life.get_goals():
            goal.print_details()
            
    def put_step(self, command):
        #PutStep <name> <description> <cost_in_hours> <name_of_goal>
        elements = command.split()
        goal_name = elements[1].lower()
        name = elements[2].lower()
        description = ""
        cost = int(elements[3])
        step = Step.build_new_step(name, description, cost)
        # Find the goal in life and add this step to it.
        success = False
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.put_step(step)
                success=True
        if success == False:
            print "Specified goal not found!"
    
    def _show_usage_and_accept_user_input(self):
        # Show usage and accept user input
        self._show_usage()
        continue_flag = self._read_input_and_process()
        return continue_flag
        
    def mark_step_complete(self, command):
        elements = command.split()
        goal_name = elements[1]
        step_name = elements[2]
        print "Marking step "+ step_name + " in goal " + goal_name + " as COMPLETE"
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.mark_step_complete(step_name)
        
    def mark_step_incomplete(self, command):
        elements = command.split()
        goal_name = elements[1]
        step_name = elements[2]
        print "Marking step "+ step_name + " in goal " + goal_name + " as INCOMPLETE"
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.mark_step_incomplee(step_name)
        
    def main_menu_loop(self):
         # Keeps the program running so that use can interact
        should_keep_loop_running = True
        while(should_keep_loop_running):
            try:
                should_keep_loop_running = self._show_usage_and_accept_user_input()
            except:
                print "Exception raised\n"
                traceback.print_exc(file=sys.stdout)

# In[ ]:

def main():
    #initialize
    life_filename = "./gta.data"
    try:
        life = _load_from_file(life_filename)
        print "Loading life from datastore"
    except:
        #traceback.print_exc(file=sys.stdout)
        print "Couldn't load life from datastore, creating a new life"
        life = Life()
        
    # start main loop
    CommandLineInterface(life).main_menu_loop()
    
    #persist data
    try:
        _save_to_file(life, life_filename)
    except:
        traceback.print_exc(file=sys.stdout)

def _load_from_file(filename):
    # If files don't exist, return empty list
    return_value = None
    with open(filename, 'rb') as f:
        return_value = pickle.load(f)
    return return_value
    
def _save_to_file(domain_object, filename):
    with open(filename, 'wb') as f:
        pickle.dump(domain_object, f)

if __name__ == "__main__":
        main()


# In[ ]:



