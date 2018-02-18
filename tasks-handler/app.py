from chalice import Chalice, Response
import boto3
import pickle

app = Chalice(app_name='tasks-handler')
app.debug=True

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/process/message', methods=['POST'])
def process_message():
    # Extract command from body
    request_body = app.current_request.json_body
    command = request_body["command"]
    username= request_body["username"]
    
    life = _load_life(username) 
    command_response = CommandLineInterface(life)._process_command(command)
    _write_to_ddb(username, life)

    response_body={"body":request_body, "result":command_response}
    return Response(body=response_body)
    
def _load_life(username):
    try: 
        return _load_from_ddb(username)
    except:
        return Life()

def _load_from_ddb(username):
    # Hardcoding table names here for now
    ddb = boto3.client('dynamodb')
    print ddb.list_tables()
    table_data = ddb.scan(TableName = "tasks_handler_life") # get all users because there's not many
    all_rows=table_data["Items"]
    user_life_data=""
    for row in all_rows:
        # Find row for given username
        if row['user_name']['S'] == username:
            # Found data for user
            user_life_data = row['data']['S']
            break
    life = pickle.loads(user_life_data)

def _write_to_ddb(username, life):
    ddb = boto3.client('dynamodb')
    data_to_be_written = pickle.dumps(life)
    ddb.put_item(TableName="tasks_handler_life", Item={"user_name":{"S":username},"data":{"S":data_to_be_written}})

########################################################################

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

    def add_goal(self, goal):
        return self.goals.append(goal)

    def remove_goal(self, goalname):
        for g in self._get_all_goals():
            if g.name == goalname:
                self.goals.remove(g)

    def get_progress_percentage(self):
        # Returns progress in percentage 
        total_progress = 0.0 # This will be percentage progress in each goal
        for goal in self._get_all_goals():
            total_progress += goal.get_progress_percentage()
            return total_progress/self._get_total_number_of_goals()

    def print_details(self):
        print "\n=========================================================="
        print "Category name: " + self.name,
        print " progress: " + str(self.get_progress_percentage()) + "%"

        if len(self.goals) != 0:
            print "Goals: "
        for goal in self.goals:
            print "------------------------------------------------------"
            print goal.name
        print "==========================================================\n"

    @staticmethod
    def build_new_category(name):
        guid = uuid.uuid4()
        return Category(guid, name)

####################################################################

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

###################################################################

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
                                        

##############################################################

from enum import Enum

class StepStatus(Enum):
    INCOMPLETE = 1
    COMPLETE = 2
    IN_PROGRESS = 3


#############################################################
from enum import Enum
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
        # count number of steps completed
        complete=int(self.get_progress_percentage()/10)
        remaining=10-complete

        print "\n=========================================================="
        print "Goal name: " + self.name,
        print " cost: " + str(self.get_total_cost_in_hours()),
        print " progress: " + str(self.get_progress_percentage()) + "%",
        print "[" + "#"*complete + "_"*remaining + "]"

                # Show incomplete tasks first 
        completed_steps=[s for s in self.steps if s.get_step_status() == StepStatus.COMPLETE]
        incomplete_steps=[s for s in self.steps if s.get_step_status() == StepStatus.INCOMPLETE]
        ordered_steps = incomplete_steps + completed_steps

        if len(self.steps) != 0:
            print "Steps: "
        for step in ordered_steps:
            #print "------------------------------------------------------"
            step.print_details()

        print "==========================================================\n"

    def put_step(self, step):
        self.steps.append(step)

    def get_steps(self):
        return self.steps

    def remove_step(self, step_name):
        for step in self.steps:
            if step.name == step_name:
                self.steps.remove(step)
                print "Removed step with name: ",step.name,"from the goal"
                return None
        print "Step with name:",step_name," not found"

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

###############################################################

from enum import Enum

class Operation(Enum):
    EXIT = 'exit'
    PUT_GOAL = 'pg'
    REMOVE_GOAL = "rg"
    GET_GOALS = 'gg'
    PUT_STEP = 'ps'
    GET_STEP = 'gs'
    REMOVE_STEP = "rs"
    GET_PROGRESS_SUMMARY = 'gps'
    MARK_STEP_COMPLETE = 'msc'
    MARK_STEP_INCOMPLETE = 'msi'
    PUT_CATEGORY = "pc"
    REMOVE_CATEGORY = "rc"
    GET_CATEGORIES = "gc"
    ADD_GOAL_TO_CATEGORY = "agc"
    REMOVE_GOAL_FROM_CATEGORY = "rgc"

##############################################################

import traceback
import sys

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

