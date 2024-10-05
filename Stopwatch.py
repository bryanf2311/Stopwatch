import tkinter as tk
from tkinter import ttk
import threading
import json
import os

class Stopwatch:
    def __init__(self, root, save_path):
        self.root = root
        self.root.title("Focus Mode")
        self.save_path = "C:\\Users\\bryan\\Documents\\Stopwatch"

        self.tab_control = ttk.Notebook(root)
        self.stopwatch_tab = ttk.Frame(self.tab_control)
        self.highscores_tab = ttk.Frame(self.tab_control)
        self.week_tab = ttk.Frame(self.tab_control)
        self.month_tab = ttk.Frame(self.tab_control)
        self.year_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.stopwatch_tab, text='Stopwatch')
        self.tab_control.add(self.highscores_tab, text='Highscores')
        self.tab_control.add(self.week_tab, text='Past 7 Days')
        self.tab_control.add(self.month_tab, text='Past Month')
        self.tab_control.add(self.year_tab, text='Past Year')
        self.tab_control.pack(expand=1, fill="both")

        self.label = tk.Label(self.stopwatch_tab, text="00:00:00", font=("Helvetica", 48))
        self.label.pack()

        self.start_button = tk.Button(self.stopwatch_tab, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self.stopwatch_tab, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT)
        self.reset_button = tk.Button(self.stopwatch_tab, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        self.running = False
        self.time_elapsed = 0
        self.highscores = self.load_data('highscores.json')
        self.focus_hours = self.load_data('focus_hours.json', default={ "week": 0, "month": 0, "year": 0 })

        self.highscores_listbox = tk.Listbox(self.highscores_tab, height=10)
        self.highscores_listbox.pack()
        self.delete_button = tk.Button(self.highscores_tab, text="Delete Selected", command=self.delete_highscore)
        self.delete_button.pack()

        self.week_goal_var = tk.IntVar()
        self.month_goal_var = tk.IntVar()
        self.year_goal_var = tk.IntVar()
        self.create_goal_tab(self.week_tab, "Past 7 Days", self.week_goal_var, "week")
        self.create_goal_tab(self.month_tab, "Past Month", self.month_goal_var, "month")
        self.create_goal_tab(self.year_tab, "Past Year", self.year_goal_var, "year")

        self.display_highscores()

    def update_time(self):
        if self.running:
            self.time_elapsed += 1
            minutes, seconds = divmod(self.time_elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.label.config(text=time_string)
            self.root.after(1000, self.update_time)

    def start(self):
        if not self.running:
            self.running = True
            self.update_time()

    def stop(self):
        if self.running:
            self.running = False
            self.add_highscore()
            self.update_focus_hours()

    def reset(self):
        self.time_elapsed = 0
        self.label.config(text="00:00:00")
        self.running = False

    def add_highscore(self):
        minutes, seconds = divmod(self.time_elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.highscores.append(time_string)
        self.highscores_listbox.insert(tk.END, time_string)
        self.save_data('highscores.json', self.highscores)

    def delete_highscore(self):
        selected_index = self.highscores_listbox.curselection()
        if selected_index:
            self.highscores_listbox.delete(selected_index)
            del self.highscores[selected_index[0]]
            self.save_data('highscores.json', self.highscores)

    def update_focus_hours(self):
        self.focus_hours['week'] += self.time_elapsed / 3600
        self.focus_hours['month'] += self.time_elapsed / 3600
        self.focus_hours['year'] += self.time_elapsed / 3600
        self.save_data('focus_hours.json', self.focus_hours)
        self.update_progress_bar('week')
        self.update_progress_bar('month')
        self.update_progress_bar('year')

    def create_goal_tab(self, tab, title, goal_var, period):
        label = tk.Label(tab, text=title, font=("Helvetica", 24))
        label.pack()
        goal_entry = tk.Entry(tab, textvariable=goal_var)
        goal_entry.pack()
        self.set_goal_button = tk.Button(tab, text="Set Goal", command=lambda: self.save_goals())
        self.set_goal_button.pack()
        progress_label = tk.Label(tab, text="Progress")
        progress_label.pack()
        progress_bar = ttk.Progressbar(tab, orient="horizontal", mode="determinate", maximum=goal_var.get())
        progress_bar.pack(fill='x')
        setattr(self, f'{period}_progress_bar', progress_bar)
        self.update_progress_bar(period)

    def update_progress_bar(self, period):
        progress_bar = getattr(self, f'{period}_progress_bar')
        progress_bar['value'] = self.focus_hours[period]

    def load_data(self, filename, default=None):
        file_path = os.path.join(self.save_path, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return default or []

    def save_data(self, filename, data):
        file_path = os.path.join(self.save_path, filename)
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def save_goals(self):
        goals = {
            "week": self.week_goal_var.get(),
            "month": self.month_goal_var.get(),
            "year": self.year_goal_var.get()
        }
        self.save_data('goals.json', goals)
        self.update_progress_bar('week')
        self.update_progress_bar('month')
        self.update_progress_bar('year')

    def display_highscores(self):
        for highscore in self.highscores:
            self.highscores_listbox.insert(tk.END, highscore)

def run_app(save_path):
    root = tk.Tk()
    stopwatch = Stopwatch(root, save_path)
    root.mainloop()

# Specify the path where you want to save the highscores.json
save_path = os.path.expanduser("~")  # This will save in the user's home directory
# Run the GUI in a separate thread
app_thread = threading.Thread(target=run_app, args=(save_path,))
app_thread.start()

# Now the terminal is free for other tasks
