import tkinter as tk
from circular_queue import CircularQueue
from tkinter import ttk, messagebox, scrolledtext
from sql_functions import *
from misc_functions import *


FONT_1 = ("Arial", 7)
FONT_2 = ("Arial", 10)
FONT_3 = ("Arial", 15)
FONT_4 = ("Arial", 20)
FONT_5 = ("Arial", 25)
FONT_6 = ("Arial", 40)
ROW_HEIGHT = 33
IMPORTANCES = ["Low", "Medium", "High"]
IMPORTANCE_COLOURS = [
    "#006400",  # green
    "#ea9400",  # gold
    "#ff5733",  # salmon
    "#c70039",  # crimson
    "#4b0082",  # purple
    "#00008b",  # navy
]


### window
class Window(tk.Tk):
    def __init__(self, minwidth, minheight):
        super().__init__()
        self.title("Team Tracker")
        self.geometry(f"{minwidth}x{minheight}")
        self.minsize(minwidth, minheight)
        self.login()

    def login(self):
        Login(self)

    def new_password(self, username):
        NewPassword(self, username)

    def main(self, username):
        Main(self, username)


### login
class Login(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=11 * ROW_HEIGHT, width=10000)
        # width = 10000 is an awkward solution to the frame not filling the
        # screen width while grid_progagate is false
        self.fill_frame()
        self.grid_propagate(False)
        # this stops the frame resizing to fill its container
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.login_label = tk.Label(self, text="Login", font=FONT_6)
        self.username_label = tk.Label(self, text="Username:", font=FONT_4)
        self.username_entry = tk.Entry(self, font=FONT_3)
        self.password_label = tk.Label(self, text="Password:", font=FONT_4)
        self.password_entry = tk.Entry(self, show="*", font=FONT_3)
        self.enter_button = tk.Button(
            self, text="Enter", font=FONT_4, command=self.enter
        )

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(11)]), weight=1, uniform="a"
        )
        # defines 11 equally sized rows

        ## grid widgets
        self.login_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.username_label.grid(row=3, column=0, sticky="w")
        self.username_entry.grid(row=4, column=0, sticky="w")
        self.password_label.grid(row=6, column=0, sticky="w")
        self.password_entry.grid(row=7, column=0, sticky="w")
        self.enter_button.grid(row=9, column=0, rowspan=2, sticky="w")

    def enter(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if login_valid(username, password):
            if active(username):
                self.destroy()
                self.master.main(username)
            else:
                messagebox.showwarning("Warning", "A new password is required")
                self.destroy()
                self.master.new_password(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")


class NewPassword(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master, height=11 * ROW_HEIGHT, width=10000)
        self.username = username
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.new_password_title_label = tk.Label(
            self, text="New Password", font=FONT_6
        )
        self.new_password_label = tk.Label(
            self, text="New Password:", font=FONT_4
        )
        self.new_password_entry = tk.Entry(self, show="*", font=FONT_3)
        self.confirm_new_password_label = tk.Label(
            self, text="Confirm New Password:", font=FONT_4
        )
        self.confirm_new_password_entry = tk.Entry(self, show="*", font=FONT_3)
        self.enter_button = tk.Button(
            self, text="Enter", font=FONT_4, command=self.enter
        )

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(11)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.new_password_title_label.grid(
            row=0, column=0, rowspan=2, sticky="w"
        )
        self.new_password_label.grid(row=3, column=0, sticky="w")
        self.new_password_entry.grid(row=4, column=0, sticky="w")
        self.confirm_new_password_label.grid(row=6, column=0, sticky="w")
        self.confirm_new_password_entry.grid(row=7, column=0, sticky="w")
        self.enter_button.grid(row=9, column=0, rowspan=2, sticky="w")

    def enter(self):
        if (
            self.new_password_entry.get()
            == self.confirm_new_password_entry.get()
        ):
            new_password = self.new_password_entry.get()
            if strong(new_password):
                set_new_password(self.username, new_password)
                self.destroy()
                self.master.main(self.username)
            else:
                messagebox.showerror(
                    "Error",
                    "Password not strong enough, try using a longer password or a larger variety of character types",
                )
        else:
            messagebox.showerror("Error", "Passwords do not match")


### main
class Main(ttk.Notebook):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.admin = admin(self.username)
        self.fill_notebook()
        self.pack(fill="both", expand=True)

    def fill_notebook(self):
        ## add tabs
        self.task_interface = TaskInterface(self, self.username)
        self.event_interface = EventInterface(self, self.username)
        self.add(self.task_interface, text="Tasks")
        self.add(self.event_interface, text="Events")
        if self.admin:
            self.account_interface = AccountInterface(self, self.username)
            self.add(self.account_interface, text="Accounts")

        ## events
        self.bind("<<NotebookTabChanged>>", lambda event: self.tab_change())
        # refreshes tabs as they are changed to
        # lambda used to ensure correct number of positional arguments given

    def tab_change(self):
        if self.index("current") == 0:
            self.task_interface.winfo_children()[0].destroy()
            self.task_interface.task_menu()
        elif self.index("current") == 1:
            self.event_interface.winfo_children()[0].destroy()
            self.event_interface.calendar()
        elif self.index("current") == 2:
            self.account_interface.winfo_children()[0].destroy()
            self.account_interface.account_menu()


### task interface
class TaskInterface(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.sort_through_backlog_action = ""
        self.task_menu()

    def task_menu(self):
        TaskMenu(self, self.username)

    def new_task(self):
        NewTask(self)

    def progress_task(self, task_id):
        if get_task(task_id)[3] == "backlog":
            ProgressTaskFromBacklog(self, task_id)
        else:
            ProgressTaskFromToDo(self, task_id)

    def edit_task(self, task_id):
        EditTask(self, task_id)

    def sort_through_backlog(self):
        queue = CircularQueue(100)
        for task in get_tasks(team(self.username), 0):
            queue.enqueue(task)

        while not queue.is_empty():
            task = queue.dequeue()
            progress_interface = ProgressTaskFromBacklog(
                self, task[0], sort=True
            )
            # ensures the following code only runs once the
            # ProgressTaskFromBacklog window is closed
            while progress_interface.get_running():
                self.update()
            if self.sort_through_backlog_action == "cancel":
                self.set_sort_through_backlog_action("")
                break
            if self.sort_through_backlog_action == "send to back":
                queue.enqueue(task)
            self.set_sort_through_backlog_action("")

        self.task_menu()

    def set_sort_through_backlog_action(self, action):
        self.sort_through_backlog_action = action


class TaskMenu(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.scroll_toggle = True
        self.fill_frame()
        self.pack(fill="both", expand=True)

    def fill_frame(self):
        ## toolbar
        self.toolbar = tk.Frame(self, relief="ridge", bd=4)
        self.toolbar.pack(fill="x")

        self.add_task_button = tk.Button(
            self.toolbar, text="Add Task", font=FONT_2, command=self.new_task
        )
        self.sort_through_backlog_button = tk.Button(
            self.toolbar,
            text="Sort Through Backlog",
            font=FONT_2,
            command=self.sort_through_backlog,
        )
        self.clear_done_button = tk.Button(
            self.toolbar,
            text='Clear "Done"',
            font=FONT_2,
            command=self.clear_done,
        )
        self.add_task_button.pack(side="left", padx=4, pady=4)
        self.sort_through_backlog_button.pack(side="left", padx=4, pady=4)
        self.clear_done_button.pack(side="left", padx=4, pady=4)

        self.stats_button = tk.Button(
            self.toolbar,
            text="Stats",
            font=FONT_2,
            command=lambda: messagebox.showinfo(
                "Stats", stats_string(self.username)
            ),
        )
        self.stats_button.pack(side="right", padx=4, pady=4)

        self.account_info_label = tk.Label(
            self.toolbar, text=account_info_string(self.username), font=FONT_2
        )
        self.account_info_label.pack(side="right")

        ## canvas
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        ## canvas frame
        self.canvas_frame = tk.Frame(self.canvas)
        self.canvas_frame.columnconfigure(
            tuple([n for n in range(4)]), weight=1, uniform="a"
        )
        for i in range(4):
            TaskMenuColumn(self.canvas_frame, self.username, i)

        ## events
        self.bind_all("<MouseWheel>", self.scroll)
        # ensures the above event is destroyed along with the canvas
        self.canvas.bind(
            "<Destroy>", lambda event: self.unbind_all("<MouseWheel>")
        )
        # <Configure> triggers when the widget size is changed i.e. when the
        # window is resized
        self.canvas.bind(
            "<Configure>",
            lambda event: self.update_size(event.width, event.height),
        )

    def update_size(self, canvas_width, canvas_height):
        if canvas_height < self.canvas_frame.winfo_reqheight():
            height = self.canvas_frame.winfo_reqheight()
            self.scroll_toggle = True
            self.canvas.configure(
                scrollregion=(
                    0,
                    0,
                    canvas_width,
                    self.canvas_frame.winfo_reqheight(),
                )
            )
        else:
            height = canvas_height
            self.scroll_toggle = False

        self.canvas.create_window(
            (0, 0),
            window=self.canvas_frame,
            anchor="nw",
            width=canvas_width,
            height=height,
        )

    def scroll(self, event):
        # the height aspect of update_size() is unreliable during window
        # resizing (due to text wrapping in task descriptions) so must be
        # recalled before scrolling
        self.update_size(self.canvas.winfo_width(), self.canvas.winfo_height())
        if self.scroll_toggle:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def new_task(self):
        self.destroy()
        self.master.new_task()

    def sort_through_backlog(self):
        self.destroy()
        self.master.sort_through_backlog()

    def clear_done(self):
        clear_done()
        self.destroy()
        self.master.task_menu()


class TaskMenuColumn(tk.Frame):
    def __init__(self, master, username, column):
        super().__init__(master)
        self.username = username
        self.column = column
        if self.column == 0:
            self.title = "Backlog"
        elif self.column == 1:
            self.title = "To Do"
        elif self.column == 2:
            self.title = "Doing"
        elif self.column == 3:
            self.title = "Done"
        self.fill_frame()
        self.grid(row=0, column=self.column, sticky="nesw", pady=5)

    def fill_frame(self):
        ## title
        self.title_label = tk.Label(self, text=self.title, font=FONT_3)
        self.title_label.pack()

        ## tasks
        self.tasks = get_tasks(team(self.username), self.column)
        for task in self.tasks:
            Task(self, task, self.username)


class Task(tk.Frame):
    def __init__(self, master, task, username):
        super().__init__(
            master, relief="raised", bd=4, bg=get_task_bg(task[0], username)
        )
        self.task = task
        self.username = username
        self.bg = get_task_bg(self.task[0], self.username)
        self.importance = importance(self.task[4], self.task[5])
        self.fill_frame()
        self.pack(fill="x", padx=10, pady=5)

    def fill_frame(self):
        ## create widgets
        self.id_label = tk.Label(
            self,
            text=f"ID:{self.task[0]}",
            font=FONT_1,
            fg="grey",
            bg=self.bg,
        )
        self.deadline_label = tk.Label(
            self,
            text=self.task[4],
            font=FONT_1,
            fg="grey",
            bg=self.bg,
        )
        self.title_label = tk.Label(
            self,
            text=self.task[1],
            font=FONT_2 + ("bold",),
            bg=self.bg,
        )
        self.description_label = tk.Label(
            self,
            text=self.task[2],
            font=FONT_2,
            bg=self.bg,
        )

        ## create button frame
        self.button_frame = tk.Frame(self, bg=self.bg)
        self.progress_button = tk.Button(
            self.button_frame,
            text="Progress",
            font=FONT_2,
            command=self.progress,
        )
        self.edit_button = tk.Button(
            self.button_frame, text="Edit", font=FONT_2, command=self.edit
        )
        self.delete_button = tk.Button(
            self.button_frame, text="Delete", font=FONT_2, command=self.delete
        )
        self.importance_dot = tk.Label(
            self.button_frame,
            text="⬤",
            font=FONT_2,
            fg=IMPORTANCE_COLOURS[self.importance - 1],
            bg=self.bg,
        )

        if self.master.column != 3:
            self.progress_button.pack(side="left", padx=4, pady=4)
        self.edit_button.pack(side="left", padx=4, pady=4)
        self.delete_button.pack(side="left", padx=4, pady=4)
        if self.master.column != 0:
            self.importance_dot.pack(side="right", padx=10)

        ## create grid
        self.grid_columnconfigure(0, weight=1)
        # ensures contents of the task frame are centered correctly

        ## grid widgets
        self.id_label.grid(row=0, column=0, sticky="w")
        self.deadline_label.grid(row=0, column=0, sticky="e")
        self.title_label.grid(row=1, column=0)
        if self.task[2]:
            self.description_label.grid(row=2, column=0, sticky="ew")
        self.button_frame.grid(row=3, column=0, sticky="nesw")

        ## events
        self.bind(
            "<Configure>",
            lambda event: self.description_label.configure(
                wraplength=event.width - 10
            ),
        )
        # ensures description_label wraps text to fit frame width whenever it is
        # resized

    def progress(self):
        if self.master.column == 2:
            answer = messagebox.askokcancel(
                'Progress to "Done"',
                f'{self.task[1]} will be progressed to "Done"',
            )
            if answer:
                update_state(self.task[0], "done")
                self.master.master.master.master.destroy()
                self.master.master.master.master.master.task_menu()
        else:
            self.master.master.master.master.destroy()
            self.master.master.master.master.master.progress_task(self.task[0])

    def edit(self):
        self.master.master.master.master.destroy()
        self.master.master.master.master.master.edit_task(self.task[0])

    def delete(self):
        if messagebox.askyesno(
            "Delete", "Are you sure you want to delete this task?"
        ):
            delete_task(self.task[0])
            self.destroy()


class NewTask(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=18 * ROW_HEIGHT, width=10000)
        self.deadline = False
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.new_task_label = tk.Label(self, text="New Task", font=FONT_6)
        self.title_label = tk.Label(self, text="Title:", font=FONT_4)
        self.title_entry = tk.Entry(self, font=FONT_3)
        self.team_label = tk.Label(self, text="Team:", font=FONT_4)
        self.description_label = tk.Label(
            self, text="Description:", font=FONT_4
        )
        self.description_scrolledtext = scrolledtext.ScrolledText(
            self, font=FONT_3, height=2
        )
        self.add_deadline_button = tk.Button(
            self, text="+ Deadline", font=FONT_4, command=self.add_deadline
        )
        self.deadline_label = tk.Label(self, text="Deadline:", font=FONT_4)
        self.deadline_entry_frame = tk.Frame(self)

        ## create team optionmenu
        self.team_optionmenu_value = tk.StringVar(
            self, value="Select a team..."
        )
        self.team_optionmenu = tk.OptionMenu(
            self,
            self.team_optionmenu_value,
            "Operational",
            "Development",
            "Both",
        )
        self.team_optionmenu.configure(font=FONT_3)
        self.team_optionmenu["menu"].configure(font=FONT_2)

        ## fill deadline entry frame
        self.day_label = tk.Label(
            self.deadline_entry_frame, text="Day:", font=FONT_4
        )
        self.day_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
        self.month_label = tk.Label(
            self.deadline_entry_frame, text="Month:", font=FONT_4
        )
        self.month_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
        self.year_label = tk.Label(
            self.deadline_entry_frame, text="Year:", font=FONT_4
        )
        self.year_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)

        self.day_label.pack(side="left")
        self.day_entry.pack(side="left")
        self.month_label.pack(side="left")
        self.month_entry.pack(side="left")
        self.year_label.pack(side="left")
        self.year_entry.pack(side="left")

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.add_task_button = tk.Button(
            self.button_frame,
            text="Add Task",
            font=FONT_4,
            command=self.add_task,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_task_menu,
        )

        self.add_task_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(18)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.new_task_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.title_label.grid(row=3, column=0, sticky="w")
        self.title_entry.grid(row=4, column=0, sticky="w")
        self.team_label.grid(row=6, column=0, sticky="w")
        self.team_optionmenu.grid(row=7, column=0, sticky="w")
        self.description_label.grid(row=9, column=0, sticky="w")
        self.description_scrolledtext.grid(
            row=10, column=0, rowspan=2, sticky="w"
        )
        self.add_deadline_button.grid(row=13, column=0, sticky="w")
        self.button_frame.grid(row=15, column=0, rowspan=2, sticky="w")

    def add_deadline(self):
        # deadlines are optional here as sometimes deadlines will be concrete
        # and known when the task is first created but sometimes a reasonable
        # deadline will have to be assigned when the task is progressed to "to
        # do"
        self.add_deadline_button.grid_forget()
        self.deadline_label.grid(row=13, column=0, sticky="w")
        self.deadline_entry_frame.grid(row=14, column=0, sticky="w")
        self.button_frame.grid(row=16, column=0, rowspan=2, sticky="w")
        self.deadline = True

    def details_valid(self):
        if not self.title_entry.get():
            return False
        if self.team_optionmenu_value.get() == "Select a team...":
            return False
        if self.deadline and not date_valid(
            self.day_entry.get(), self.month_entry.get(), self.year_entry.get()
        ):
            return False
        return True

    def add_task(self):
        if self.details_valid():
            if self.deadline:
                deadline = f"{int(self.year_entry.get())}-{int(self.month_entry.get())}-{int(self.day_entry.get())}"
            else:
                deadline = "0-0-0"
            add_task(
                self.title_entry.get(),
                self.description_scrolledtext.get("1.0", "end-1c"),
                "backlog",
                deadline,
                0,
                self.team_optionmenu_value.get().lower(),
            )
            self.reload_task_menu()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_task_menu(self):
        self.destroy()
        self.master.task_menu()


class ProgressTaskFromBacklog(tk.Frame):
    def __init__(self, master, task_id, sort=False):
        super().__init__(master, height=17 * ROW_HEIGHT, width=10000)
        self.task = get_task(task_id)
        self.sort = sort
        self.running = True
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        sort_shift = 6 if self.sort else 0

        ## create widgets
        self.progress_task_label = tk.Label(
            self, text='Progress to "To Do"', font=FONT_6
        )
        if self.sort:
            self.title = tk.Label(self, text=self.task[1], font=FONT_5)
            self.description_label = tk.Label(
                self, text="Description:", font=FONT_4
            )
            self.description_scrolledtext = scrolledtext.ScrolledText(
                self, font=FONT_3, height=2
            )
            self.description_scrolledtext.insert("end", self.task[2])
            self.description_scrolledtext.configure(state="disabled")

        ## create importance widgets
        self.importance_label = tk.Label(self, text="Importance:", font=FONT_4)
        self.importance_optionmenu_value = tk.StringVar(
            self, value="Select an importance..."
        )
        self.importance_optionmenu = tk.OptionMenu(
            self, self.importance_optionmenu_value, "Low", "Medium", "High"
        )
        self.importance_optionmenu.configure(font=FONT_3)
        self.importance_optionmenu["menu"].configure(font=FONT_2)

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.progress_task_button = tk.Button(
            self.button_frame,
            text="Progress Task",
            font=FONT_4,
            command=self.progress_task,
        )
        if self.sort:
            self.send_to_back_button = tk.Button(
                self.button_frame,
                text="Send to Back",
                font=FONT_4,
                command=lambda: self.exit_interface(action="send to back"),
            )
            self.skip_button = tk.Button(
                self.button_frame,
                text="Skip",
                font=FONT_4,
                command=self.exit_interface,
            )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=lambda: self.exit_interface(action="cancel"),
        )

        # this padding arrangement ensures the progress button is as far left as
        # possible
        self.progress_task_button.pack(side="left")
        if self.sort:
            self.send_to_back_button.pack(side="left", padx=8)
            self.skip_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(17)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.progress_task_label.grid(row=0, column=0, rowspan=2, sticky="w")
        if self.sort:
            self.title.grid(row=3, column=0, sticky="w")
            self.description_label.grid(row=5, column=0, sticky="w")
            self.description_scrolledtext.grid(
                row=6, column=0, rowspan=2, sticky="w"
            )
        self.importance_label.grid(row=3 + sort_shift, column=0, sticky="w")
        self.importance_optionmenu.grid(
            row=4 + sort_shift, column=0, sticky="w"
        )

        # only adds deadline widgets if the task has no deadline yet
        if not deadline_present(self.task[0]):
            ## create deadline widgets
            self.deadline_label = tk.Label(self, text="Deadline:", font=FONT_4)
            self.deadline_entry_frame = tk.Frame(self)

            self.day_label = tk.Label(
                self.deadline_entry_frame, text="Day:", font=FONT_4
            )
            self.day_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
            self.month_label = tk.Label(
                self.deadline_entry_frame, text="Month:", font=FONT_4
            )
            self.month_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
            self.year_label = tk.Label(
                self.deadline_entry_frame, text="Year:", font=FONT_4
            )
            self.year_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)

            self.day_label.pack(side="left")
            self.day_entry.pack(side="left")
            self.month_label.pack(side="left")
            self.month_entry.pack(side="left")
            self.year_label.pack(side="left")
            self.year_entry.pack(side="left")

            ## grid remaining widgets
            self.deadline_label.grid(row=6 + sort_shift, column=0, sticky="w")
            self.deadline_entry_frame.grid(
                row=7 + sort_shift, column=0, sticky="w"
            )
            self.button_frame.grid(
                row=9 + sort_shift, column=0, rowspan=2, sticky="w"
            )
        else:
            self.button_frame.grid(
                row=6 + sort_shift, column=0, rowspan=2, sticky="w"
            )

    def details_valid(self):
        if self.importance_optionmenu_value.get() == "Select an importance...":
            return False
        if not deadline_present(self.task[0]):
            if not date_valid(
                self.day_entry.get(),
                self.month_entry.get(),
                self.year_entry.get(),
            ):
                return False
        return True

    def progress_task(self):
        if self.details_valid():
            if not deadline_present(self.task[0]):
                update_deadline(
                    self.task[0],
                    f"{int(self.year_entry.get())}-{int(self.month_entry.get())}-{int(self.day_entry.get())}",
                )
            update_importance(
                self.task[0],
                IMPORTANCES.index(self.importance_optionmenu_value.get()) + 1,
            )
            update_state(self.task[0], "to do")
            self.exit_interface()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def get_running(self):
        return self.running

    def exit_interface(self, action=""):
        self.destroy()
        if not self.sort:
            self.master.task_menu()
        elif action:
            self.master.set_sort_through_backlog_action(action)
        self.running = False


class ProgressTaskFromToDo(tk.Frame):
    def __init__(self, master, task_id):
        super().__init__(master, height=10 * ROW_HEIGHT, width=10000)
        self.task = get_task(task_id)
        self.assignee_count = 0
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.progress_task_label = tk.Label(
            self, text='Progress to "Doing"', font=FONT_6
        )

        ## create assignee widgets
        self.assignee_label = tk.Label(self, text="Assignee(s):", font=FONT_4)
        self.assignee_optionmenu_value_list = [
            tk.StringVar(self, value="Select an assignee...") for i in range(9)
        ]
        self.assignee_optionmenu_list = [
            tk.OptionMenu(
                self,
                self.assignee_optionmenu_value_list[i],
                *get_usernames_from_team(self.task[6]),
            )
            for i in range(9)
        ]
        for optionmenu in self.assignee_optionmenu_list:
            optionmenu.configure(font=FONT_3)
            optionmenu["menu"].configure(font=FONT_2)
        self.new_assignee_button = tk.Button(
            self, text="+", font=FONT_4, command=self.add_new_assignee
        )

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.progress_task_button = tk.Button(
            self.button_frame,
            text="Progress Task",
            font=FONT_4,
            command=self.progress_task,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_task_menu,
        )

        self.progress_task_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(10)]), weight=1, uniform="a"
        )
        self.grid_columnconfigure(tuple([n for n in range(3)]), minsize=300)

        ## grid widgets
        self.progress_task_label.grid(
            row=0, column=0, rowspan=2, columnspan=3, sticky="w"
        )
        self.assignee_label.grid(row=3, column=0, columnspan=3, sticky="w")
        self.add_new_assignee()
        self.button_frame.grid(
            row=6, column=0, rowspan=2, columnspan=3, sticky="w"
        )
        # columnspan=3 ensures the assignee widgets grid themselves with minimum
        # column width

    def add_new_assignee(self):
        self.assignee_count += 1
        self.assignee_optionmenu_list[self.assignee_count - 1].grid(
            row=4 + (self.assignee_count - 1) // 3,
            column=(self.assignee_count - 1) % 3,
            sticky="w",
        )
        if self.assignee_count == 9:
            self.new_assignee_button.grid_forget()
        else:
            self.new_assignee_button.grid(
                row=4 + self.assignee_count // 3,
                column=self.assignee_count % 3,
                sticky="w",
            )
        if self.assignee_count == 3 or self.assignee_count == 6:
            self.button_frame.grid(
                row=6 + self.assignee_count // 3,
                column=0,
                rowspan=2,
                columnspan=3,
                sticky="w",
            )

    def get_assignees(self):
        assignees = []
        for i in range(self.assignee_count):
            if (
                not self.assignee_optionmenu_value_list[i].get()
                == "Select an assignee..."
            ):
                if self.assignee_optionmenu_value_list[i].get() in assignees:
                    return []
                else:
                    assignees.append(
                        self.assignee_optionmenu_value_list[i].get()
                    )
        return assignees

    def progress_task(self):
        if self.get_assignees():
            for assignee in self.get_assignees():
                add_assignment(assignee, self.task[0])
            update_state(self.task[0], "doing")
            self.reload_task_menu()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_task_menu(self):
        self.destroy()
        self.master.task_menu()


class EditTask(tk.Frame):
    def __init__(self, master, task_id):
        super().__init__(master, height=18 * ROW_HEIGHT, width=10000)
        self.task = get_task(task_id)
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.edit_task_label = tk.Label(self, text="Edit Task", font=FONT_6)
        self.description_label = tk.Label(
            self, text="Description:", font=FONT_4
        )
        self.description_scrolledtext = scrolledtext.ScrolledText(
            self, font=FONT_3, height=2
        )
        self.description_scrolledtext.insert("end", self.task[2])

        ## create team widgets
        self.team_label = tk.Label(self, text="Team:", font=FONT_4)
        self.team_optionmenu_value = tk.StringVar(
            self, value=self.task[6][0].upper() + self.task[6][1:]
        )
        self.team_optionmenu = tk.OptionMenu(
            self,
            self.team_optionmenu_value,
            "Operational",
            "Development",
            "Both",
        )
        self.team_optionmenu.configure(font=FONT_3)
        self.team_optionmenu["menu"].configure(font=FONT_2)

        ## create deadline widgets
        self.deadline_label = tk.Label(self, text="Deadline:", font=FONT_4)
        self.deadline_entry_frame = tk.Frame(self)
        self.day_label = tk.Label(
            self.deadline_entry_frame, text="Day:", font=FONT_4
        )
        self.day_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
        self.month_label = tk.Label(
            self.deadline_entry_frame, text="Month:", font=FONT_4
        )
        self.month_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)
        self.year_label = tk.Label(
            self.deadline_entry_frame, text="Year:", font=FONT_4
        )
        self.year_entry = tk.Entry(self.deadline_entry_frame, font=FONT_3)

        self.day_entry.insert("end", self.task[4].split("-")[2])
        self.month_entry.insert("end", self.task[4].split("-")[1])
        self.year_entry.insert("end", self.task[4].split("-")[0])

        self.day_label.pack(side="left")
        self.day_entry.pack(side="left")
        self.month_label.pack(side="left")
        self.month_entry.pack(side="left")
        self.year_label.pack(side="left")
        self.year_entry.pack(side="left")

        ## create importance widgets
        shift = 0

        if self.task[3] != "backlog":
            self.importance_label = tk.Label(
                self, text="Importance:", font=FONT_4
            )
            self.importance_optionmenu_value = tk.StringVar(
                self, value=IMPORTANCES[int(self.task[5]) - 1]
            )
            self.importance_optionmenu = tk.OptionMenu(
                self, self.importance_optionmenu_value, "Low", "Medium", "High"
            )
            self.importance_optionmenu.configure(font=FONT_3)
            self.importance_optionmenu["menu"].configure(font=FONT_2)
            self.importance_label.grid(row=13, column=0, sticky="w")
            self.importance_optionmenu.grid(row=14, column=0, sticky="w")

            shift = 3

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.save_edits_button = tk.Button(
            self.button_frame,
            text="Save Edits",
            font=FONT_4,
            command=self.save_edits,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_task_menu,
        )

        self.save_edits_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(18)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.edit_task_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.team_label.grid(row=3, column=0, sticky="w")
        self.team_optionmenu.grid(row=4, column=0, sticky="w")
        self.description_label.grid(row=6, column=0, sticky="w")
        self.description_scrolledtext.grid(
            row=7, column=0, rowspan=2, sticky="w"
        )
        self.deadline_label.grid(row=10, column=0, sticky="w")
        self.deadline_entry_frame.grid(row=11, column=0, sticky="w")
        self.button_frame.grid(row=13 + shift, column=0, rowspan=2, sticky="w")

    def details_valid(self):
        try:
            day = self.day_entry.get()
            month = self.month_entry.get()
            year = self.year_entry.get()

            # check for the special backlog case (0-0-0)
            is_backlog_zero_date = (
                int(year) == 0
                and int(month) == 0
                and int(day) == 0
                and self.task[3] == "backlog"
            )

            return date_valid(day, month, year) or is_backlog_zero_date

        except ValueError:
            return False

    def save_edits(self):
        if self.details_valid():
            if self.task[3] == "backlog":
                importance = 0
            else:
                importance = (
                    IMPORTANCES.index(self.importance_optionmenu_value.get())
                    + 1
                )
            edit_task(
                self.task[0],
                self.team_optionmenu_value.get().lower(),
                self.description_scrolledtext.get("1.0", "end-1c"),
                f"{int(self.year_entry.get())}-{int(self.month_entry.get())}-{int(self.day_entry.get())}",
                importance,
            )
            self.reload_task_menu()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_task_menu(self):
        self.destroy()
        self.master.task_menu()


### event interface
class EventInterface(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.calendar()

    def calendar(self, page=0):
        Calendar(self, self.username, page)

    def new_event(self):
        NewEvent(self)

    def new_team_event(self):
        NewTeamEvent(self)

    def remove_event(self):
        RemoveEvent(self)


class Calendar(tk.Frame):
    def __init__(self, master, username, page):
        super().__init__(master)
        self.username = username
        self.page = page
        self.cells = []
        self.fill_frame()
        self.pack(fill="both", expand=True)

    def fill_frame(self):
        ## toolbar
        self.toolbar = tk.Frame(self, relief="ridge", bd=4)
        self.toolbar.pack(side="top", fill="x")

        self.left_arrow = tk.Button(
            self.toolbar,
            text="<",
            font=FONT_2,
            command=lambda: self.change_page(self.page - 1),
            width=3,
        )
        self.left_arrow.pack(side="left", padx=4, pady=4)
        self.right_arrow = tk.Button(
            self.toolbar,
            text=">",
            font=FONT_2,
            command=lambda: self.change_page(self.page + 1),
            width=3,
        )
        self.right_arrow.pack(side="left", padx=4, pady=4)
        if self.page == 0:
            self.left_arrow.config(bg="lightgrey")
            self.left_arrow.config(state="disabled")
        if self.page == 100:
            self.right_arrow.config(bg="lightgrey")
            self.right_arrow.config(state="disabled")

        self.add_event_button = tk.Button(
            self.toolbar, text="Add Event", font=FONT_2, command=self.new_event
        )
        self.add_event_button.pack(side="left", padx=4, pady=4)
        self.add_team_event_button = tk.Button(
            self.toolbar,
            text="Add Team Event",
            font=FONT_2,
            command=self.new_team_event,
        )
        self.add_team_event_button.pack(side="left", padx=4, pady=4)
        self.delete_event_button = tk.Button(
            self.toolbar,
            text="Delete Event",
            font=FONT_2,
            command=self.remove_event,
        )
        self.delete_event_button.pack(side="left", padx=4, pady=4)
        self.clear_past_events_button = tk.Button(
            self.toolbar,
            text="Clear Past Events",
            font=FONT_2,
            command=self.clear_past_events,
        )
        self.clear_past_events_button.pack(side="left", padx=4, pady=4)

        self.stats_button = tk.Button(
            self.toolbar,
            text="Stats",
            font=FONT_2,
            command=lambda: messagebox.showinfo(
                "Stats", stats_string(self.username)
            ),
        )
        self.stats_button.pack(side="right", padx=4, pady=4)

        self.account_info_label = tk.Label(
            self.toolbar, text=account_info_string(self.username), font=FONT_2
        )
        self.account_info_label.pack(side="right")

        ## calendar
        self.calendar_frame = tk.Frame(self)
        self.calendar_frame.pack(fill="both", expand=True)
        self.calendar_frame.grid_rowconfigure(
            tuple([n for n in range(4)]), weight=1, uniform="a"
        )
        self.calendar_frame.grid_columnconfigure(
            tuple([n for n in range(7)]), weight=1, uniform="a"
        )
        for i in range(self.page * 28, (self.page + 1) * 28):
            cell = tk.Frame(
                self.calendar_frame, relief="raised", bd=4, bg=get_cell_bg(i)
            )
            cell.grid(row=i // 7 - 4 * self.page, column=i % 7, sticky="nsew")
            cell_day_label = tk.Label(
                cell, text=get_cell_day(i), font=FONT_1, bg=get_cell_bg(i)
            )
            cell_day_label.pack()
            cell_list = [cell, cell_day_label, []]
            for event in get_events(get_cell_date_string(i), self.username):
                cell_list[2].append(
                    tk.Label(cell, text=event, font=FONT_2, bg=get_cell_bg(i))
                )
                cell_list[2][-1].pack()
            for deadline in get_deadlines(
                get_cell_date_string(i), self.username
            ):
                cell_list[2].append(
                    tk.Label(
                        cell,
                        text=deadline[0],
                        font=FONT_2,
                        bg=get_cell_bg(i),
                        fg=IMPORTANCE_COLOURS[
                            importance(get_cell_date_string(i), deadline[1]) - 1
                        ],
                    )
                )
                cell_list[2][-1].pack()
            self.cells.append(cell_list)

        ## events
        cell.bind(
            "<Configure>",
            lambda event: self.update_wraplengths(event),
        )
        # having this out of the for loop ensures the binding is attached to the
        # last cell only, so that wraplengths are only updated once per resize
        # and they are updated all at once

    def update_wraplengths(self, event):
        for cell in self.cells:
            for label in cell[2]:
                label.configure(wraplength=event.width - 10)

    def change_page(self, newpage):
        self.destroy()
        self.master.calendar(page=newpage)

    def new_event(self):
        self.destroy()
        self.master.new_event()

    def new_team_event(self):
        self.destroy()
        self.master.new_team_event()

    def remove_event(self):
        if get_all_events():
            self.destroy()
            self.master.remove_event()
        else:
            messagebox.showerror("Error", "There are no events to delete")

    def clear_past_events(self):
        clear_past_events()
        self.destroy()
        self.master.calendar(page=self.page)


class NewEvent(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=18 * ROW_HEIGHT, width=10000)
        self.attendee_count = 0
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.new_event_label = tk.Label(self, text="New Event", font=FONT_6)
        self.title_label = tk.Label(self, text="Title:", font=FONT_4)
        self.title_entry = tk.Entry(self, font=FONT_3)
        self.date_label = tk.Label(self, text="Date:", font=FONT_4)
        self.date_entry_frame = tk.Frame(self)

        ## create attendee widgets
        self.attendee_label = tk.Label(self, text="Attendee(s):", font=FONT_4)
        self.attendee_optionmenu_value_list = [
            tk.StringVar(self, value="Select an attendee...") for i in range(15)
        ]
        self.attendee_optionmenu_list = [
            tk.OptionMenu(
                self,
                self.attendee_optionmenu_value_list[i],
                *get_all_usernames(),
            )
            for i in range(15)
        ]
        for optionmenu in self.attendee_optionmenu_list:
            optionmenu.configure(font=FONT_3)
            optionmenu["menu"].configure(font=FONT_2)
        self.new_attendee_button = tk.Button(
            self, text="+", font=FONT_4, command=self.add_new_attendee
        )

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.add_event_button = tk.Button(
            self.button_frame,
            text="Add Event",
            font=FONT_4,
            command=self.add_event,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_calendar,
        )

        self.add_event_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## fill date entry frame
        self.day_label = tk.Label(
            self.date_entry_frame, text="Day:", font=FONT_4
        )
        self.day_entry = tk.Entry(self.date_entry_frame, font=FONT_3)
        self.month_label = tk.Label(
            self.date_entry_frame, text="Month:", font=FONT_4
        )
        self.month_entry = tk.Entry(self.date_entry_frame, font=FONT_3)
        self.year_label = tk.Label(
            self.date_entry_frame, text="Year:", font=FONT_4
        )
        self.year_entry = tk.Entry(self.date_entry_frame, font=FONT_3)

        self.day_label.pack(side="left")
        self.day_entry.pack(side="left")
        self.month_label.pack(side="left")
        self.month_entry.pack(side="left")
        self.year_label.pack(side="left")
        self.year_entry.pack(side="left")

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(18)]), weight=1, uniform="a"
        )
        self.grid_columnconfigure(tuple([n for n in range(3)]), minsize=300)

        ## grid widgets
        self.new_event_label.grid(
            row=0, column=0, rowspan=2, columnspan=3, sticky="w"
        )
        self.title_label.grid(row=3, column=0, columnspan=3, sticky="w")
        self.title_entry.grid(row=4, column=0, columnspan=3, sticky="w")
        self.date_label.grid(row=6, column=0, columnspan=3, sticky="w")
        self.date_entry_frame.grid(row=7, column=0, columnspan=3, sticky="w")
        self.attendee_label.grid(row=9, column=0, columnspan=3, sticky="w")
        self.add_new_attendee()
        self.button_frame.grid(
            row=12, column=0, rowspan=2, columnspan=3, sticky="w"
        )

    def add_new_attendee(self):
        self.attendee_count += 1
        self.attendee_optionmenu_list[self.attendee_count - 1].grid(
            row=10 + (self.attendee_count - 1) // 3,
            column=(self.attendee_count - 1) % 3,
            sticky="w",
        )
        if self.attendee_count == 15:
            self.new_attendee_button.grid_forget()
        else:
            self.new_attendee_button.grid(
                row=10 + self.attendee_count // 3,
                column=self.attendee_count % 3,
                sticky="w",
            )
        if self.attendee_count in [3, 6, 9, 12]:
            self.button_frame.grid(
                row=12 + self.attendee_count // 3,
                column=0,
                rowspan=2,
                columnspan=3,
                sticky="w",
            )

    def get_attendees(self):
        attendees = []
        for i in range(self.attendee_count):
            if (
                not self.attendee_optionmenu_value_list[i].get()
                == "Select an attendee..."
            ):
                if self.attendee_optionmenu_value_list[i].get() in attendees:
                    return []
                else:
                    attendees.append(
                        self.attendee_optionmenu_value_list[i].get()
                    )
        return attendees

    def details_valid(self):
        if not self.title_entry.get():
            return False
        if not date_valid(
            self.day_entry.get(), self.month_entry.get(), self.year_entry.get()
        ):
            return False
        if not self.get_attendees():
            return False
        return True

    def add_event(self):
        if self.details_valid():
            date = f"{int(self.year_entry.get())}-{int(self.month_entry.get())}-{int(self.day_entry.get())}"
            add_event(
                self.title_entry.get(),
                date,
                self.get_attendees(),
            )
            self.reload_calendar()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_calendar(self):
        self.destroy()
        self.master.calendar()


class NewTeamEvent(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=14 * ROW_HEIGHT, width=10000)
        self.attendee_count = 0
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.new_team_event_label = tk.Label(
            self, text="New Team Event", font=FONT_6
        )
        self.title_label = tk.Label(self, text="Title:", font=FONT_4)
        self.title_entry = tk.Entry(self, font=FONT_3)
        self.date_label = tk.Label(self, text="Date:", font=FONT_4)
        self.date_entry_frame = tk.Frame(self)
        self.team_label = tk.Label(self, text="Team:", font=FONT_4)

        ## create team optionmenu
        self.team_optionmenu_value = tk.StringVar(
            self, value="Select a team..."
        )
        self.team_optionmenu = tk.OptionMenu(
            self,
            self.team_optionmenu_value,
            "Operational",
            "Development",
            "Both",
        )
        self.team_optionmenu.configure(font=FONT_3)
        self.team_optionmenu["menu"].configure(font=FONT_2)

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.add_event_button = tk.Button(
            self.button_frame,
            text="Add Event",
            font=FONT_4,
            command=self.add_event,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_calendar,
        )

        self.add_event_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## fill date entry frame
        self.day_label = tk.Label(
            self.date_entry_frame, text="Day:", font=FONT_4
        )
        self.day_entry = tk.Entry(self.date_entry_frame, font=FONT_3)
        self.month_label = tk.Label(
            self.date_entry_frame, text="Month:", font=FONT_4
        )
        self.month_entry = tk.Entry(self.date_entry_frame, font=FONT_3)
        self.year_label = tk.Label(
            self.date_entry_frame, text="Year:", font=FONT_4
        )
        self.year_entry = tk.Entry(self.date_entry_frame, font=FONT_3)

        self.day_label.pack(side="left")
        self.day_entry.pack(side="left")
        self.month_label.pack(side="left")
        self.month_entry.pack(side="left")
        self.year_label.pack(side="left")
        self.year_entry.pack(side="left")

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(14)]), weight=1, uniform="a"
        )
        self.grid_columnconfigure(tuple([n for n in range(3)]), minsize=300)

        ## grid widgets
        self.new_team_event_label.grid(
            row=0, column=0, rowspan=2, columnspan=3, sticky="w"
        )
        self.title_label.grid(row=3, column=0, columnspan=3, sticky="w")
        self.title_entry.grid(row=4, column=0, columnspan=3, sticky="w")
        self.date_label.grid(row=6, column=0, columnspan=3, sticky="w")
        self.date_entry_frame.grid(row=7, column=0, columnspan=3, sticky="w")
        self.team_label.grid(row=9, column=0, sticky="w")
        self.team_optionmenu.grid(row=10, column=0, sticky="w")
        self.button_frame.grid(
            row=12, column=0, rowspan=2, columnspan=3, sticky="w"
        )

    def details_valid(self):
        if not self.title_entry.get():
            return False
        if not date_valid(
            self.day_entry.get(), self.month_entry.get(), self.year_entry.get()
        ):
            return False
        if self.team_optionmenu_value.get() == "Select a team...":
            return False
        return True

    def add_event(self):
        if self.details_valid():
            date = f"{int(self.year_entry.get())}-{int(self.month_entry.get())}-{int(self.day_entry.get())}"
            add_event(
                self.title_entry.get(),
                date,
                get_usernames_from_team(
                    self.team_optionmenu_value.get().lower()
                ),
            )
            self.reload_calendar()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_calendar(self):
        self.destroy()
        self.master.calendar()


class RemoveEvent(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=8 * ROW_HEIGHT, width=10000)
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.remove_event_label = tk.Label(
            self, text="Remove Event", font=FONT_6
        )
        self.event_title_label = tk.Label(self, text="Event:", font=FONT_4)
        self.event_optionmenu_value = tk.StringVar(
            self, value="Select an event to delete..."
        )
        self.event_optionmenu = tk.OptionMenu(
            self, self.event_optionmenu_value, *get_all_events()
        )
        self.event_optionmenu.configure(font=FONT_3)
        self.event_optionmenu["menu"].configure(font=FONT_2)

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.delete_event_button = tk.Button(
            self.button_frame,
            text="Delete Event",
            font=FONT_4,
            command=self.delete,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_calendar,
        )

        self.delete_event_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(8)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.remove_event_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.event_title_label.grid(row=3, column=0, sticky="w")
        self.event_optionmenu.grid(row=4, column=0, sticky="w")
        self.button_frame.grid(row=6, column=0, rowspan=2, sticky="w")

    def delete(self):
        if self.event_optionmenu_value.get() != "Select an event to delete...":
            delete_event(self.event_optionmenu_value.get())
            self.reload_calendar()
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_calendar(self):
        self.destroy()
        self.master.calendar()


### accounts interface
class AccountInterface(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.account_menu()

    def account_menu(self):
        AccountMenu(self, self.username)

    def new_account(self):
        NewAccount(self)


class AccountMenu(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.scroll_toggle = True
        self.fill_frame()
        self.pack(fill="both", expand=True)

    def fill_frame(self):
        ## toolbar
        self.toolbar = tk.Frame(self, relief="ridge", bd=4)
        self.toolbar.pack(fill="x")

        self.add_account_button = tk.Button(
            self.toolbar,
            text="Add Account",
            font=FONT_2,
            command=self.new_account,
        )
        self.add_account_button.pack(side="left", padx=4, pady=4)

        self.stats_button = tk.Button(
            self.toolbar,
            text="Stats",
            font=FONT_2,
            command=lambda: messagebox.showinfo(
                "Stats", stats_string(self.username)
            ),
        )
        self.stats_button.pack(side="right", padx=4, pady=4)

        self.account_info_label = tk.Label(
            self.toolbar, text=account_info_string(self.username), font=FONT_2
        )
        self.account_info_label.pack(side="right")

        ## canvas
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        ## canvas frame
        self.canvas_frame = tk.Frame(self.canvas)
        for username in merge_sort(
            get_all_usernames(), key=lambda username: get_name(username)
        ):
            # sorts by name
            Account(self.canvas_frame, username)

        ## events
        self.bind_all("<MouseWheel>", self.scroll)
        self.canvas.bind(
            "<Destroy>", lambda event: self.unbind_all("<MouseWheel>")
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.update_size(event.width, event.height),
        )

    def update_size(self, canvas_width, canvas_height):
        if canvas_height < self.canvas_frame.winfo_reqheight():
            height = self.canvas_frame.winfo_reqheight()
            self.scroll_toggle = True
            self.canvas.configure(
                scrollregion=(
                    0,
                    0,
                    canvas_width,
                    self.canvas_frame.winfo_reqheight(),
                )
            )
        else:
            height = canvas_height
            self.scroll_toggle = False

        self.canvas.create_window(
            (0, 0),
            window=self.canvas_frame,
            anchor="nw",
            width=canvas_width,
            height=height,
        )

    def scroll(self, event):
        self.update_size(self.canvas.winfo_width(), self.canvas.winfo_height())
        if self.scroll_toggle:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def new_account(self):
        self.destroy()
        self.master.new_account()


class Account(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master, relief="raised", bd=4)
        self.username = username
        self.fill_frame()
        self.pack(fill="x", padx=8, pady=4)

    def fill_frame(self):
        ## create widgets
        self.name_label = tk.Label(
            self,
            text=f"{get_name(self.username)} | {self.username}",
            font=FONT_2,
        )
        self.delete_button = tk.Button(
            self, text="Delete", font=FONT_2, command=self.delete
        )
        self.save_changes_button = tk.Button(
            self, text="Save Changes", font=FONT_2, command=self.save_changes
        )
        self.admin_checkbox_value = tk.BooleanVar(
            self, value=admin(self.username)
        )
        self.admin_checkbox = tk.Checkbutton(
            self,
            text="Admin",
            font=FONT_2,
            variable=self.admin_checkbox_value,
            onvalue=True,
            offvalue=False,
        )
        self.password_change_scheduled_checkbox_value = tk.BooleanVar(
            self, value=not active(self.username)
        )
        self.password_change_scheduled_checkbox = tk.Checkbutton(
            self,
            text="Password Change Scheduled",
            font=FONT_2,
            variable=self.password_change_scheduled_checkbox_value,
            onvalue=True,
            offvalue=False,
        )

        ## create team optionmenu
        self.team_optionmenu_value = tk.StringVar(
            self, value=team(self.username)[0].upper() + team(self.username)[1:]
        )
        self.team_optionmenu = tk.OptionMenu(
            self,
            self.team_optionmenu_value,
            "Operational",
            "Development",
            "Both",
        )
        self.team_optionmenu.configure(font=FONT_2)
        self.team_optionmenu["menu"].configure(font=FONT_2)

        ## grid widgets
        self.name_label.pack(side="left")
        self.delete_button.pack(side="right", padx=4, pady=4)
        self.save_changes_button.pack(side="right", padx=4, pady=4)
        self.admin_checkbox.pack(side="right", padx=4, pady=4)
        self.password_change_scheduled_checkbox.pack(
            side="right", padx=4, pady=4
        )
        self.team_optionmenu.pack(side="right", padx=4, pady=4)

    def delete(self):
        if messagebox.askyesno(
            "Delete", "Are you sure you want to delete this account?"
        ):
            delete_account(self.username)
            self.destroy()

    def save_changes(self):
        if messagebox.askyesno(
            "Save Changes", "Are you sure you want to save these changes?"
        ):
            save_changes(
                self.username,
                self.team_optionmenu_value.get().lower(),
                not self.password_change_scheduled_checkbox_value.get(),
                self.admin_checkbox_value.get(),
            )
            self.master.master.master.destroy()
            self.master.master.master.master.account_menu()


class NewAccount(tk.Frame):
    def __init__(self, master):
        super().__init__(master, height=17 * ROW_HEIGHT, width=10000)
        self.fill_frame()
        self.grid_propagate(False)
        self.grid(row=0, column=0, padx=20, pady=20)

    def fill_frame(self):
        ## create widgets
        self.new_account_label = tk.Label(self, text="New Account", font=FONT_6)
        self.first_name_label = tk.Label(self, text="First Name:", font=FONT_4)
        self.first_name_entry = tk.Entry(self, font=FONT_3)
        self.last_name_label = tk.Label(self, text="Last Name:", font=FONT_4)
        self.last_name_entry = tk.Entry(self, font=FONT_3)
        self.temporary_password_label = tk.Label(
            self, text="Temporary Password:", font=FONT_4
        )
        self.temporary_password_entry = tk.Entry(self, font=FONT_3)

        ## create account type widgets
        self.account_type_label = tk.Label(self, text="Team:", font=FONT_4)
        self.account_type_frame = tk.Frame(self)

        self.team_optionmenu_value = tk.StringVar(
            self.account_type_frame, value="Select a team..."
        )
        self.team_optionmenu = tk.OptionMenu(
            self.account_type_frame,
            self.team_optionmenu_value,
            "Operational",
            "Development",
            "Both",
        )
        self.team_optionmenu.configure(font=FONT_3)
        self.team_optionmenu["menu"].configure(font=FONT_2)
        self.admin_checkbox_value = tk.BooleanVar(
            self.account_type_frame, value=False
        )
        self.admin_checkbox = tk.Checkbutton(
            self.account_type_frame,
            text="Admin",
            font=FONT_3,
            variable=self.admin_checkbox_value,
            onvalue=True,
            offvalue=False,
        )
        self.team_optionmenu.pack(side="left")
        self.admin_checkbox.pack(side="left", padx=8)

        ## create button frame
        self.button_frame = tk.Frame(self)
        self.add_account_button = tk.Button(
            self.button_frame,
            text="Add Account",
            font=FONT_4,
            command=self.add_account,
        )
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            font=FONT_4,
            command=self.reload_account_menu,
        )

        self.add_account_button.pack(side="left")
        self.cancel_button.pack(side="left", padx=8)

        ## create grid
        self.grid_rowconfigure(
            tuple([n for n in range(17)]), weight=1, uniform="a"
        )

        ## grid widgets
        self.new_account_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.first_name_label.grid(row=3, column=0, sticky="w")
        self.first_name_entry.grid(row=4, column=0, sticky="w")
        self.last_name_label.grid(row=6, column=0, sticky="w")
        self.last_name_entry.grid(row=7, column=0, sticky="w")
        self.account_type_label.grid(row=9, column=0, sticky="w")
        self.account_type_frame.grid(row=10, column=0, sticky="w")
        self.temporary_password_label.grid(row=12, column=0, sticky="w")
        self.temporary_password_entry.grid(row=13, column=0, sticky="w")
        self.button_frame.grid(row=15, column=0, rowspan=2, sticky="w")

    def details_valid(self):
        if not self.first_name_entry.get():
            return False
        if not self.last_name_entry.get():
            return False
        if self.team_optionmenu_value.get() == "Select a team...":
            return False
        return True

    def add_account(self):
        if self.details_valid():
            firstname = self.first_name_entry.get()
            lastname = self.last_name_entry.get()
            password = self.temporary_password_entry.get()
            if strong(password):
                add_account(
                    create_username(firstname, lastname),
                    firstname,
                    lastname,
                    password,
                    self.team_optionmenu_value.get().lower(),
                    self.admin_checkbox_value.get(),
                )
                self.reload_account_menu()
            else:
                messagebox.showerror(
                    "Error",
                    "Password not strong enough, try using a longer password or a larger variety of character types",
                )
        else:
            messagebox.showerror(
                "Error",
                "The details you've entered do not meet the criteria for validity",
            )

    def reload_account_menu(self):
        self.destroy()
        self.master.account_menu()


if __name__ == "__main__":
    Window(1100, 670).mainloop()
