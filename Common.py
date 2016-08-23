import sys
import os

def remove(filename):
    # This will attempt to remove whatever filename is passed.
    # Requires os
    try:
        os.remove(filename)
        print ("Removed file called %s" % filename)
    except:
        print ("Didn't remove %s" % filename)
        
        
class colour:
    # These are all colours and should work in all terminals
    # Just print a colour.XXX and ALL following text will turn
    # in to it
    blue = "\033[34m"
    red = "\033[31m"
    bold = "\033[1m"
    endc = "\033[0m"
    black = "\033[0m" + bold
    purple = "\033[35m"
    teal = "\033[36m"

def query_yes_no(question, default="yes"):
    question = colour.bold + question + colour.endc
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")