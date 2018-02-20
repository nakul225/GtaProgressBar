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
    command_response=None
    request_body = app.current_request.json_body
    command = request_body["command"]
    username= request_body["username"]
    
    life = _load_life(username) 
    cli=CommandLineInterface(life)
    command_response=cli.process_command(command)
    _write_to_ddb(username, life)

    response_body={"request":request_body, "result":command_response}
    return Response(body=response_body)
    
def _load_life(username):
    try: 
        life = _load_from_ddb(username)
        print "Successfully loaded life instance from datastore: " + str(life)
    except Exception as e:
        life = Life()
        print "Caught exception, so creating a new Life instance, exception message: " + str(e)

    if life is None:
        print "Life is None even after loading from datastore, creating a new one"
        life = Life()
    return life

def _load_from_ddb(username):
    ddb = boto3.client('dynamodb')
    print ">> Reading goals from table"
    goals=_read_goals(ddb, username)
    print ">> Reading categories from table"
    categories=_read_categories(ddb, username)
    print ">>Loaded following goals and categories from ddb:"
    print goals
    print categories
    life = Life()
    life.goals = goals
    life.categories = categories
    return life

def _read_goals(ddb, username):
    table_data = ddb.scan(TableName = "tasks_handler_goals")
    all_rows=table_data["Items"]
    user_goals=[]
    for row in all_rows:
        # Find row for given username
        if row['user_name']['S'] == username:
            # Found data for user
            data = row['data']['S']
            #print ">>> Deserializing goal data: " + str(data)
            goal = pickle.loads(data)
            #print ">>> goal_dict:" + goal.get_details()
            user_goals.append(goal)
    return user_goals

def _write_goals(ddb, username, goals):
    print ">> Write_goals, goals:" + str(goals)
    for goal in goals:
        data_to_be_written = pickle.dumps(goal)
        ddb.put_item(TableName="tasks_handler_goals", Item={"user_name":{"S":username},"goal_name":{"S":goal.get_name()},"data":{"S":data_to_be_written}})

def _read_categories(ddb, username):
    table_data = ddb.scan(TableName = "tasks_handler_categories")
    all_rows = table_data["Items"]
    user_categories_data=[]
    for row in all_rows:
        if row['user_name']['S'] == username:
            category = pickle.loads(row['data']['S'])
            user_categories_data.append(category)
    return user_categories_data

def _write_categories(ddb, username, categories):
    for category in categories:
        data_to_be_written = pickle.dumps(category)
        ddb.put_item(TableName="tasks_handler_categories", Item={"user_name":{"S":username},"category_name":{"S":category.get_name()},"data":{"S":data_to_be_written}})

def _write_to_ddb(username, life):
    ddb = boto3.client('dynamodb')
    # Write a new row for each goal
    _write_goals(ddb, username, life.get_goals())
    _write_categories(ddb, username, life.get_categories())
########################################################################

import uuid

class Category:
    def __init__(self, guid, name):
        self.id=str(guid) #UUID
        self.name=name
        self.goals=[]
	
    def get_name(self):
	return self.name
	
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

    def get_details(self):
	response = {}
	goals_data = {}
	for goal in self.goals:
		goals_data[goal.get_name()] = goal.get_details()
	response["name"]=self.name
	response["progress"]=str(self.get_progress_percentage()) + "%"
	response["goals"]=goals_data
	return response

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

    def get_name(self):
	return self.name

    def get_details(self):
	return {"name":self.name,"cost":self.cost_in_hours,"status":self.status.name}

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

    def get_all_goals_details():
	response = {}
	for goal in self.goals:
		response[goal.get_name()] = goal.get_details()
	return response

    def get_all_categories_details():
	response = {}
	for category in self.categories:
		response[category.get_name()] = category.get_details()
	return response

    def put_goal(self, goal):
        goal_exists = self._search_goal(goal)
        if goal_exists:
            print "Goal",goal.name,"already exists, won't create a new one"
        else:
            self.goals.append(goal)
	return goal.get_details()

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

    def get_name(self):
	return self.name

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

    def get_details(self):
        response={}
	#progress data
        complete=int(self.get_progress_percentage()/10)
        remaining=10-complete
        response["name"]=self.name
        response["cost"]=str(self.get_total_cost_in_hours())
        response["progress"]=str(self.get_progress_percentage()) + "%"
        response["progress_bar"]="[" + "#"*complete + "_"*remaining + "]"
	response["steps"]=self.get_all_steps_details()	
	return response

    def get_all_steps_details(self):
	steps_data={}
	for step in self.get_steps():
                steps_data[step.get_name()] = step.get_details()
	return steps_data

    def put_step(self, step):
        self.steps.append(step)
	return self.get_details()
	
    def get_steps(self):
	completed_steps=[s for s in self.steps if s.get_step_status() == StepStatus.COMPLETE]
        incomplete_steps=[s for s in self.steps if s.get_step_status() == StepStatus.INCOMPLETE]
        ordered_steps = incomplete_steps + completed_steps

        return ordered_steps

    def remove_step(self, step_name):
	flag = False
        for step in self.steps:
            if step.name == step_name:
                self.steps.remove(step)
                print "Removed step with name: ",step.name,"from the goal"
		flag = True
		break
        print "Step with name:",step_name," not found"
	if flag:
		return {"result":"success", "details":self.get_details()}
	else:
		return {"result":"failure", "reason":"step_not_found"}

    def mark_step_complete(self, step_name):
        #Finds step by name and marks it complete
        for step in self.get_steps():
            if step.name == step_name:
                step.mark_step_complete()
	return self.get_details()

    def mark_step_incomplete(self, step_name):
        #Finds step by name and marks it incomplete
        for step in self.get_steps():
            if step.name == step_name:
                step.mark_step_incomplete()
	return self.get_details()

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

class TaskHandlerResponse:
    def __init__(self, input_message):
        self.message = {"message":input_message}

    def get_body(self):
        return self.message
##############################################################

import traceback
import sys

class CommandLineInterface:
    # Implementation that provides cmd line input/response interaction
    def __init__(self, providedLife):
        self.life = providedLife
        print ">>> Initiating life: " + str(self.life)

    def usage(self):
        return {
                "pc":"put categories -- pc <category_name>",
                "gc":"get categories -- gc",
                "rc":"remove categories -- rc <category_name>",
                "pg":"put goals -- pg <goal_name>",
                "rg":"remove goals -- rg <goal_name>",
                "ps":"put step -- ps <goal_name> <name> <cost_in_hours>",
                "rs":"remove step -- rs <goal_name> <step_name>",
                "gg":"get goals -- gg",
                "agc":"add goals to category -- agc <goal_name> <category_name>",
                "rgc":"remove goals from category -- rgc <goal_name> <category_name>",
                "msc":"mark step complete -- msc <goal_name> <step_name>",
                "msi":"mark step incomplete -- msi <goal_name> <step_name>"}

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
        response = {}
        goals_response = self._show_progress_for_goals()
        categories_response = self._show_progress_for_categories()
        response["goals_progress"] = goals_response
        response["categories_progress"] = categories_response
        return response

    def _show_progress_for_goals(self):
        #Iterates through each goal and shows progress for each one
        response = {}
        for goal in self.life.get_goals():
            print "Goal " + goal.name + " is " + str(goal.get_progress_percentage()) + "% complete"
            response[goal.name] = str(goal.get_progress_percentage()) + "% complete"
        return response

    def _show_progress_for_categories(self):
        #Iterates through each goal and shows progress for each one
        response = {}
        for category in self.life.get_categories():
            #print "Category " + category.name + " has completed " + str(category.get_progress_percentage())
            response[category.name] = str(category.get_progress_percentage())
        return response

    def process_command(self, command):
        lowercase_command = command.lower()
        #if command == "":
        #        self._show_usage()
        #        return

        operation = lowercase_command.split()[0]
        #continue_program = True

        try:
            if operation == Operation.EXIT.value:
                #continue_program  = False
                pass
            elif operation == Operation.PUT_GOAL.value:
                response = self.put_goal(lowercase_command)
            elif operation == Operation.REMOVE_GOAL.value:
                response = self.remove_goal(lowercase_command)
            elif operation == Operation.GET_GOALS.value:
                response = self.get_goals(lowercase_command)
            elif operation == Operation.PUT_STEP.value:
                response = self.put_step(lowercase_command)
            elif operation == Operation.REMOVE_STEP.value:
                response = self.remove_step(lowercase_command)
            elif operation == Operation.GET_PROGRESS_SUMMARY.value:
                response = self.show_progress_summary()
            elif operation == Operation.MARK_STEP_COMPLETE.value:
                response = self.mark_step_complete(lowercase_command)
            elif operation == Operation.MARK_STEP_INCOMPLETE.value:
                response = self.mark_step_incomplete(lowercase_command)
            elif operation == Operation.PUT_CATEGORY.value:
                response = self.put_category(lowercase_command)
            elif operation == Operation.REMOVE_CATEGORY.value:
                response = self.remove_category(lowercase_command)
            elif operation == Operation.GET_CATEGORIES.value:
                response = self.get_categories(lowercase_command)
            elif operation == Operation.ADD_GOAL_TO_CATEGORY.value:
                response = self.add_goal_to_category(lowercase_command)
            elif operation == Operation.REMOVE_GOAL_FROM_CATEGORY.value:
                response = self.remove_goal_from_category(lowercase_command)
            else:
                print "Operation not recognized. Please see usage:"
                #self._show_usage()
                response = self.usage()
        except Exception as e:
            #{"result":"exception_testing"} 
            response = {"exception": str(e)}
            traceback.print_exc(file=sys.stdout)
        result = {"response_message": response}
        return result
                                             
    def show_progress_summary(self):
        self._show_progress()

    def put_category(self, command):
        #PutCategory category_name
        tokens=command.split()
        name=tokens[1].lower()
        category=Category.build_new_category(name)
        return self.life.put_category(category)

    def get_categories(self, command):
        # GetCategories
        if len(self.life.get_categories()) == 0:
            print "You don't have any categories in the system"
        else:
            print "You have following categories in the system:"
            for c in self.life.get_categories():
                c.print_details()
        #TODO

    def add_goal_to_category(self, command):
        #AddGoalToCategory goal_name category_name
        tokens = command.split()
        goal_name=tokens[1].lower()
        category_name=tokens[2].lower()
        return self.life.add_goal_to_category(goal_name, category_name)

    def remove_goal_from_category(self, command):
        elements = command.split()
        goal_name = elements[1].lower()
        category_name = elements[2].lower()
        return self.life.remove_goal_from_category(goal_name, category_name)

    def remove_category(self, command):
        #RemoveCategory <category_name>
        tokens=command.split()
        name=tokens[1].lower()
        return self.life.remove_category(name)

    def put_goal(self, command):
        #PutGoal <lowercase_goal_name_without_spaces> <lowercase_description_without_spaces>
        elements = command.split()
        name = elements[1].lower()
        description = "dummy_description"
        goal = Goal.build_new_goal(name, description)
        return self.life.put_goal(goal)

    def remove_goal(self, command):
        #RemoveGoal <lowercase_goal_name_without_spaces>
        elements = command.split()
        name = elements[1].lower()
        return self.life.remove_goal(name)

    def get_goals(self, command):
        response = {}
        goals_data={}
        if len(self.life.get_goals()) == 0:
            print "You don't have any goals in the system"
            response = {"result":"failure", "reason":"no_goals_found"}
        else:
            print "You have following goals in the system: "
            for goal in self.life.get_goals():
                goal.print_details()
                goals_data[goal.get_name()]=goal.get_details()
        response = {"result":"success","goals":goals_data}
        return response

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
        response = {}
        response["result"]="success"
        response["goal"]=goal_name
        response["step"]=name
        response["cost"]=cost
        return response

    def remove_step(self, command):
        # Remove step <lowercase_step_name> <lowercase_goal_name>
        tokens = command.split()
        step_name = tokens[2]
        goal_name = tokens[1]
        flag=False
        for goal in self.life.get_goals():
            if goal_name == goal.name:
                goal.remove_step(step_name)
                flag=True
                break
        if flag:
            return {"result":"success"}
        else:
            return {"result":"failure", "reason":"step_not_found"}

    def _show_usage_and_accept_user_input(self):
        # Show usage and accept user input
        self._show_usage()
        continue_flag = self._read_input_and_process()
        return continue_flag

    def mark_step_complete(self, command):
        elements = command.split()
        goal_name = elements[1]
        step_name = elements[2]
        flag = False
        details = {}
        print "Marking step "+ step_name + " in goal " + goal_name + " as COMPLETE"
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.mark_step_complete(step_name)
                # Show progress bars
                goal.print_details()
                details = goal.get_details()
                flag = True
                break
        if flag:
            return {"result":"success","step":step_name,"status":"complete","goal":details}
        else:
            return {"result":"failure","reason":"goal_not_found"}

    def mark_step_incomplete(self, command):
        elements = command.split()
        goal_name = elements[1]
        step_name = elements[2]
        flag = False
        details = {}
        print "Marking step "+ step_name + " in goal " + goal_name + " as INCOMPLETE"
        for goal in self.life.get_goals():
            if goal.name == goal_name:
                goal.mark_step_incomplete(step_name)
                # Show progress bars
                goal.print_details()
                details=goal.get_details()
                flag =True
                break
        if flag:
            return {"result":"success","step":step_name,"status":"incomplete","goal":details}
        else:
            return {"result":"failure", "reason":"goal_not_found"}

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
            self.process_command(actual_command)
        except:
            print "Exception raised while dealing with input command: "+traceback.print_exc(file=sys.stdout)
            self._show_usage()

