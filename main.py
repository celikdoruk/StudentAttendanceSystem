import tkinter as tk
from tkinter import messagebox
from database import Database
from manage_students import ManageStudentsWindow
from manage_classes import ManageClassesWindow
from manage_attendance import ManageAttendanceWindow
from manage_report import ManageReportWindow

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Student Attendance System')
        self.geometry('400x550')

        self.logo = tk.PhotoImage(file="debreceni_egyetem.png")
        logo_label = tk.Label(self, image=self.logo)
        logo_label.pack(pady=10)

        welcome_label = tk.Label(self, text="Welcome to the Student Attendance System!", font=("Arial", 14))
        welcome_label.pack(pady=10)

        tk.Button(self, text='Manage Students', command=self.open_student_window).pack(pady=10)
        tk.Button(self, text='Manage Classes', command=self.open_class_window).pack(pady=10)
        tk.Button(self, text='Manage Attendance', command=self.open_attendance_window).pack(pady=10)
        tk.Button(self, text='Get Report', command=self.open_report_window).pack(pady=10)
        tk.Button(self, text='Exit', command=self.quit).pack(pady=10)

    def open_student_window(self):
        ManageStudentsWindow(self)

    def open_class_window(self):
        ManageClassesWindow(self)

    def open_attendance_window(self):
        ManageAttendanceWindow(self)

    def open_report_window(self):
        ManageReportWindow(self)

    def quit_app(self):
        self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()