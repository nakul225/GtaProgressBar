'''
Created on Mar 20, 2017

@author: nakul
'''
import traceback
import sys
from src.models.Operation import Operation
from src.models.Goal import Goal
from src.models.Step import Step
from src.models.Category import Category

class CommandLineInterface:
    # Implementation that provides cmd line input/response interaction
    def __init__(self, providedLife):
        self.life = providedLife

    def _show_usage(self):
        print "\n==========================================================="
        print "Supported commands are:"
        print "Put Categories: \n\t pc <lowercase_category_name_without_spaces>"
        print "Get Categories: \n\t gc"
        print "Remove Categories: \n\t rc"
        print "Put Goals: \n\t pg <lowercase_goal_name_without_spaces>"
        print "Remove Goal: \n\t rg <lowercase_goal_name_without_spaces>"
        print "Put Step: \n\t ps <goal_name> <name> <cost_in_hours>"
        print "Remove Step: \n\t rs <goal_name> <step_name>"
        print "Get Goals: \n\t gg"
	print "Add Goal to Category: \n\t agc <lowercase_goal_name_without_space> <lowercase_category_name>"
        print "Remove Goal From Category: \n\t rgc <lowercase_goal_name_without_space> <lowercase_category_name>"
        print "Mark Step Complete: \n\t msc <goal_name> <step_name>"
        print "Mark Step Incomplete: \n\t msi <goal_name> <step_name>"
        print "Get Progress Summary: \n\t gps"
        print "Exit Program: \n\t exit"
        print "===========================================================\n"

    def _show_progress(self):
        #Iterates through each goal/category and shows progress for each one
        self._show_progress_for_goals()
        self._show_progress_for_categories()

    def _show_progress_for_goals(self):
        #Iterates through each goal and shows progress for each one
        for goal in self.life.get_goals():
            print "Goal " + goal.name + " is " + str(goal.get_progress_percentage()) + "% complete"

    def _show_progress_for_categories(self):
        #Iterates through each goal and shows progress for each one
        for category in self.life.get_categories():
            print "Category " + category.name + " has completed " + str(category.get_progress_percentage())

    def _process_command(self, command):
        lowercase_command = command.lower()
	if command == "":
		self._show_usage()
	 	return

        operation = lowercase_command.split()[0]
        continue_program = True

        if operation == Operation.EXIT.value:
            continue_program  = False
        elif operation == Operation.PUT_GOAL.value:
            self.put_goal(lowercase_command)
        elif operation == Operation.REMOVE_GOAL.value:
            self.remove_goal(lowercase_command)
        elif operation == Operation.GET_GOALS.value:
            self.get_goals(lowercase_command)
        elif operation == Operation.PUT_STEP.value:
            self.put_step(lowercase_command)
        elif operation == Operation.REMOVE_STEP.value:
            self.remove_step(lowercase_command)
        elif operation == Operation.GET_PROGRESS_SUMMARY.value:
            self.show_progress_summary()
        elif operation == Operation.MARK_STEP_COMPLETE.value:
            self.mark_step_complete(lowercase_command)
        elif operation == Operation.MARK_STEP_INCOMPLETE.value:
            self.mark_step_incomplete(lowercase_command)
        elif operation == Operation.PUT_CATEGORY.value:
            self.put_category(lowercase_command)
        elif operation == Operation.REMOVE_CATEGORY.value:
            self.remove_category(lowercase_command)
        elif operation == Operation.GET_CATEGORIES.value:
            self.get_categories(lowercase_command)
	elif operation == Operation.ADD_GOAL_TO_CATEGORY.value:
	    self.add_goal_to_category(lowercase_command)
        elif operation == Operation.REMOVE_GOAL_FROM_CATEGORY.value:
            self.remove_goal_from_category(lowercase_command)
        else:
            print "Operation not recognized. Please see usage:"
            self._show_usage()
        return continue_program

    def show_progress_summary(self):
        self._show_progress()

    def put_category(self, command):
        #PutCategory category_name
        tokens=command.split()
        name=tokens[1].lower()
        category=Category.build_new_category(name)
        self.life.put_category(category)

    def get_categories(self, command):
        # GetCategories
        if len(self.life.get_categories()) == 0:
            print "You don't have any categories in the system"
        else:
            print "You have following categories in the system:"
            for c in self.life.get_categories():
                c.print_details()

    def add_goal_to_category(self, command):
        #AddGoalToCategory goal_name category_name
	tokens = command.split()
	goal_name=tokens[1].lower()
	category_name=tokens[2].lower()
	self.life.add_goal_to_category(goal_name, category_name)	

    def remove_goal_from_category(self, command):
        elements = command.split()
        goal_name = elements[1].lower()
        category_name = elements[2].lower()
        self.life.remove_goal_from_category(goal_name, category_name)

    def remove_category(self, command):
        #RemoveCategory <category_name>
        tokens=command.split()
        name=tokens[1].lower()
        self.life.remove_category(name)

    def put_goal(self, command):
        #PutGoal <lowercase_goal_name_without_spaces> <lowercase_description_without_spaces>
        elements = command.split()
        name = elements[1].lower()
        description = "dummy_description"
        goal = Goal.build_new_goal(name, description)
        self.life.put_goal(goal)

    def remove_goal(self, command):
        #RemoveGoal <lowercase_goal_name_without_spaces>
        elements = command.split()
        name = elements[1].lower()
        self.life.remove_goal(name)
        
    def get_goals(self, command):
        if len(self.life.get_goals()) == 0:
            print "You don't have any goals in the system"
        else:
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

    def remove_step(self, command):
        # Remove step <lowercase_step_name> <lowercase_goal_name>
        tokens = command.split()
        step_name = tokens[2]
        goal_name = tokens[1]
        for goal in self.life.get_goals():
            if goal_name == goal.name:
                goal.remove_step(step_name)

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
                # Show progress bars
                goal.print_details()

    def mark_step_incomplete(self, command):
        elements = command.split()
        goal_name = elements[1]
        step_name = elements[2]
        print "Marking step "+ step_name + " in goal " + goal_name + " as INCOMPLETE"
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.mark_step_incomplete(step_name)
                # Show progress bars
                goal.print_details()

    def main_menu_loop(self):
        # Keeps the program running so that use can interact
        should_keep_loop_running = True
        while(should_keep_loop_running):
            try:
                should_keep_loop_running = self._show_usage_and_accept_user_input()
            except:
                print "Exception raised\n"
                traceback.print_exc(file=sys.stdout)

    def _process_single_command(self):
        # Useful to accept single command invoked with the program. This is alternative to having conitinous loop of accepting commands and showing output.
        try:
            actual_command = " ".join(sys.argv[1:])
            self._process_command(actual_command)
        except:
            print "Exception raised while dealing with input command: "+traceback.print_exc(file=sys.stdout)
            self._show_usage()
