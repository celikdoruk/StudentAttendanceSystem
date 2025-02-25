import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database

class ManageReportWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Report Window')
        self.geometry('400x500')
        self.CreateWidgets()
        self.db = Database('school_database.db')

    def CreateWidgets(self):
        self.logo = tk.PhotoImage(file="debreceni_egyetem.png")
        logo_label = tk.Label(self, image=self.logo)
        logo_label.pack(pady=10)

        welcome_label = tk.Label(self, text="Get Reports", font=("Arial", 14))
        welcome_label.pack(pady=10)

        tk.Button(self, text='Students With More Than 3 Attendances', command=self.more_than_3_attendance).pack(pady=10)
        tk.Button(self, text='Number of Classes Attended by Each Student', command=self.no_of_classes_attended_each_student).pack(pady=10)
        tk.Button(self, text='Classes with the Highest Attendance', command=self.classes_highest_attendance).pack(pady=10)
        tk.Button(self, text='Exit', command=self.destroy).pack(pady=10)

    def more_than_3_attendance(self):
        new_window = tk.Toplevel(self)
        new_window.title('Select Class')
        new_window.geometry('300x200')

        data = self.db.query_data("SELECT class_name FROM classes")
        classes = pd.DataFrame(data)
        classes = classes[0].to_list()

        class_label = tk.Label(new_window, text="Select Class")
        class_label.pack(pady=10)

        selected_class = tk.StringVar(new_window)
        selected_class.set(classes[0])

        class_dropdown = tk.OptionMenu(new_window, selected_class, *classes)
        class_dropdown.pack(pady=10)

        check_button = tk.Button(new_window, text='Show Results', command=lambda: self.show_attendance(selected_class.get()))
        check_button.pack(pady=10)

        tk.Button(new_window, text='Exit', command=new_window.destroy).pack(pady=10)

    def show_attendance(self, selected_class):
        query = """
                SELECT 
                    s.first_name || ' ' || s.last_name AS student_name,
                    COUNT(*) as missed_classes 
                FROM students s 
                LEFT JOIN attendance a on s.student_id = a.student_id
                JOIN classes c on c.class_id = a.class_id 
                WHERE c.class_name = ? AND a.status = 'Absent'
                GROUP BY s.first_name || ' ' || s.last_name
                HAVING missed_classes > 3
        """

        data = self.db.query_data(query, (selected_class,))
        df = pd.DataFrame(data, columns = ['student_name', 'missed_classes'])

        window = tk.Toplevel()
        window.title("Students")
        window.geometry("500x400")

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END,
                           f"Students who missed more than 3 classes for {selected_class}: \n\n")
        if not df.empty:
            report_text.insert(tk.END, df.to_string(index=False))
        else:
            report_text.insert(tk.END, "No students who missed more than 3 classes for " + selected_class)

        tk.Button(window, text='Exit', command=window.destroy).pack(pady=10)

    def no_of_classes_attended_each_student(self):
        query = """
                SELECT 
                    s.first_name || ' ' || s.last_name AS student_name,
                    COUNT(*) AS attended_classes
                FROM students s
                JOIN attendance a ON s.student_id = a.student_id
                WHERE a.status = 'Present'
                GROUP BY s.first_name || ' ' || s.last_name
                ORDER BY attended_classes DESC
        """

        data = self.db.query_data(query)
        df = pd.DataFrame(data, columns=['student_name', 'attended_classes'])

        window = tk.Toplevel()
        window.title("Classes Attended by Each Student")
        window.geometry("500x400")

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END, "Number of Classes Attended by Each Student:\n\n")

        if not df.empty:
            report_text.insert(tk.END, df.to_string(index=False))
        else:
            report_text.insert(tk.END, "No attendance records found.")

        tk.Button(window, text='Exit', command=window.destroy).pack(pady=10)


    def classes_highest_attendance(self):
        query = """
                SELECT 
                    c.class_name, COUNT(a.student_id) AS no_of_students 
                FROM classes c 
                JOIN attendance a ON c.class_id = a.class_id
                WHERE a.status = 'Present'
                GROUP BY c.class_name
                ORDER BY no_of_students DESC
        """

        data = self.db.query_data(query)
        df = pd.DataFrame(data, columns = ['class_name', 'no_of_students'])

        window = tk.Toplevel()
        window.title("Classes With The Highest Attendance")
        window.geometry("500x400")

        report_frame = tk.Frame(window)
        report_frame.pack(pady=10)
        report_text = tk.Text(report_frame, width=80, height=20)
        report_text.pack()
        report_text.insert(tk.END, "Classes With The Highest Attendance:\n\n")

        if not df.empty:
            report_text.insert(tk.END, df.to_string(index=False))
        else:
            report_text.insert(tk.END, "No classes who have the highest attendance records found.")

        tk.Button(window, text='Exit', command=window.destroy).pack(pady=10)



