import tkinter as tk
import pandas as pd
import re
from tkinter import messagebox
from database import Database
from tkinter import filedialog
from datetime import datetime


class ManageClassesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Manage Classes')
        self.geometry('480x520')
        self.db = Database('school_database.db')
        self.create_widgets()
        self.class_listbox.bind('<Double-Button-1>', self.on_class_select)

    def create_widgets(self):
        self.logo = tk.PhotoImage(file="resized.png")
        logo_label = tk.Label(self, image=self.logo)
        logo_label.grid(column=0, row=0)

        welcome_label = tk.Label(self, text=" Welcome to the Class Management Window! ", font=("Arial", 14))
        welcome_label.grid(column=1, row=0, columnspan=2, pady=15)

        tk.Label(self, text="Class ID:").grid(column=0, row=1, sticky='e', pady=4)
        self.class_id_entry = tk.Entry(self)
        self.class_id_entry.grid(column=1, row=1, sticky='w', pady=4)

        tk.Label(self, text="Class Name:").grid(column=0, row=2, sticky='e', pady=4)
        self.class_name_entry = tk.Entry(self)
        self.class_name_entry.grid(column=1, row=2, sticky='w', pady=4)

        tk.Label(self, text="Teacher Name:").grid(column=0, row=3, sticky='e', pady=4)
        self.teacher_name_entry = tk.Entry(self)
        self.teacher_name_entry.grid(column=1, row=3, padx=2,sticky='w', pady=4)

        tk.Label(self, text="Class Time:").grid(column=0, row=4, sticky='e', pady=4)
        self.class_time_entry = tk.Entry(self)
        self.class_time_entry.grid(column=1, row=4, padx=2, sticky='w', pady=4)


        tk.Button(self, text=' Add Class  ', command=self.add_class).grid(column=1, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Update Class', command=self.update_class).grid(column=2, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Delete Class', command=self.delete_class).grid(column=1, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' View Classes', command=self.view_class).grid(column=2, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' Clear Fields ', command=self.clear_fields).grid(column=1, row=4, columnspan=4, pady=5)
        tk.Button(self, text='       Exit       ', command=self.quit_app).grid(column=2, row=4, columnspan=4, pady=5)
        tk.Button(self, text='  Import Data ', command=self.import_data).grid(column=1, row=3, columnspan=2, pady=5)
        tk.Button(self, text='  Export Data ', command=self.export_data).grid(column=2, row=3, columnspan=2, pady=5)
        tk.Button(self,text='Enrolled Students', command=self.enrolled_students).grid(column=0, row=11, columnspan=3, pady=5)

        tk.Label(self, text="List of Classes:").grid(column=0, row=8, columnspan=3, pady=10, sticky='s')
        self.class_listbox = tk.Listbox(self, width=80)
        self.class_listbox.grid(column=0, row=9, columnspan=4, pady=10, sticky='')

        tk.Label(self, text='Please leave the Class ID entry empty, they are automatically generated.').grid(column=0, row=10, columnspan=3, pady=10)

    def add_class(self):
        class_id = self.class_id_entry.get()
        class_name = self.class_name_entry.get()
        teacher_name = self.teacher_name_entry.get()
        class_time = self.class_time_entry.get()

        if not all([class_name, teacher_name, class_time]):
            messagebox.showerror("Input Error", "Except from Class ID, all fields must be filled out.")
            return

        existing_class = self.db.query_data('SELECT * FROM classes WHERE class_id = ?', (class_id,))
        if existing_class:
            messagebox.showerror("Class Already Exists", "Class with that ID already exists.")
            return

        name_pattern = re.compile("^[A-Za-z0-9- ]+$")
        time_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)-([1-9]|1[0-2])(AM|PM)$")

        if not name_pattern.match(class_name) or len(class_name) > 50:
            messagebox.showerror("Input Error", "Class name must contain only letters and/or numbers and be less than 50 characters.")
            return

        if not name_pattern.match(teacher_name) or len(teacher_name) > 50:
            messagebox.showerror("Input Error", "Teacher name must contain only letters and be less than 50 characters.")
            return

        if not time_pattern.match(class_time):
            messagebox.showerror("Input Error", "Class time must be in format Day-HourPeriod (e.g., Monday-9AM or Tuesday-14PM).")
            return


        self.db.insert_data('INSERT INTO classes (class_name, teacher_name, class_time) VALUES (?, ?, ?)',
                            (class_name, teacher_name, class_time))
        messagebox.showinfo("Success", "Class added successfully.")

        self.clear_fields()
        self.view_class()


    def delete_class(self):
        try:
            selected_class = self.class_listbox.curselection()
            if not selected_class:
                raise ValueError("No class is selected")

            selected_item = self.class_listbox.get(selected_class)
            class_info = selected_item.split(" || ")
            class_id = class_info[0]

            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Class ID: {class_id}?")
            if not confirm:
                return

            self.db.delete_data('DELETE FROM classes WHERE class_id = ?', (class_id,))
            messagebox.showinfo("Success", "Class deleted successfully.")
            self.view_class()

        except ValueError as Ve:
            messagebox.showerror("Error", str(Ve))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def update_class(self):
        try:
            if not self.class_id_entry.get():
                raise ValueError("No class is selected!")

            class_id = self.class_id_entry.get()
            class_name = self.class_name_entry.get()
            teacher_name = self.teacher_name_entry.get()
            class_time = self.class_time_entry.get()

            if not all([class_name, teacher_name, class_time]):
                messagebox.showerror("Input Error", "Except from Class ID, all fields must be filled out.")
                return

            name_pattern = re.compile("^[A-Za-z- ]+$")
            time_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)-([1-9]|1[0-2])(AM|PM)$")

            if not name_pattern.match(class_name) or len(class_name) > 50:
                messagebox.showerror("Input Error",
                                     "Class name must contain only letters and be less than 50 characters.")
                return

            if not name_pattern.match(teacher_name) or len(teacher_name) > 50:
                messagebox.showerror("Input Error",
                                     "Teacher name must contain only letters and be less than 50 characters.")
                return

            if not time_pattern.match(class_time):
                messagebox.showerror("Input Error", "Class time must be in format Day-HourPeriod (e.g., Monday-9AM or Tuesday-14PM).")
                return

            confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to update Class ID: {class_id}?")
            if not confirm:
                return

            self.db.update_data('UPDATE classes SET class_name = ?, teacher_name = ?, class_time = ? WHERE class_id = ?',
                                (class_name, teacher_name, class_time, class_id))
            messagebox.showinfo("Success", "Class updated successfully.")

            self.class_id_entry.delete(0, tk.END)
            self.class_name_entry.delete(0, tk.END)
            self.teacher_name_entry.delete(0, tk.END)
            self.class_time_entry.delete(0, tk.END)
            self.view_class()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_data(self):
        try:
            file_to_import = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_to_import:
                return

            readed = pd.read_csv(file_to_import)
            df = pd.DataFrame(readed)

            required_columns = ['class_name', 'teacher_name', 'class_time']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Error", f"Column: {col} is not found in CSV file, please check the file again.")
                    return

            for index,data in df.iterrows():
                if pd.isnull(data['class_name']) or pd.isnull(data['teacher_name']) or pd.isnull(data['class_time']):
                    messagebox.showerror("Error", "Some of the fields in the CSV are missing, please check again.")
                    return

            for class_name in df['class_name']:
                if not self.is_valid_name(class_name):
                    messagebox.showerror("Error", "Class name(s) are invalid, please check the CSV file again.")
                    return

            for teacher_name in df['teacher_name']:
                if not self.is_valid_name(teacher_name):
                    messagebox.showerror("Error", "Teacher name(s) are invalid, please check the CSV file again.")
                    return

            for class_time in df['class_time']:
                if not self.is_valid_class_time(class_time):
                    return

            for index, data in df.iterrows():
                self.db.insert_data("INSERT INTO classes (class_id, class_name, teacher_name, class_time) VALUES (? , ?, ?, ?)",
                                    (data['class_id'], data['class_name'], data['teacher_name'], data['class_time']))
            messagebox.showinfo("Success", "Data imported successfully.")
            self.view_class()

        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {str(e)}")


    def export_data(self):
        try:
            if self.class_listbox.size() == 0:
                messagebox.showerror("Error","No class to export in the list.")
                return

            classes = self.db.query_data("SELECT * FROM classes")

            if not classes:
                messagebox.showerror("No class to export in the database.")

            df = pd.DataFrame(classes, columns=['class_id', 'class_name', 'teacher_name', 'class_time'])
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Success", f"Class data has been successfully exported to {file_path}.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while exporting data: {e}")

    def view_class(self):
        self.class_listbox.delete(0, tk.END)
        classes = self.db.query_data('SELECT * FROM classes')
        for class1 in classes:
            class_info = f"{class1[0]} || {class1[1]} || {class1[2]} || {class1[3]}"
            self.class_listbox.insert(tk.END, class_info)

    def clear_fields(self):
        self.class_listbox.delete(0, tk.END)
        self.class_id_entry.delete(0, tk.END)
        self.class_name_entry.delete(0, tk.END)
        self.teacher_name_entry.delete(0, tk.END)
        self.class_time_entry.delete(0, tk.END)

    def on_class_select(self, event):
        selected_class = self.class_listbox.curselection()
        if not selected_class:
            return

        selected_item = self.class_listbox.get(selected_class)
        class_info = selected_item.split(" || ")

        self.class_id_entry.delete(0, tk.END)
        self.class_id_entry.insert(0, class_info[0])
        self.class_name_entry.delete(0, tk.END)
        self.class_name_entry.insert(0, class_info[1])
        self.teacher_name_entry.delete(0, tk.END)
        self.teacher_name_entry.insert(0, class_info[2])
        self.class_time_entry.delete(0, tk.END)
        self.class_time_entry.insert(0, class_info[3])

    def is_valid_name(self, name):
        if not name or pd.isnull(name):
            return False
        name_pattern = re.compile("^[A-Za-z0-9- ]+$")
        if name_pattern.match(name) and len(name) <= 50:
            return True
        else:
            return False

    def is_valid_class_time(self, class_time):
        try:
            pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)-(\d{1,2})(AM|PM)$')
            if not pattern.match(class_time):
                raise ValueError("Class time must be in the format 'Day-HourPeriod', e.g. 'Tuesday-14PM'.")

            day, hour, period = pattern.match(class_time).groups()
            hour = int(hour)

            if (period == "AM" and (hour < 1 or hour > 12)) or (period == "PM" and (hour < 1 or hour > 12)):
                raise ValueError("Hour must be between 1 and 12 inclusive for AM/PM format.")
            return True

        except ValueError as Ve:
            messagebox.showerror("Error", str(Ve))
            return False

    def enrolled_students(self):
        query = """
                SELECT 
                    s.first_name || ' ' || s.last_name AS full_name,
                    s.student_id,
                    COUNT(CASE WHEN a.status = 'Absent' THEN 1 ELSE NULL END) AS no_of_absences
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                JOIN classes c ON c.class_id = a.class_id
                WHERE c.class_id = ?
                GROUP BY full_name;
        """

        try:
            selected_class = self.class_listbox.get(self.class_listbox.curselection())
        except tk.TclError:
            messagebox.showerror("Error", "Please select a class.")
            return

        window = tk.Toplevel()
        window.title("Enrolled Students")
        window.geometry("500x400")

        the_class = selected_class.split(' || ')
        class_id = the_class[0]
        class_name = the_class[1]

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END,
                           f"Enrolled Students for {class_name} with the CLass ID: {class_id}\n\n")

        try:
            enrollment_data = self.db.query_data(query, (class_id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not receive enrollment data: {str(e)} ")
            return

        if enrollment_data:
            dataframe = pd.DataFrame(enrollment_data, columns=['STUDENTS', 'Student ID', 'Number of Absences'])
            report_text.insert(tk.END, dataframe.to_string(index=False))
        else:
            report_text.insert(tk.END, f"No enrollment data found for class {class_name}.")

        tk.Button(report_frame, text="Close", command=window.destroy).pack(pady=10)


    def quit_app(self):
        self.destroy()