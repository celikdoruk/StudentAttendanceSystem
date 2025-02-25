import tkinter as tk
import pandas as pd
import re
from tkinter import messagebox
from database import Database
from tkinter import filedialog
from datetime import datetime


class ManageStudentsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Manage Students')
        self.geometry('480x550')
        self.db = Database('school_database.db')
        self.create_widgets()
        self.student_listbox.bind('<Double-Button-1>', self.on_student_select)

    def create_widgets(self):
        self.logo = tk.PhotoImage(file="resized.png")
        logo_label = tk.Label(self, image=self.logo)
        logo_label.grid(column=0, row=0)

        welcome_label = tk.Label(self, text="Welcome to the Student Management Window!", font=("Arial", 14))
        welcome_label.grid(column=1, row=0, columnspan=2, pady=15)

        tk.Label(self, text="Student ID:").grid(column=0, row=1, sticky='e', pady=4)
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.grid(column=1, row=1, sticky='w', pady=4)

        tk.Label(self, text="First Name:").grid(column=0, row=2, sticky='e', pady=4)
        self.first_name_entry = tk.Entry(self)
        self.first_name_entry.grid(column=1, row=2, sticky='w', pady=4)

        tk.Label(self, text="Last Name:").grid(column=0, row=3, sticky='e', pady=4)
        self.last_name_entry = tk.Entry(self)
        self.last_name_entry.grid(column=1, row=3, padx=2,sticky='w', pady=4)

        tk.Label(self, text="Email:").grid(column=0, row=4, sticky='e', pady=4)
        self.email_entry = tk.Entry(self)
        self.email_entry.grid(column=1, row=4, padx=2, sticky='w', pady=4)

        tk.Label(self, text="Date of Birth:").grid(column=0, row=5, sticky='e', pady=4)
        self.dob_entry = tk.Entry(self)
        self.dob_entry.grid(column=1, row=5, padx=2, sticky='w', pady=4)

        tk.Button(self, text=' Add Student  ', command=self.add_student).grid(column=1, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Update Student', command=self.update_student).grid(column=2, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Delete Student', command=self.delete_students).grid(column=1, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' View Students', command=self.view_students).grid(column=2, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' Clear Fields ', command=self.clear_fields).grid(column=1, row=4, columnspan=4, pady=5)
        tk.Button(self, text='       Exit       ', command=self.quit_app).grid(column=2, row=4, columnspan=4, pady=5)
        tk.Button(self, text='  Import Data ', command=self.import_data).grid(column=1, row=3, columnspan=2, pady=5)
        tk.Button(self, text='  Export Data ', command=self.export_data).grid(column=2, row=3, columnspan=2, pady=5)
        tk.Button(self, text="Student's classes and attendances.", command=self.open_student_class_attendance).grid(column=0, row=11, columnspan=3, pady=5)

        tk.Label(self, text="List of Students:").grid(column=0, row=8, columnspan=3, pady=10, sticky='s')
        self.student_listbox = tk.Listbox(self, width=80)
        self.student_listbox.grid(column=0, row=9, columnspan=4, pady=10, sticky='')

        tk.Label(self, text='Please leave the Student ID entry empty, they are automatically generated.').grid(column=0, row=10, columnspan=3, pady=10)

    def add_student(self):
        student_id = self.student_id_entry.get()
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        dob = self.dob_entry.get()

        if not all([first_name, last_name, email, dob]):
            messagebox.showerror("Input Error", "Except from Student ID, all fields must be filled out.")
            return

        existing_student = self.db.query_data('SELECT * FROM students WHERE student_id = ?', (student_id,))
        if existing_student:
            messagebox.showerror("Student Already Exists", "Student with that ID already exists.")
            return

        name_pattern = re.compile("^[A-Za-z- ]+$")
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not name_pattern.match(first_name) or len(first_name) > 50:
            messagebox.showerror("Input Error", "First name must contain only letters and be less than 50 characters.")
            return

        if not name_pattern.match(last_name) or len(last_name) > 50:
            messagebox.showerror("Input Error", "Last name must contain only letters and be less than 50 characters.")
            return

        if not email_pattern.match(email):
            messagebox.showerror("Input Error", "Email format is invalid!")
            return

        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Input Error", "Date of birth must be in YYYY-MM-DD format.")
            return

        self.db.insert_data('INSERT INTO students (first_name, last_name, email, date_of_birth) VALUES (?, ?, ?, ?)',
                            (first_name, last_name, email, dob))
        messagebox.showinfo("Success", "Student added successfully.")

        self.clear_fields()
        self.view_students()


    def delete_students(self):
        try:
            selected_student = self.student_listbox.curselection()
            if not selected_student:
                raise ValueError("No student selected")

            selected_item = self.student_listbox.get(selected_student)
            student_info = selected_item.split(" || ")
            student_id = student_info[0]

            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Student ID: {student_id}?")
            if not confirm:
                return

            self.db.delete_data('DELETE FROM students WHERE student_id = ?', (student_id,))
            messagebox.showinfo("Success", "Student deleted successfully.")
            self.view_students()

        except ValueError as Ve:
            messagebox.showerror("Error", str(Ve))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def update_student(self):
        try:
            if not self.student_id_entry.get():
                raise ValueError("No student is selected!")

            student_id = self.student_id_entry.get()
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            email = self.email_entry.get()
            dob = self.dob_entry.get()

            if not all([first_name, last_name, email, dob]):
                messagebox.showerror("Input Error", "Except from Student ID, all fields must be filled out.")
                return

            name_pattern = re.compile("^[A-Za-z- ]+$")
            email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

            if not name_pattern.match(first_name) or len(first_name) > 50:
                messagebox.showerror("Input Error",
                                     "First name must contain only letters and be less than 50 characters.")
                return

            if not name_pattern.match(last_name) or len(last_name) > 50:
                messagebox.showerror("Input Error",
                                     "Last name must contain only letters and be less than 50 characters.")
                return

            if not email_pattern.match(email):
                messagebox.showerror("Input Error", "Email format is invalid!")
                return

            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
            except ValueError as e:
                messagebox.showerror("Input Error", "Date of birth must be in YYYY-MM-DD format.")
                return

            confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to update Student ID: {student_id}?")
            if not confirm:
                return

            self.db.update_data('UPDATE students SET first_name = ?, last_name = ?, email = ?, date_of_birth = ? WHERE student_id = ?',
                                (first_name, last_name, email, dob, student_id))
            messagebox.showinfo("Success", "Student updated successfully.")

            self.student_id_entry.delete(0, tk.END)
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.dob_entry.delete(0, tk.END)
            self.view_students()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_data(self):
        try:
            file_to_import = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_to_import:
                return

            readed = pd.read_csv(file_to_import)
            df = pd.DataFrame(readed)

            required_columns = ['first_name', 'last_name', 'email', 'date_of_birth']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Error", f"Column: {col} is not found in CSV file, please check the file again.")
                    return

            for index,data in df.iterrows():
                if pd.isnull(data['first_name']) or pd.isnull(data['last_name']) or pd.isnull(data['email']) or pd.isnull(data['date_of_birth']):
                    messagebox.showerror("Error", "Some of the fields in the CSV are missing, please check again.")
                    return

            for first_name in df['first_name']:
                if not self.is_valid_name(first_name):
                    messagebox.showerror("Error", "First name(s) are invalid, please check the CSV file again.")
                    return

            for last_name in df['last_name']:
                if not self.is_valid_name(last_name):
                    messagebox.showerror("Error", "Last name(s) are invalid, please check the CSV file again.")
                    return

            for email in df['email']:
                if not self.is_valid_email(email):
                    messagebox.showerror("Error", "Email(s) are invalid, please check the CSV file again.")
                    return

            for dob in df['date_of_birth']:
                if not self.is_valid_dob(dob):
                    return

            for index, data in df.iterrows():
                self.db.insert_data("INSERT INTO students (student_id, first_name, last_name, email, date_of_birth) VALUES (? , ?, ?, ?, ?)",
                                    (data['student_id'], data['first_name'], data['last_name'], data['email'], data['date_of_birth']))
            messagebox.showinfo("Success", "Data imported successfully.")
            self.view_students()

        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {str(e)}")


    def export_data(self):
        try:
            if self.student_listbox.size() == 0:
                messagebox.showerror("Error","No student to export in the list.")
                return

            students = self.db.query_data("SELECT * FROM students")

            if not students:
                messagebox.showerror("No students to export in the database.")

            df = pd.DataFrame(students, columns=['student_id', 'first_name', 'last_name', 'email', 'date_of_birth'])
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Success", f"Student data has been successfully exported to {file_path}.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while exporting data: {e}")

    def view_students(self):
        self.student_listbox.delete(0, tk.END)
        students = self.db.query_data('SELECT * FROM students')
        for student in students:
            student_info = f"{student[0]} || {student[1]} || {student[2]} || {student[3]} || {student[4]}"
            self.student_listbox.insert(tk.END, student_info)

    def clear_fields(self):
        self.student_listbox.delete(0, tk.END)
        self.student_id_entry.delete(0, tk.END)
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.dob_entry.delete(0, tk.END)

    def on_student_select(self, event):
        selected_student = self.student_listbox.curselection()
        if not selected_student:
            return

        selected_item = self.student_listbox.get(selected_student)
        student_info = selected_item.split(" || ")

        self.student_id_entry.delete(0, tk.END)
        self.student_id_entry.insert(0, student_info[0])
        self.first_name_entry.delete(0, tk.END)
        self.first_name_entry.insert(0, student_info[1])
        self.last_name_entry.delete(0, tk.END)
        self.last_name_entry.insert(0, student_info[2])
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, student_info[3])
        self.dob_entry.delete(0, tk.END)
        self.dob_entry.insert(0, student_info[4])

    def is_valid_name(self, name):
        if not name or pd.isnull(name):
            return False
        name_pattern = re.compile("^[A-Za-z- ]+$")
        if name_pattern.match(name) and len(name) <= 50:
            return True
        else:
            return False

    def is_valid_dob(self, dob):
        try:
            pd.to_datetime(dob, format='%Y-%m-%d')
            return True
        except ValueError as e:
            messagebox.showerror("Error", "The dates must be in YYYY-MM-DD format, please check the CSV file again.")

    def is_valid_email(self, email):
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def open_student_class_attendance(self):
        query = """
            SELECT class_name, status, attendance_date, teacher_name
            FROM students s 
            JOIN attendance a ON s.student_id = a.student_id
            JOIN classes c ON c.class_id = a.class_id
            WHERE s.student_id = ?
            """

        try:
            selected_student = self.student_listbox.get(self.student_listbox.curselection())
        except tk.TclError:
            messagebox.showerror("Error", "Please select a student.")
            return

        window = tk.Toplevel()
        window.title("Attendance Info")
        window.geometry("700x400")

        splitted_list = selected_student.split(" || ")
        student_id = splitted_list[0]
        student_name = splitted_list[1]
        student_last_name = splitted_list[2]

        try:
            attendance_and_class_record = self.db.query_data(query, (student_id,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not recieve attendance data: {str(e)}.")
            return

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END, f"Attendance Report for {student_name} {student_last_name} with the ID: {student_id}\n\n")

        if attendance_and_class_record:
            data_frame = pd.DataFrame(attendance_and_class_record)
            x = data_frame.groupby(0)[1].value_counts().unstack(fill_value=0)
            report_text.insert(tk.END, x)
        else:
            report_text.insert(tk.END, f"No attendance records found for {student_name} {student_last_name} with the ID: {student_id}")

        tk.Button(window, text="Close", command=window.destroy).pack(pady=10)

    def quit_app(self):
        self.destroy()