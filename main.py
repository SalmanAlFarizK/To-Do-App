import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector


class Task:
    def __init__(self, task, status):
        self.task = task
        self.status = status


class ToDoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)

        self.entry = tk.Entry(self.input_frame, font=("Helvetica", 14), width=35)
        self.entry.pack(side=tk.LEFT)

        self.add_button = tk.Button(self.input_frame, text="Add Task", command=self.add_task, width=10)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Task", "Status"), show="headings", height=10)
        self.tree.pack()

        self.tree.heading("#1", text="Task")
        self.tree.heading("#2", text="Status")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Task", command=self.delete_task, width=15)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.mark_done_button = tk.Button(self.button_frame, text="Mark as Done", command=self.mark_task_as_done,
                                          width=15)
        self.mark_done_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear All", command=self.clear_tasks, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.create_table()
        self.load_tasks_from_db()

    def create_table(self):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INT AUTO_INCREMENT PRIMARY KEY, task TEXT, status INT DEFAULT 0)")
        conn.commit()
        conn.close()

    @staticmethod
    def get_mysql_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="9633",
            database="todolist"
        )

    def add_task(self):
        task = self.entry.get()
        if task:
            self.tree.insert("", tk.END, values=(task, "Not Done"))
            self.entry.delete(0, tk.END)
            self.save_task_to_db(task, status="Not Done")
        else:
            messagebox.showwarning("Warning", "Please enter a task.")

    def delete_task(self):
        try:
            selected_item = self.tree.selection()[0]
            task, status = self.tree.item(selected_item)["values"]
            self.tree.delete(selected_item)
            self.delete_task_from_db(task)
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def mark_task_as_done(self):
        try:
            selected_item = self.tree.selection()[0]
            task, status = self.tree.item(selected_item)["values"]
            new_status = "Done" if status == "Not Done" else "Not Done"
            self.tree.item(selected_item, values=(task, new_status))
            self.update_task_status_in_db(task, new_status)
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to mark as done.")

    def clear_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.clear_tasks_in_db()

    def save_task_to_db(self, task, status):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, status) VALUES (%s, %s)", (task, 1 if status == "Done" else 0))
        conn.commit()
        conn.close()

    def load_tasks_from_db(self):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT task, status FROM tasks")
        tasks = cursor.fetchall()
        conn.close()
        for task, status in tasks:
            self.tree.insert("", tk.END, values=(task, "Done" if status else "Not Done"))

    def delete_task_from_db(self, task):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task=%s", (task,))
        conn.commit()
        conn.close()

    def update_task_status_in_db(self, task, status):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status=%s WHERE task=%s", (1 if status == "Done" else 0, task))
        conn.commit()
        conn.close()

    def clear_tasks_in_db(self):
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    r = tk.Tk()
    app = ToDoListApp(r)
    r.mainloop()
