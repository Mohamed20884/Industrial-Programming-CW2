#!/usr/bin/env python3
from task_manager import TaskManager
import argparse
from gui import GUI


"""
    Starting point of the application
"""
def main():
    # command line argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-u")
    parser.add_argument("-d")
    parser.add_argument("-t")
    parser.add_argument("-g")
    parser.add_argument("-f")
    args = vars(parser.parse_args())
    # parses user id from command line
    user_id = args["u"]
    # parses document id from command line
    doc_id = args["d"]
    # parses task id from command line
    task_id = args["t"]
    # parses if you want gui argument from command line
    display = args["g"]
    # parses file name from command line
    file = args["f"]
    cmd = True
    g = None
    data = TaskManager.load_file(file)
    # loads gui
    if display == "yes":
        g = GUI(data)
        g.main.mainloop()
    # uses command line interface
    else:
        TaskManager.task_handler(doc_id, user_id, task_id, data, g, cmd)
    return


if __name__ == "__main__":
    main()
