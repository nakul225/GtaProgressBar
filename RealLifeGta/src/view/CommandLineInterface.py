'''
Created on Mar 20, 2017

@author: nakul
'''
import traceback
import sys
from src.models.Operation import Operation
from src.models.Goal import Goal
from src.models.Step import Step

class CommandLineInterface:
    # Implementation that provides cmd line input/response interaction
    def __init__(self, providedLife):
        self.life = providedLife

    def _show_usage(self):
        print "\n==========================================================="
        print "Supported commands are:"
        print "Put Goals: \n\t pg <lowercase_goal_name_without_spaces> <lowercase_description_without_spaces>"
        print "Put Step: \n\t ps <goal_name> <name> <cost_in_hours>"
        print "Get Goals: \n\t gg"
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
            print "Category " + category.name + "has completed " + str(category.get_progress_percentage())

    def _process_command(self, command):
        lowercase_command = command.lower()
        operation = lowercase_command.split()[0]
        continue_program = True

        if operation == Operation.EXIT.value:
            continue_program  = False
        elif operation == Operation.PUT_GOAL.value:
            self.put_goal(lowercase_command)
        elif operation == Operation.GET_GOALS.value:
            self.get_goals(lowercase_command)
        elif operation == Operation.PUT_STEP.value:
            self.put_step(lowercase_command)
        elif operation == Operation.GET_PROGRESS_SUMMARY.value:
            self.show_progress_summary()
        elif operation == Operation.MARK_STEP_COMPLETE.value:
            self.mark_step_complete(lowercase_command)
        elif operation == Operation.MARK_STEP_INCOMPLETE.value:
            self.mark_step_incomplete(lowercase_command)
        else:
            print "Operation not recognized. Please see usage:"
            self._show_usage()
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
                goal.mark_step_incomplete(step_name)

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
            print "Exception raised while dealing with input command"
            self._show_usage()
