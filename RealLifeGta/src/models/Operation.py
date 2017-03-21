'''
Created on Mar 20, 2017

@author: nakul
'''
from enum import Enum

class Operation(Enum):
    EXIT = 'exit'
    PUT_GOAL = 'pg'
    GET_GOALS = 'gg'
    PUT_STEP = 'ps'
    GET_STEP = 'gs'
    GET_PROGRESS_SUMMARY = 'gps'
    MARK_STEP_COMPLETE = 'msc'
    MARK_STEP_INCOMPLETE = 'msi'
