from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import *
from task_manager import TaskManager
from tkinter import ttk


class GUI():
    """
        Initialises the gui for the application
        Parameters:
            data: points to the parsed json array
    """
    def __init__(self, data):
        self.main = Tk()
        self.main.configure(background="white")
        self.data = data
        self.docs = TaskManager.get_all_documents(self.data)
        self.users = [""]
        self.tasks = ["2a", "2b", "3a", "3b", "4", "5a", "5b", "5c", "5d", "5e"]
        self.menu = Frame(self.main).pack(side=TOP)
        self.test = StringVar()
        self.task_title = Label(self.menu, textvariable=self.test, bg="white", font="-weight bold -size 26").pack(side=TOP)
        self.task = Label(self.menu, text="Task ID", bg="white").pack(side=TOP)
        self.tid = StringVar()
        self.tid.trace("w", callback=self.find_users_by_task)
        self.task_options = ttk.Combobox(self.main, textvariable=self.tid)
        self.task_options['values'] = self.tasks
        self.task_options.pack(side=TOP)
        self.doc_title = Label(self.menu, text="Document ID", bg="white").pack(side=TOP)
        self.did = StringVar()
        self.did.trace("w", callback=self.find_users_by_doc)
        self.doc_options = ttk.Combobox(self.main, textvariable=self.did, width=50)
        self.doc_options['values'] = self.docs
        self.doc_options.pack(side=TOP)
        self.user = Label(self.menu, text="User ID", bg="white").pack(side=TOP)
        self.uid = StringVar()
        self.user_options = ttk.Combobox(self.main, textvariable=self.uid)
        self.user_options['values'] = self.users
        self.user_options.pack(side=TOP)
        self.canvas = None
        self.toolbar = None
        self.listbox = None
        self.btn_search = Button(self.menu, text="Search", command=self.btn_click_search).pack(side=TOP)
        self.btn_file = Button(self.menu, text="Open File", command=self.btn_click_file).pack(side=LEFT)

    """
        Deals with the eent of selecting a task that requires users id's
    """
    def find_users_by_task(self, *args):
        if self.tid.get() == "5b":
            print(self.tid.get())
            new_choices = TaskManager.get_all_users(self.data)
            self.users = new_choices
            self.user_options['values'] = [""] + new_choices
    """
        Deals with the event of selecting a document id by finding users of a certain document
    """
    def find_users_by_doc(self, *args):
        new_choices = TaskManager.get_all_users_by_doc(self.did.get(), self.data)
        self.users = new_choices
        self.user_options['values'] = [""] + new_choices

    """
        Deals with the event of clicking the open button
    """
    def btn_click_file(self):
        file = filedialog.askopenfilename()
        try:
            self.data = TaskManager.load_file(file)
        except FileNotFoundError:
            showinfo("No File Provided", "Application will use Previous File")
    """
        Deals with the event of clicking the search button
    """
    def btn_click_search(self):
        tasks = {"2a": "Viewers by Country",
                 "2b": "Viewers by Continent",
                 "3a": "All Browsers Simple",
                 "3b": "All Browsers Sorted",
                 "4":  "Top 10 Readers",
                 "5a": "Users Who Read Document",
                 "5b": "Documents That User Read",
                 "5c": "Also Likes",
                 "5d": "Also Likes Sorted by Reader Profile",
                 "5e": "Also Likes Sorted By Readership"}
        # check if input the task textbox is valid
        if self.tid.get() not in tasks.keys():
            showerror("Input Error", "Please Enter a Valid Task")
            return
        # check if it requires a document id and user id inputs
        if self.tid.get() not in ["3a", "3b", "4"]:
            if self.tid.get() == "5a" and self.did.get() not in self.docs:
                showerror("Input Error", "Please Enter a Valid Document ID")
                return
            if self.tid.get() == "5b" and self.uid.get() not in self.users:
                showerror("Input Error", "Please Enter a Valid User ID")
                return
            if self.tid.get() not in ["5a", "5b"] and self.did.get() not in self.docs:
                showerror("Input Error", "Please Enter a Valid Document ID")
                return
            if self.tid.get() not in ["5a", "5b"] and self.uid.get() not in TaskManager.get_all_users_by_doc(self.did.get(), self.data):
                showerror("Input Error", "Please Enter a Valid User ID")
                return
        self.test.set(tasks[self.tid.get()])
        TaskManager.task_handler(self.did.get(), self.uid.get(), self.tid.get(), self.data, self, False)
