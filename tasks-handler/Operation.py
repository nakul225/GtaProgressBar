'''
Created on Mar 20, 2017

@author: nakul
'''
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
