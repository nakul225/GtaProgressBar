import traceback
import sys
import pickle
import os
import subprocess
from src.models.Life import Life
from src.view.CommandLineInterface import CommandLineInterface

def main():
    #initialize
    # Assumes Linux setup
    cmd="whoami 2>/dev/null >/tmp/username"
    username=subprocess.check_output("whoami",shell=True).split()

    life_directory = "/home/"+username[0]+"/Documents/RealLifeGTA/"
    life_filename="gta.data"
    life_complete_path=life_directory+life_filename
    try:
        life = _load_from_file(life_complete_path)
        #print "Loading life from datastore"
    except:
        #traceback.print_exc(file=sys.stdout)
        print "Couldn't load life from datastore, creating a new file at path:" +life_directory
        subprocess.check_output("mkdir -p "+life_directory,shell=True)
        life = Life()

    # start main loop
    CommandLineInterface(life)._process_single_command()

    #persist data
    try:
        _save_to_file(life, life_complete_path)
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
