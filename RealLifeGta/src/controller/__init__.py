import traceback
import sys
import pickle
import os
from src.models.Life import Life
from src.view.CommandLineInterface import CommandLineInterface

def main():
    #initialize
    life_filename = "/home/nakul/Documents/RealLifeGTA/gta.data"
    try:
        life = _load_from_file(life_filename)
        print "Loading life from datastore"
    except:
        traceback.print_exc(file=sys.stdout)
        print "Couldn't load life from datastore, creating a new life"
        life = Life()

    # start main loop
    CommandLineInterface(life)._process_single_command()

    #persist data
    try:
        _save_to_file(life, life_filename)
    except:
        traceback.print_exc(file=sys.stdout)

def _load_from_file(filename):
    # If files don't exist, return empty list
    with open(filename, 'rb') as f:
        return_value = pickle.load(f)
    return return_value

def _save_to_file(domain_object, filename):
    with open(filename, 'wb') as f:
        pickle.dump(domain_object, f)

if __name__ == "__main__":
        main()
