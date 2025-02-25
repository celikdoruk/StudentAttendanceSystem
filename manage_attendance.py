import tkinter as tk
import pandas as pd
import re
from tkinter import messagebox
from database import Database
from tkinter import filedialog
from datetime import datetime


class ManageAttendanceWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Manage Attendance Records')
        self.geometry('550x510')
        self.db = Database('school_database.db')
        self.create_widgets()
        self.attendance_listbox.bind('<Double-Button-1>', self.on_attendance_select)

    def create_widgets(self):
        self.logo = tk.PhotoImage(file="resized.png")
        logo_label = tk.Label(self, image=self.logo)
        logo_label.grid(column=0, row=0)

        welcome_label = tk.Label(self, text="Welcome to the Attendance Management Window!", font=("Arial", 14))
        welcome_label.grid(column=1, row=0, columnspan=2, pady=15)

        tk.Label(self, text="Attendance ID:").grid(column=0, row=1, sticky='e', pady=4)
        self.attendance_id_entry = tk.Entry(self)
        self.attendance_id_entry.grid(column=1, row=1, sticky='w', pady=4)

        tk.Label(self, text="Attendance Date:").grid(column=0, row=2, sticky='e', pady=4)
        self.attendance_date_entry = tk.Entry(self)
        self.attendance_date_entry.grid(column=1, row=2, sticky='w', pady=4)

        tk.Label(self, text="Student ID:").grid(column=0, row=3, sticky='e', pady=4)
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.grid(column=1, row=3, padx=2,sticky='w', pady=4)

        tk.Label(self, text="Class ID:").grid(column=0, row=4, sticky='e', pady=4)
        self.class_id_entry = tk.Entry(self)
        self.class_id_entry.grid(column=1, row=4, padx=2, sticky='w', pady=4)

        tk.Label(self, text="Status:").grid(column=0, row=5, sticky='e', pady=4)
        self.status_entry = tk.Entry(self)
        self.status_entry.grid(column=1, row=5, padx=2, sticky='w', pady=4)

        tk.Button(self, text=' Add Attendance  ', command=self.add_attendance).grid(column=1, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Update Attendance', command=self.update_attendance).grid(column=2, row=1, columnspan=2, pady=5)
        tk.Button(self, text='Delete Attendance', command=self.delete_attendance).grid(column=1, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' View Attendances', command=self.view_attendance).grid(column=2, row=2, columnspan=2, pady=5)
        tk.Button(self, text=' Clear Fields ', command=self.clear_fields).grid(column=1, row=5, columnspan=4, pady=5)
        tk.Button(self, text='       Exit       ', command=self.quit_app).grid(column=2, row=5, columnspan=4, pady=5)
        tk.Button(self, text='    Import Data   ', command=self.import_data).grid(column=1, row=3, columnspan=2, pady=5)
        tk.Button(self, text='  Class List  ',command=self.class_list).grid(column=1, row=4, columnspan=2, pady=5)
        tk.Button(self, text='     Export Data    ', command=self.export_data).grid(column=2, row=3, columnspan=2, pady=5)
        tk.Button(self, text='  Student List  ', command=self.student_list).grid(column=2, row=4, columnspan=2, pady=5)

        tk.Label(self, text="List of Attendances:").grid(column=0, row=8, columnspan=3, pady=10, sticky='s')
        self.attendance_listbox = tk.Listbox(self, width=80)
        self.attendance_listbox.grid(column=0, row=9, columnspan=4, pady=10, sticky='')

        tk.Label(self, text='Please leave the Attendance ID entry empty, they are automatically generated.').grid(column=0, row=10, columnspan=3, pady=10)

    def add_attendance(self):
        attendance_id = self.attendance_id_entry.get()
        attendance_date = self.attendance_date_entry.get()
        student_id = self.student_id_entry.get()
        class_id = self.class_id_entry.get()
        status = self.status_entry.get()

        if not all([attendance_date, student_id, class_id, status]):
            messagebox.showerror("Input Error", "Except from Attendance ID, all fields must be filled out.")
            return

        existing_attendance = self.db.query_data('SELECT * FROM attendance WHERE attendance_id = ?', (attendance_id,))
        if existing_attendance:
            messagebox.showerror("Attendance Already Exists", "Attendance with that ID already exists.")
            return

        try:
            attendance_date_format = datetime.strptime(attendance_date, '%Y-%m-%d')
        except ValueError as e:
            messagebox.showerror("Input Error", "Attendance date must be in YYYY-MM-DD format.")
            return

        try:
            student_id = int(student_id)
        except ValueError:
            messagebox.showerror("Input Error", "Student ID must be an integer.")
            return

        try:
            class_id = int(class_id)
        except ValueError:
            messagebox.showerror("Input Error", "Class ID must be an integer.")
            return


        if not self.is_valid_status(status):
            return


        self.db.insert_data('INSERT INTO attendance (attendance_date, student_id, class_id, status) VALUES (?, ?, ?, ?)',
                            (attendance_date, student_id, class_id, status))
        messagebox.showinfo("Success", "Attendance added successfully.")

        self.attendance_listbox.delete(0, tk.END)
        self.attendance_id_entry.delete(0, tk.END)
        self.student_id_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)
        self.view_attendance()


    def delete_attendance(self):
        try:
            selected_attendance = self.attendance_listbox.curselection()
            if not selected_attendance:
                raise ValueError("No attendance selected")

            selected_item = self.attendance_listbox.get(selected_attendance)
            attendance_info = selected_item.split(" || ")
            attendance_id = attendance_info[0]

            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Attendance ID: {attendance_id}?")
            if not confirm:
                return

            self.db.delete_data('DELETE FROM attendance WHERE attendance_id = ?', (attendance_id,))
            messagebox.showinfo("Success", "Attendance deleted successfully.")
            self.view_attendance()

        except ValueError as Ve:
            messagebox.showerror("Error", str(Ve))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def update_attendance(self):
        try:
            if not self.attendance_id_entry.get():
                raise ValueError("No attendance record is selected!")

            attendance_id = self.attendance_id_entry.get()
            attendance_date = self.attendance_date_entry.get()
            student_id = self.student_id_entry.get()
            class_id = self.class_id_entry.get()
            status = self.status_entry.get()

            if not all([attendance_date, student_id, class_id, status]):
                messagebox.showerror("Input Error", "Except from Attendance ID, all fields must be filled out.")
                return

            try:
                attendance_date_format = datetime.strptime(attendance_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Input Error", "Attendance date must be in YYYY-MM format.")
                return

            try:
                student_id = int(student_id)
            except ValueError:
                messagebox.showerror("Input Error", "Student ID must be an integer.")
                return

            try:
                class_id = int(class_id)
            except ValueError:
                messagebox.showerror("Input Error", "Class ID must be an integer.")
                return

            if not self.is_valid_status(status):
                return

            confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to update Attendance ID: {attendance_id}?")
            if not confirm:
                return

            self.db.update_data('UPDATE attendance SET attendance_date = ?, student_id = ?, class_id = ?, status = ? WHERE attendance_id = ?',
                                (attendance_date, student_id, class_id, status, attendance_id))
            messagebox.showinfo("Success", "Attendance updated successfully.")

            self.attendance_id_entry.delete(0, tk.END)
            self.attendance_date_entry.delete(0, tk.END)
            self.student_id_entry.delete(0, tk.END)
            self.class_id_entry.delete(0, tk.END)
            self.status_entry.delete(0, tk.END)
            self.view_attendance()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_data(self):
        try:
            file_to_import = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_to_import:
                return

            readed = pd.read_csv(file_to_import)
            df = pd.DataFrame(readed)

            required_columns = ['attendance_id', 'attendance_date', 'student_id', 'class_id', 'status']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Error", f"Column: {col} is not found in CSV file, please check the file again.")
                    return

            for index,data in df.iterrows():
                if pd.isnull(data['attendance_date']) or pd.isnull(data['student_id']) or pd.isnull(data['class_id']) or pd.isnull(data['status']):
                    messagebox.showerror("Error", "Some of the fields in the CSV are missing, please check again.")
                    return

            for id in df['attendance_id']:
                try:
                    id = int(id)
                except ValueError:
                    messagebox.showerror("Error", "Attendance ID must be an integer, check the CSV file.")
                    return

            for date in df['attendance_date']:
                if not self.is_valid_dob(date):
                    return

            for student_id in df['student_id']:
                try:
                    student_id = int(student_id)
                except ValueError:
                    messagebox.showerror("Error", "Student ID must be an integer, check the CSV file.")
                    return

            for class_id in df['class_id']:
                try:
                    class_id = int(class_id)
                except ValueError:
                    messagebox.showerror("Error", "Class ID must be an integer, check the CSV file.")
                    return

            for status in df['status']:
                try:
                    accepted_status =['Present', 'Absent']
                    if status not in accepted_status:
                        messagebox.showerror("Error", f"Status must be one of {accepted_status}. Check the CSV file again.")
                        return
                except ValueError as e:
                    messagebox.showerror("Unexpected Error", str(e))


            for index, data in df.iterrows():
                self.db.insert_data("INSERT INTO attendance (attendance_id, attendance_date, student_id, class_id, status) VALUES (? , ?, ?, ?, ?)",
                                    (data['attendance_id'], data['attendance_date'], data['student_id'], data['class_id'], data['status']))
            messagebox.showinfo("Success", "Data imported successfully.")
            self.view_attendance()

        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {str(e)}")


    def export_data(self):
        try:
            if self.attendance_listbox.size() == 0:
                messagebox.showerror("Error","No attendances to export in the list.")
                return

            attendances = self.db.query_data("SELECT * FROM attendance")

            if not attendances:
                messagebox.showerror("No attendance record to export in the database.")

            df = pd.DataFrame(attendances, columns=['attendance_id', 'attendance_date', 'student_id', 'class_id', 'status'])
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Success", f"Attendance data has been successfully exported to {file_path}.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while exporting data: {e}")

    def view_attendance(self):
        self.attendance_listbox.delete(0, tk.END)
        attendances = self.db.query_data('SELECT * FROM attendance')
        for attendance in attendances:
            attendance_info = f"{attendance[0]} || {attendance[1]} || {attendance[2]} || {attendance[3]} || {attendance[4]}"
            self.attendance_listbox.insert(tk.END, attendance_info)

    def clear_fields(self):
        self.attendance_listbox.delete(0, tk.END)
        self.attendance_id_entry.delete(0, tk.END)
        self.attendance_date_entry.delete(0, tk.END)
        self.student_id_entry.delete(0, tk.END)
        self.class_id_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)

    def on_attendance_select(self, event):
        selected_attendance = self.attendance_listbox.curselection()
        if not selected_attendance:
            return

        selected_item = self.attendance_listbox.get(selected_attendance)
        attendance_info = selected_item.split(" || ")

        self.attendance_id_entry.delete(0, tk.END)
        self.attendance_id_entry.insert(0, attendance_info[0])
        self.attendance_date_entry.delete(0, tk.END)
        self.attendance_date_entry.insert(0, attendance_info[1])
        self.student_id_entry.delete(0, tk.END)
        self.student_id_entry.insert(0, attendance_info[2])
        self.class_id_entry.delete(0, tk.END)
        self.class_id_entry.insert(0, attendance_info[3])
        self.status_entry.delete(0, tk.END)
        self.status_entry.insert(0, attendance_info[4])

    def is_valid_status(self, status):
        if not status or pd.isnull(status):
            return False
        accepted_values = ['Present', 'Absent']
        if status not in accepted_values:
            messagebox.showerror("Input Error",f"Status must be one of {accepted_values}")
        else:
            return True

    def is_valid_dob(self, dob):
        try:
            pd.to_datetime(dob, format='%Y-%m-%d')
            return True
        except ValueError as e:
            messagebox.showerror("Error", "The dates must be in YYYY-MM-DD format, please check the CSV file again.")

    def class_list(self):
        window = tk.Toplevel()
        window.title("Class List")
        window.geometry("500x400")

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END,
                           f"Current Classes in the system: \n\n")

        try:
            get_data = self.db.query_data("SELECT class_name, class_id FROM classes")
        except Exception as e:
            messagebox.showerror("Error", f"Could not reach to the database: {str(e)}.")
            return

        if get_data:
            x = pd.DataFrame(get_data, columns=['class_name', 'class_id'])
            report_text.insert(tk.END, x.to_string(index=False))
        else:
            messagebox.showerror("Error", "Can not insert data.")

        tk.Button(report_frame, text='Close', command=window.destroy).pack(pady=10)


    def student_list(self):
        window = tk.Toplevel()
        window.title("Student List")
        window.geometry("500x400")

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END,
                           f"Current Students in the system: \n\n")

        query = """SELECT 
                    first_name || ' ' || last_name as full_name,
                    student_id
                FROM students"""

        try:
            get_data = self.db.query_data(query)
        except Exception as e:
            messagebox.showerror("Error", f"Could not reach to the database: {str(e)}.")

        if get_data:
            x = pd.DataFrame(get_data, columns=['student_name', 'student_id'])
            report_text.insert(tk.END, x.to_string(index=False))
        else:
            messagebox.showerror("Error", "Can not insert data.")

        tk.Button(report_frame, text='Close', command=window.destroy).pack(pady=10)

    def quit_app(self):
        self.destroy()