import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from tkinter import Scrollbar
from tkinter.simpledialog import askfloat

class Project:
    def __init__(self, project_id, name, start_date, end_date, description, status="", assigned_employees=None):
        self.project_id = project_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.status = status
        self.assigned_employees = assigned_employees if assigned_employees else []

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'name': self.name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'description': self.description,
            'status': self.status,
            'assigned_employees': self.assigned_employees
        }

    @classmethod
    def from_dict(cls, project_dict):
        return cls(
            project_dict['project_id'],
            project_dict['name'],
            datetime.strptime(project_dict['start_date'], '%Y-%m-%d'),
            datetime.strptime(project_dict['end_date'], '%Y-%m-%d'),
            project_dict['description'],
            project_dict.get('status', ''),
            project_dict.get('assigned_employees', [])
        )


class Employee:
    def __init__(self, employee_id, department_id, salary_id, name, dob, gender, ethnicity, id_number, id_issued_place, position, hired_date=None):
        self.employee_id = employee_id
        self.department_id = department_id
        self.salary_id = salary_id
        self.name = name
        self.dob = dob
        self.gender = gender
        self.ethnicity = ethnicity
        self.id_number = id_number
        self.id_issued_place = id_issued_place
        self.position = position
        self.hired_date = hired_date if hired_date else datetime.now()

class EmployeeManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Quản lý nhân viên")
        self.geometry("1200x600")
        self.configure(background="#F0F0F0")

        self.projects = []
        self.employees = []
        self.activity_history = []
        self.attendance = {}

        self.create_widgets()
        self.load_data()
        self.load_attendance_data()
        self.create_attendance_list()
        self.load_attendance_data()
        self.load_salary_data()
        self.load_project_data()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.employee_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.attendance_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.history_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.salary_frame = tk.Frame(self.notebook, bg="#F0F0F0")

        self.notebook.add(self.employee_frame, text="Nhân viên")
        self.notebook.add(self.attendance_frame, text="Điểm danh")
        self.notebook.add(self.history_frame, text="Lịch sử hoạt động")
        self.notebook.add(self.salary_frame, text="Bảng lương")

        self.salary_tree = ttk.Treeview(self.salary_frame, columns=("Name", "Employee ID", "Department ID", "Salary ID", "Total Salary", "Month"), show="headings")

        self.salary_tree.heading("Name", text="Tên nhân viên", anchor="center")
        self.salary_tree.heading("Employee ID", text="Mã NV", anchor="center")
        self.salary_tree.heading("Department ID", text="Mã Phòng", anchor="center")
        self.salary_tree.heading("Salary ID", text="Mã Lương", anchor="center")
        self.salary_tree.heading("Total Salary", text="Tổng Lương", anchor="center")
        self.salary_tree.heading("Month", text="Tháng", anchor="center")

        self.salary_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=6)

        y_scrollbar = ttk.Scrollbar(self.salary_frame, orient="vertical", command=self.salary_tree.yview)
        x_scrollbar = ttk.Scrollbar(self.salary_frame, orient="horizontal", command=self.salary_tree.xview)
        self.salary_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")

        self.salary_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # New Project Frame
        self.project_frame = tk.Frame(self.notebook, bg="#F0F0F0")
        self.notebook.add(self.project_frame, text="Dự án")

        self.project_tree = ttk.Treeview(self.project_frame, columns=("Name", "Start Date", "End Date", "Description", "Status", "Assigned Employees"), show="headings")
        self.project_tree.heading("Name", text="Tên dự án", anchor=tk.CENTER)
        self.project_tree.heading("Start Date", text="Ngày bắt đầu", anchor=tk.CENTER)
        self.project_tree.heading("End Date", text="Ngày kết thúc", anchor=tk.CENTER)
        self.project_tree.heading("Description", text="Mô tả", anchor=tk.CENTER)
        self.project_tree.heading("Status", text="Trạng thái", anchor=tk.CENTER)  # Thêm cột Trạng thái
        self.project_tree.heading("Assigned Employees", text="Mã NV Join", anchor=tk.CENTER)  # Thêm cột Nhân viên tham gia
        self.project_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Buttons for project frame
        add_project_button = tk.Button(self.project_frame, text="Thêm dự án", command=self.add_project, bg="#4CAF50", fg="white")
        add_project_button.pack(side=tk.LEFT, padx=5, pady=5)

        edit_project_button = tk.Button(self.project_frame, text="Sửa dự án", command=self.edit_project, bg="#FFA500", fg="white")
        edit_project_button.pack(side=tk.LEFT, padx=5, pady=5)

        delete_project_button = tk.Button(self.project_frame, text="Xóa dự án", command=self.delete_project, bg="#FF0000", fg="white")
        delete_project_button.pack(side=tk.LEFT, padx=5, pady=5)

        assign_employee_button = tk.Button(self.project_frame, text="Gán nhân viên", command=self.assign_employee_to_project)
        assign_employee_button.pack(side=tk.LEFT, padx=5, pady=5)


        search_label = tk.Label(self.project_frame, text="Tìm kiếm:", bg="#F0F0F0")
        search_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Đổi tên biến search_entry thành search_entry_project
        self.search_entry_project = tk.Entry(self.project_frame)
        self.search_entry_project.pack(side=tk.LEFT, padx=5, pady=5)

        search_button = tk.Button(self.project_frame, text="Tìm kiếm", command=self.search_project, bg="#1E90FF", fg="white", width=10)
        search_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add sorting functionality
        sort_options = ["Tên dự án", "Ngày bắt đầu", "Ngày kết thúc"]
        self.sort_variable = tk.StringVar(self.project_frame)
        self.sort_variable.set(sort_options[0])
        sort_dropdown = tk.OptionMenu(self.project_frame, self.sort_variable, *sort_options, command=self.sort_projects)
        sort_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Widgets for attendance frame
        self.attendance_tree = ttk.Treeview(self.attendance_frame, columns=("Employee ID", "Department ID", "Salary ID", "Name", "Check In Time"), show="headings")
        self.attendance_tree.heading("Employee ID", text="Mã NV", anchor=tk.CENTER)
        self.attendance_tree.heading("Department ID", text="Mã Phòng", anchor=tk.CENTER)
        self.attendance_tree.heading("Salary ID", text="Mã Lương", anchor=tk.CENTER)
        self.attendance_tree.heading("Name", text="Tên nhân viên", anchor=tk.CENTER)
        self.attendance_tree.heading("Check In Time", text="Thời gian chấm công", anchor=tk.CENTER)

        self.attendance_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Add vertical scrollbar
        v_scrollbar = Scrollbar(self.attendance_frame, orient="vertical", command=self.attendance_tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.attendance_tree.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = Scrollbar(self.attendance_frame, orient="horizontal", command=self.attendance_tree.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        self.attendance_tree.configure(xscrollcommand=h_scrollbar.set)

        # Widgets for employee frame
        self.employee_tree = ttk.Treeview(self.employee_frame, columns=("Name", "Position", "Employee ID", "Department ID", "Salary ID", "DOB", "Gender", "Ethnicity", "ID Number", "ID Issued Place"))
        self.employee_tree.heading("#0", text="STT", anchor=tk.CENTER)
        self.employee_tree.heading("Name", text="Tên", anchor=tk.CENTER)
        self.employee_tree.heading("Position", text="Chức vụ", anchor=tk.CENTER)
        self.employee_tree.heading("Employee ID", text="Mã NV", anchor=tk.CENTER)
        self.employee_tree.heading("Department ID", text="Mã phòng", anchor=tk.CENTER)
        self.employee_tree.heading("Salary ID", text="Mã lương", anchor=tk.CENTER)
        self.employee_tree.heading("DOB", text="Ngày sinh", anchor=tk.CENTER)
        self.employee_tree.heading("Gender", text="Giới tính", anchor=tk.CENTER)
        self.employee_tree.heading("Ethnicity", text="Dân tộc", anchor=tk.CENTER)
        self.employee_tree.heading("ID Number", text="CMND/CCCD", anchor=tk.CENTER)
        self.employee_tree.heading("ID Issued Place", text="Nơi cấp", anchor=tk.CENTER)
        
        y_scrollbar = ttk.Scrollbar(self.employee_frame, orient="vertical", command=self.employee_tree.yview)
        x_scrollbar = ttk.Scrollbar(self.employee_frame, orient="horizontal", command=self.employee_tree.xview)
        self.employee_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        
        self.employee_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        button_frame = tk.Frame(self.employee_frame, bg="#F0F0F0")
        button_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Thêm ô nhập mã nhân viên và nút tìm kiếm vào button_frame
        search_label = tk.Label(button_frame, text="Mã nhân viên:", bg="#F0F0F0")
        search_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.search_entry = tk.Entry(button_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)

        search_button = tk.Button(button_frame, text="Tìm kiếm", command=self.search_employee, bg="#1E90FF", fg="white", width=10)
        search_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Thêm nút sắp xếp danh sách vào button_frame
        sort_options = ["Tên", "Mã NV", "Mã phòng", "Mã lương", "Ngày sinh"]
        sort_variable = tk.StringVar(button_frame)
        sort_variable.set(sort_options[0])
        sort_dropdown = tk.OptionMenu(button_frame, sort_variable, *sort_options, command=self.sort_employees)
        sort_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Thêm các nút thêm nhân viên, sửa, xóa, tính lương vào button_frame
        add_button = tk.Button(button_frame, text="Thêm nhân viên", command=self.add_employee, bg="#4CAF50", fg="white", width=15)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(button_frame, text="Sửa nhân viên", command=self.edit_employee, bg="#FFA500", fg="white", width=15)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Xóa nhân viên", command=self.delete_employee, bg="#FF0000", fg="white", width=15)
        delete_button.pack(side=tk.LEFT, padx=5)

        # Widgets for history frame
        self.history_listbox = tk.Listbox(self.history_frame, bg="#FFFFFF", selectbackground="#D5E8D4")
        self.history_listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Bind double click event to show employee details
        self.employee_tree.bind("<Double-1>", self.show_employee_details)
        self.attendance_tree.bind("<Double-1>", self.show_attendance_history)
        self.project_tree.bind("<Double-1>", self.show_project_details_on_double_click)


        # Tạo frame mới cho tab "Bảng lương"
        self.salary_button_frame = tk.Frame(self.salary_frame, bg="#F0F0F0")
        self.salary_button_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Di chuyển nút "Tính lương" vào frame mới
        calculate_salary_button = tk.Button(self.salary_button_frame, text="Tính lương", command=self.calculate_salary, bg="#1E90FF", fg="white", width=15)
        calculate_salary_button.pack(side=tk.LEFT, padx=5)

        # Widgets for attendance frame
        self.select_employee_tree = ttk.Treeview(self.attendance_frame, columns=("Name", "Employee ID", "Department ID", "Salary ID"), show="headings")
        self.select_employee_tree.heading("Name", text="Tên nhân viên", anchor="center")
        self.select_employee_tree.heading("Employee ID", text="Mã NV", anchor="center")
        self.select_employee_tree.heading("Department ID", text="Mã Phòng", anchor="center")
        self.select_employee_tree.heading("Salary ID", text="Mã Lương", anchor="center")
        self.select_employee_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Add vertical scrollbar
        select_y_scrollbar = ttk.Scrollbar(self.attendance_frame, orient="vertical", command=self.select_employee_tree.yview)
        select_y_scrollbar.pack(side="right", fill="y")
        self.select_employee_tree.configure(yscroll=select_y_scrollbar.set)

        # Add horizontal scrollbar
        select_x_scrollbar = ttk.Scrollbar(self.attendance_frame, orient="horizontal", command=self.select_employee_tree.xview)
        select_x_scrollbar.pack(side="bottom", fill="x")
        self.select_employee_tree.configure(xscroll=select_x_scrollbar.set)

        # New frame to contain buttons
        button_frame = tk.Frame(self.attendance_frame, bg="#F0F0F0")
        button_frame.pack(pady=10)

        mark_attendance_button = tk.Button(button_frame, text="Chấm công", command=self.mark_attendance, bg="#4CAF50", fg="white")
        mark_attendance_button.pack(side=tk.LEFT, padx=10)

        delete_attendance_button = tk.Button(button_frame, text="Xóa điểm danh", command=self.delete_attendance, bg="#FF0000", fg="white")
        delete_attendance_button.pack(side=tk.LEFT, padx=10)

    def add_project(self):
        project_window = tk.Toplevel(self)
        project_window.title("Thêm dự án")

        name_label = tk.Label(project_window, text="Tên dự án:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = tk.Entry(project_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        start_date_label = tk.Label(project_window, text="Ngày bắt đầu (YYYY-MM-DD):")
        start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = tk.Entry(project_window)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)

        end_date_label = tk.Label(project_window, text="Ngày kết thúc (YYYY-MM-DD):")
        end_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = tk.Entry(project_window)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5)

        description_label = tk.Label(project_window, text="Mô tả:")
        description_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.description_entry = tk.Text(project_window, width=30, height=5)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        save_button = tk.Button(project_window, text="Lưu", command=self.save_new_project, bg="#4CAF50", fg="white")
        save_button.grid(row=4, columnspan=2, padx=5, pady=5)

    def save_new_project(self):
        name = self.name_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        description = self.description_entry.get("1.0", tk.END).strip()

        if not (name and start_date_str and end_date_str and description):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Định dạng ngày không hợp lệ!")
            return

        project_id = len(self.projects) + 1
        new_project = Project(project_id, name, start_date, end_date, description)
        self.projects.append(new_project)
        self.update_project_tree()
        self.save_project_data()
        messagebox.showinfo("Thông báo", "Thêm dự án thành công!")
        self.name_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)

        # Lưu thông tin dự án
        self.save_project_data()
        self.update_activity_history(f"Thêm Dự Án: {name}")
        

    def edit_project(self):
        selected_items = self.project_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án để sửa!")
            return

        selected_item = selected_items[0]
        project_id = int(self.project_tree.item(selected_item, "text"))
        selected_project = self.projects[project_id - 1]

        edit_window = tk.Toplevel(self)
        edit_window.title("Sửa dự án")

        name_label = tk.Label(edit_window, text="Tên dự án:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_name_entry = tk.Entry(edit_window)
        self.edit_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.edit_name_entry.insert(tk.END, selected_project.name)

        start_date_label = tk.Label(edit_window, text="Ngày bắt đầu (YYYY-MM-DD):")
        start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_start_date_entry = tk.Entry(edit_window)
        self.edit_start_date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.edit_start_date_entry.insert(tk.END, selected_project.start_date.strftime("%Y-%m-%d"))

        end_date_label = tk.Label(edit_window, text="Ngày kết thúc (YYYY-MM-DD):")
        end_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_end_date_entry = tk.Entry(edit_window)
        self.edit_end_date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.edit_end_date_entry.insert(tk.END, selected_project.end_date.strftime("%Y-%m-%d"))

        description_label = tk.Label(edit_window, text="Mô tả:")
        description_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_description_entry = tk.Text(edit_window, width=30, height=5)
        self.edit_description_entry.grid(row=3, column=1, padx=5, pady=5)
        self.edit_description_entry.insert(tk.END, selected_project.description)

            # Thêm widget nhập trạng thái dự án
        status_label = tk.Label(edit_window, text="Trạng thái:")
        status_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_status_entry = tk.Entry(edit_window)
        self.edit_status_entry.grid(row=4, column=1, padx=5, pady=5)
        self.edit_status_entry.insert(tk.END, selected_project.status)

        # Thêm nút cập nhật trạng thái dự án
        update_status_button = tk.Button(edit_window, text="Cập nhật trạng thái", command=lambda: self.update_project_status(selected_project), bg="#1E90FF", fg="white", width=15)
        update_status_button.grid(row=5, columnspan=2, padx=5, pady=5)

        save_button = tk.Button(edit_window, text="Lưu", command=lambda: self.save_edit_project(selected_project), bg="#4CAF50", fg="white")
        save_button.grid(row=4, columnspan=2, padx=5, pady=5)


    def save_edit_project(self, selected_project):
        name = self.edit_name_entry.get().strip()
        start_date_str = self.edit_start_date_entry.get().strip()
        end_date_str = self.edit_end_date_entry.get().strip()
        description = self.edit_description_entry.get("1.0", tk.END).strip()

        if not (name and start_date_str and end_date_str and description):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Định dạng ngày không hợp lệ!")
            return

        selected_project.name = name
        selected_project.start_date = start_date
        selected_project.end_date = end_date
        selected_project.description = description

        self.update_project_tree()
        self.save_project_data()
        self.update_activity_history(f"Sửa dự án: {name}")
        messagebox.showinfo("Thông báo", "Sửa dự án thành công!")

    def delete_project(self):
        selected_items = self.project_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án để xóa!")
            return

        confirmation = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa dự án này?")
        if not confirmation:
            return

        selected_item = selected_items[0]
        project_id = int(self.project_tree.item(selected_item, "text"))
        del self.projects[project_id - 1]

        self.update_project_tree()
        self.save_project_data()
        self.update_activity_history(f"Xóa dự án: {project_id}")
        messagebox.showinfo("Thông báo", "Xóa dự án thành công!")

    def show_project_details(self, project):
        project_info_window = tk.Toplevel(self)
        project_info_window.title("Thông tin dự án")

        name_label = tk.Label(project_info_window, text="Tên dự án:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_value = tk.Label(project_info_window, text=project.name)
        name_value.grid(row=0, column=1, padx=5, pady=5)

        start_date_label = tk.Label(project_info_window, text="Ngày bắt đầu:")
        start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        start_date_value = tk.Label(project_info_window, text=project.start_date.strftime("%Y-%m-%d"))
        start_date_value.grid(row=1, column=1, padx=5, pady=5)

        end_date_label = tk.Label(project_info_window, text="Ngày kết thúc:")
        end_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        end_date_value = tk.Label(project_info_window, text=project.end_date.strftime("%Y-%m-%d"))
        end_date_value.grid(row=2, column=1, padx=5, pady=5)

        description_label = tk.Label(project_info_window, text="Mô tả:")
        description_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        description_value = tk.Label(project_info_window, text=project.description)
        description_value.grid(row=3, column=1, padx=5, pady=5)

        status_label = tk.Label(project_info_window, text="Trạng thái:")
        status_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        status_value = tk.Label(project_info_window, text=project.status)
        status_value.grid(row=5, column=1, padx=5, pady=5)

        # Hiển thị danh sách nhân viên tham gia vào dự án
        employees_label = tk.Label(project_info_window, text="Nhân viên tham gia:")
        employees_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        employees_listbox = tk.Listbox(project_info_window, bg="#FFFFFF", selectbackground="#D5E8D4")
        employees_listbox.grid(row=4, column=1, padx=5, pady=5)

        for employee_id in project.assigned_employees:
            employee = self.get_employee_by_id(employee_id)
            if employee:
                employees_listbox.insert(tk.END, employee.name)



    def get_employee_by_id(self, employee_id):
        for employee in self.employees:
            if employee.employee_id == employee_id:
                return employee
        return None


    def search_project(self):
        keyword = self.search_entry_project.get().strip().lower()
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return

        found_projects = []
        for project in self.projects:
            if keyword == project.name.lower():
                found_projects.append(project)

        if not found_projects:
            messagebox.showinfo("Thông báo", "Không tìm thấy dự án phù hợp.")
            return

        # Mở cửa sổ mới để hiển thị thông tin chi tiết của dự án
        for found_project in found_projects:
            self.show_project_details(found_project)

    def sort_projects(self, option):
        if option == "Tên dự án":
            self.projects.sort(key=lambda x: x.name)
        elif option == "Ngày bắt đầu":
            self.projects.sort(key=lambda x: x.start_date)
        elif option == "Ngày kết thúc":
            self.projects.sort(key=lambda x: x.end_date)

        self.update_project_tree()

    def update_project_tree(self):
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        for project in self.projects:
            assigned_employees_str = ", ".join(project.assigned_employees)
            self.project_tree.insert("", tk.END, text=project.project_id, values=(project.name, project.start_date.strftime("%Y-%m-%d"), project.end_date.strftime("%Y-%m-%d"), project.description, project.status, assigned_employees_str))

    def assign_employee_to_project(self):
        # Kiểm tra xem có dự án nào được chọn không
        selected_items = self.project_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án để gán nhân viên!")
            return

        # Lấy thông tin về dự án được chọn
        selected_item = selected_items[0]
        project_id = int(self.project_tree.item(selected_item, "text"))
        selected_project = self.projects[project_id - 1]

        # Tạo cửa sổ mới để chọn nhân viên
        assign_window = tk.Toplevel(self)
        assign_window.title("Gán nhân viên vào dự án")

        # Hiển thị danh sách nhân viên
        select_employee_label = tk.Label(assign_window, text="Chọn nhân viên:", bg="#F0F0F0")
        select_employee_label.pack(padx=10, pady=5)

        select_employee_tree = ttk.Treeview(assign_window, columns=("Name", "Employee ID", "Department ID", "Salary ID"), show="headings")
        select_employee_tree.heading("Name", text="Tên nhân viên", anchor="center")
        select_employee_tree.heading("Employee ID", text="Mã NV", anchor="center")
        select_employee_tree.heading("Department ID", text="Mã Phòng", anchor="center")
        select_employee_tree.heading("Salary ID", text="Mã Lương", anchor="center")

        select_employee_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        for employee in self.employees:
            select_employee_tree.insert("", tk.END, text=employee.employee_id, values=(employee.name, employee.employee_id, employee.department_id, employee.salary_id))

        # Tạo nút để gán nhân viên
        assign_button = tk.Button(assign_window, text="Gán", command=lambda: self.save_assigned_employees(selected_project, select_employee_tree))
        assign_button.pack(pady=10)

    def save_assigned_employees(self, project, select_employee_tree):
        selected_items = select_employee_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một nhân viên để gán!")
            return

        for item in selected_items:
            employee_id = select_employee_tree.item(item, "text")
            project.assigned_employees.append(employee_id)

        self.update_project_tree()  # Cập nhật giao diện hiển thị dự án
        self.save_project_data()  # Lưu thông tin về việc gán nhân viên vào dự án

        messagebox.showinfo("Thông báo", "Đã gán nhân viên vào dự án thành công!")


    def update_project_status(self, selected_project):
        new_status = self.edit_status_entry.get().strip()
        selected_project.status = new_status
        self.save_project_data()
        messagebox.showinfo("Thông báo", "Cập nhật trạng thái dự án thành công!")
    def show_project_details_on_double_click(self, event):
        # Lấy vị trí của dự án được kích đúp
        item_id = self.project_tree.selection()[0]
        project_id = int(self.project_tree.item(item_id, "text"))
        
        # Lấy thông tin chi tiết của dự án
        selected_project = self.projects[project_id - 1]
        
        # Hiển thị thông tin chi tiết của dự án trong một cửa sổ mới
        self.show_project_details(selected_project)



    def save_project_data(self):
        with open("projects.json", "w") as file:
            json.dump([project.to_dict() for project in self.projects], file, indent=4, default=str)

    def load_project_data(self):
        try:
            with open("projects.json", "r") as file:
                data = json.load(file)
                self.projects = [Project.from_dict(project_data) for project_data in data]
        except FileNotFoundError:
            self.projects = []


        # Sau khi tải dữ liệu, cập nhật giao diện
        self.update_project_tree()
        
    def show_attendance_history(self, event):
        selected_item = self.attendance_tree.focus()
        if not selected_item:
            return

        employee_name = self.attendance_tree.item(selected_item, "values")[3]
        self.view_attendance_history(employee_name)


    def search_employee(self):
        search_text = self.search_entry.get()
        if not search_text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên!")
            return

        found_employee = None
        for employee in self.employees:
            if employee.employee_id == search_text:
                found_employee = employee
                break

        if found_employee:
            self.display_employee_details(found_employee)
        else:
            messagebox.showinfo("Thông báo", f"Không tìm thấy nhân viên có mã {search_text}")

    def display_employee_details(self, employee):
        details_window = tk.Toplevel(self)
        details_window.title("Chi tiết nhân viên")

        details_frame = tk.Frame(details_window, bg="#F0F0F0")
        details_frame.pack(padx=10, pady=10)

        labels = ["Họ và Tên:", "Chức vụ:", "Mã nhân viên:", "Mã phòng:", "Mã lương:", "Ngày sinh:", "Giới tính:", "Dân tộc:", "Số CMND/CCCD:", "Nơi cấp:"]
        employee_details = [employee.name, employee.position, employee.employee_id, employee.department_id, employee.salary_id, employee.dob.strftime("%d/%m/%Y"), employee.gender, employee.ethnicity, employee.id_number, employee.id_issued_place]

        for i, (label_text, detail) in enumerate(zip(labels, employee_details)):
            label = tk.Label(details_frame, text=label_text, bg="#F0F0F0")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            detail_label = tk.Label(details_frame, text=detail, bg="#FFFFFF")
            detail_label.grid(row=i, column=1, padx=5, pady=5, sticky="w")

        # Add a button to view attendance history
        view_attendance_button = tk.Button(details_frame, text="Xem lịch sử điểm danh", command=lambda: self.view_attendance_history(employee.name), bg="#1E90FF", fg="white")
        view_attendance_button.grid(row=len(labels), columnspan=2, pady=10)

    def view_attendance_history(self, employee_name):
        if employee_name in self.attendance:
            attendance_history = self.attendance[employee_name]
            if attendance_history:
                history_window = tk.Toplevel(self)
                history_window.title("Lịch sử điểm danh")

                history_frame = tk.Frame(history_window, bg="#F0F0F0")
                history_frame.pack(padx=10, pady=10)

                history_listbox = tk.Listbox(history_frame, bg="#FFFFFF", selectbackground="#D5E8D4")
                history_listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

                for idx, check_in_time in enumerate(attendance_history, start=1):
                    history_listbox.insert(tk.END, f"{idx}. {check_in_time}")

            else:
                messagebox.showinfo("Thông báo", f"{employee_name} chưa có lịch sử điểm danh!")
        else:
            messagebox.showinfo("Thông báo", f"{employee_name} không tồn tại trong lịch sử điểm danh!")



    def load_salary_data(self):
        try:
            self.salary_tree.delete(*self.salary_tree.get_children())
            with open("salary.json", "r") as f:
                salary_data = [json.loads(line) for line in f]
                # Sắp xếp danh sách nhân viên theo mã phòng trước khi hiển thị
                sorted_salary_data = sorted(salary_data, key=lambda x: x["department_id"])
                for data in sorted_salary_data:
                    self.salary_tree.insert("", "end", values=(
                        data["name"],
                        data["employee_id"],
                        data["department_id"],
                        data["salary_id"],
                        data["total_salary"],
                        data["calculation_time"].split(" ")[0]  # Lấy phần tháng từ thời gian tính lương
                    ))
        except FileNotFoundError:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu lương!")



    def calculate_salary(self):
        # Tạo cửa sổ mới để nhập mã nhân viên
        input_window = tk.Toplevel(self)
        input_window.title("Nhập mã nhân viên")

        label = tk.Label(input_window, text="Nhập mã nhân viên:", bg="#F0F0F0")
        label.grid(row=0, column=0, padx=10, pady=5)

        entry = tk.Entry(input_window)
        entry.grid(row=0, column=1, padx=10, pady=5)

        confirm_button = tk.Button(input_window, text="Xác nhận", command=lambda: self.process_salary(entry.get()), bg="#4CAF50", fg="white")
        confirm_button.grid(row=1, columnspan=2, padx=10, pady=5)

    def process_salary(self, employee_id):
        # Tìm nhân viên với mã nhân viên được nhập
        selected_employee = None
        for employee in self.employees:
            if employee.employee_id == employee_id:
                selected_employee = employee
                break

        if selected_employee:
            # Nhập số tiền thưởng
            bonus = askfloat("Nhập số tiền thưởng", "Nhập số tiền thưởng:")
            if bonus is None:
                return

            # Nhập số tiền phạt
            penalty = askfloat("Nhập số tiền phạt", "Nhập số tiền phạt:")
            if penalty is None:
                return

            # Tính tổng lương
            total_salary = float(selected_employee.salary_id) + bonus - penalty

            # Lưu dữ liệu lương vào tệp JSON
            salary_data = {
                "name": selected_employee.name,
                "employee_id": selected_employee.employee_id,
                "department_id": selected_employee.department_id,
                "salary_id": selected_employee.salary_id,
                "total_salary": total_salary,
                "calculation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open("salary.json", "a") as f:
                json.dump(salary_data, f)
                f.write("\n")

            # Hiển thị kết quả tính toán
            messagebox.showinfo("Kết quả", f"Tổng lương của nhân viên {selected_employee.name} là: {total_salary}")


        else:
            messagebox.showwarning("Cảnh báo", f"Không tìm thấy nhân viên với mã {employee_id}")
        
        self.update_activity_history(f"Tính lương cho nhân viên: {selected_employee.name}")

    def show_employee_details(self, event):
        selected_item = self.employee_tree.selection()
        if len(selected_item) == 0:
            return
        
        employee_id = self.employee_tree.item(selected_item)['text']
        selected_employee = self.employees[int(employee_id) - 1]

        details_window = tk.Toplevel(self)
        details_window.title("Chi tiết nhân viên")

        details_frame = tk.Frame(details_window, bg="#F0F0F0")
        details_frame.pack(padx=10, pady=10)

        labels = ["Họ và Tên:", "Chức vụ:", "Mã nhân viên:", "Mã phòng:", "Mã lương:", "Ngày sinh:", "Giới tính:", "Dân tộc:", "Số CMND/CCCD:", "Nơi cấp:"]
        employee_details = [selected_employee.name, selected_employee.position, selected_employee.employee_id, selected_employee.department_id, selected_employee.salary_id, selected_employee.dob.strftime("%d/%m/%Y"), selected_employee.gender, selected_employee.ethnicity, selected_employee.id_number, selected_employee.id_issued_place]

        for i, (label_text, detail) in enumerate(zip(labels, employee_details)):
            label = tk.Label(details_frame, text=label_text, bg="#F0F0F0")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            detail_label = tk.Label(details_frame, text=detail, bg="#FFFFFF")
            detail_label.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                # Thêm nút "Xem lịch sử điểm danh"
            view_attendance_button = tk.Button(details_frame, text="Xem lịch sử điểm danh", command=lambda: self.view_attendance_history(selected_employee.name), bg="#1E90FF", fg="white")
            view_attendance_button.grid(row=len(labels), columnspan=2, pady=10)
    def sort_employees(self, criteria):
        if criteria == "Tên":
            self.employees.sort(key=lambda x: x.name)
        elif criteria == "Mã NV":
            self.employees.sort(key=lambda x: x.employee_id)
        elif criteria == "Mã phòng":
            self.employees.sort(key=lambda x: x.department_id)
        elif criteria == "Mã lương":
            self.employees.sort(key=lambda x: x.salary_id)
        elif criteria == "Ngày sinh":
            self.employees.sort(key=lambda x: x.dob)
        self.update_employee_tree()
                
    def mark_attendance(self):
        selected_items = self.select_employee_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một nhân viên để chấm công!")
            return

        current_date = datetime.now().date()
        for item in selected_items:
            values = self.select_employee_tree.item(item, "values")
            employee_name = values[0]
            employee_id = values[1]
            department_id = values[2]
            salary_id = values[3]

            if employee_name in self.attendance:
                if self.attendance[employee_name]:
                    last_check_in_date = self.attendance[employee_name][-1].date()
                    if last_check_in_date == current_date:
                        messagebox.showwarning("Cảnh báo", f"{employee_name} đã được chấm công vào ngày hôm nay!")
                        continue
            else:
                self.attendance[employee_name] = []

            self.attendance[employee_name].append(datetime.now())
            self.update_attendance_tree()
            self.save_attendance_data()
            self.update_activity_history("Chấm công cho các nhân viên")

    def update_attendance_tree(self):
        self.attendance_tree.delete(*self.attendance_tree.get_children())
        for employee, check_in_times in self.attendance.items():
            employee_info = None
            for emp in self.employees:
                if emp.name == employee:
                    employee_info = emp
                    break
            if employee_info:
                employee_id = employee_info.employee_id
                department_id = employee_info.department_id
                salary_id = employee_info.salary_id
                for idx, check_in_time in enumerate(check_in_times, start=1):
                    self.attendance_tree.insert("", "end", values=(employee_id, department_id, salary_id, employee, check_in_time))
            else:
                for idx, check_in_time in enumerate(check_in_times, start=1):
                    self.attendance_tree.insert("", "end", text=str(idx), values=("N/A", "N/A", "N/A", employee, check_in_time))


    def save_attendance_data(self):
        with open("attendance.json", "w") as f:
            # Chuyển đổi dữ liệu thời gian chấm công sang định dạng chuỗi
            converted_attendance = {employee: [str(time) for time in times] for employee, times in self.attendance.items()}
            json.dump(converted_attendance, f)

    # Phương thức load_attendance_data sẽ chuyển đổi dữ liệu thời gian từ chuỗi sang đối tượng datetime sau khi tải từ tệp JSON
    def load_attendance_data(self):
        try:
            with open("attendance.json", "r") as f:
                converted_attendance = json.load(f)
                # Chuyển đổi dữ liệu thời gian chấm công từ chuỗi sang đối tượng datetime
                self.attendance = {employee: [datetime.fromisoformat(time) for time in times] for employee, times in converted_attendance.items()}
                self.update_attendance_tree()  # Update attendance tree when loading data
        except FileNotFoundError:
            self.attendance = {}

    def create_attendance_list(self):
        for employee in self.employees:
            self.select_employee_tree.insert("", "end", values=(employee.name, employee.employee_id, employee.department_id, employee.salary_id))



    def add_employee(self):
        employee_window = tk.Toplevel(self)
        employee_window.title("Thêm nhân viên")

        labels = ["Họ Tên:", "Chức vụ:", "Mã nhân viên:", "Mã phòng:", "Mã lương:", "Ngày sinh (dd/mm/yyyy):", "Giới tính:", "Dân tộc:", "Số CMND/CCCD:", "Nơi cấp:"]
        entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(employee_window, text=label_text, bg="#F0F0F0")
            label.grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(employee_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        add_button = tk.Button(employee_window, text="Thêm", command=lambda: self.save_employee(*[entry.get() for entry in entries]), bg="#4CAF50", fg="white")
        add_button.grid(row=len(labels), columnspan=2, padx=10, pady=5)

    def save_employee(self, name, position, employee_id, department_id, salary_id, dob, gender, ethnicity, id_number, id_issued_place):
        try:
            dob = datetime.strptime(dob, "%d/%m/%Y")
            employee = Employee(employee_id, department_id, salary_id, name, dob, gender, ethnicity, id_number, id_issued_place, position)
            self.employees.append(employee)
            self.update_employee_tree()
            self.update_activity_history(f"Thêm nhân viên: {name}")
            self.save_data()
            self.create_attendance_list()  # Update the attendance list
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng cho các trường!")
            return

    def update_employee_tree(self):
        self.employee_tree.delete(*self.employee_tree.get_children())
        for idx, employee in enumerate(self.employees, start=1):
            dob_date = employee.dob.date()
            self.employee_tree.insert("", "end", text=str(idx), values=(employee.name, employee.position, employee.employee_id, employee.department_id, employee.salary_id, dob_date, employee.gender, employee.ethnicity, employee.id_number, employee.id_issued_place))

        self.employee_tree.heading("#0", text="STT", anchor=tk.CENTER)
        self.employee_tree.column("#0", anchor=tk.CENTER, width=70)

        columns = ("Name", "Position", "Employee ID", "Department ID", "Salary ID", "DOB", "Gender", "Ethnicity", "ID Number", "ID Issued Place")
        for column in columns:
            self.employee_tree.heading(column, anchor=tk.CENTER)
            self.employee_tree.column(column, anchor=tk.CENTER, width=120)
        
        self.employee_tree.update()
        self.employee_tree.yview_moveto(0)
        self.employee_tree.xview_moveto(0)

    def edit_employee(self):
        selected_item = self.employee_tree.selection()
        if len(selected_item) == 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để sửa!")
            return
        employee_id = self.employee_tree.item(selected_item)['text']
        selected_employee = self.employees[int(employee_id) - 1]  # Trích xuất mã nhân viên để sửa
        employee_window = tk.Toplevel(self)
        employee_window.title("Sửa nhân viên")

        labels = ["Họ Tên:", "Chức vụ:", "Mã nhân viên:", "Mã phòng:", "Mã lương:", "Ngày sinh (dd/mm/yyyy):", "Giới tính:", "Dân tộc:", "Số CMND/CCCD:", "Nơi cấp:"]
        entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(employee_window, text=label_text, bg="#F0F0F0")
            label.grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(employee_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        for entry, value in zip(entries, [selected_employee.name, selected_employee.position, selected_employee.employee_id, selected_employee.department_id, selected_employee.salary_id, selected_employee.dob.strftime("%d/%m/%Y"), selected_employee.gender, selected_employee.ethnicity, selected_employee.id_number, selected_employee.id_issued_place]):
            entry.insert(0, value)

        update_button = tk.Button(employee_window, text="Cập nhật", command=lambda: self.update_employee(employee_id, *[entry.get() for entry in entries]), bg="#4CAF50", fg="white")
        update_button.grid(row=len(labels), columnspan=2, padx=10, pady=5)

    def delete_employee(self):
        selected_item = self.employee_tree.selection()
        if len(selected_item) == 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để xóa!")
            return
        employee_id = self.employee_tree.item(selected_item)['text']
        confirmed = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa nhân viên này?")
        if confirmed:
            deleted_employee = self.employees.pop(int(employee_id) - 1)
            self.update_employee_tree()
            self.update_activity_history(f"Xóa nhân viên: {deleted_employee.name}")
            self.save_data()
            self.create_attendance_list()  # Update the attendance list

    def update_employee(self, selected_item, name, position, employee_id, department_id, salary_id, dob, gender, ethnicity, id_number, id_issued_place):
        try:
            selected_employee = self.employees[int(selected_item) - 1]  # Chuyển đổi selected_item sang kiểu int
            dob = datetime.strptime(dob, "%d/%m/%Y")
            selected_employee.name = name
            selected_employee.position = position
            selected_employee.employee_id = employee_id
            selected_employee.department_id = department_id
            selected_employee.salary_id = salary_id
            selected_employee.dob = dob
            selected_employee.gender = gender
            selected_employee.ethnicity = ethnicity
            selected_employee.id_number = id_number
            selected_employee.id_issued_place = id_issued_place
            self.update_employee_tree()
            self.update_activity_history(f"Sửa thông tin nhân viên: {name}")
            self.save_data()
            self.create_attendance_list()  # Update the attendance list
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng cho các trường!")
            return

    def update_activity_history(self, activity):
        current_time = datetime.now()
        activity_with_time = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} - {activity}"
        if activity_with_time:  # Thêm điều kiện kiểm tra giá trị
            self.activity_history.append(activity_with_time)
            self.history_listbox.insert(tk.END, activity_with_time)

    def delete_attendance(self):
        selected_items = self.attendance_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một nhân viên để xóa điểm danh!")
            return

        for item in selected_items:
            employee_name = self.attendance_tree.item(item, "values")[3]  # Lấy tên nhân viên từ mục đã chọn
            if employee_name in self.attendance:
                del self.attendance[employee_name]

        self.update_attendance_tree()
        self.save_attendance_data()
        messagebox.showinfo("Thông báo", "Đã xóa điểm danh cho các nhân viên đã chọn.")

    def save_data(self):
        def default(obj):
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            raise TypeError("Object of type {} is not JSON serializable".format(obj.__class__.__name__))
        
        data = {
            "employees": [employee.__dict__ for employee in self.employees],
            "attendance": {employee: [str(time) for time in times] for employee, times in self.attendance.items()},
            "activity_history": self.activity_history
        }
        with open("employees.json", "w") as f:
            json.dump(data, f, default=default)

    def load_data(self):
        try:
            with open("employees.json", "r") as f:
                data = json.load(f)
                self.employees = [Employee(**employee_data) for employee_data in data["employees"]]
                for employee in self.employees:
                    employee.dob = datetime.strptime(employee.dob, "%Y-%m-%d %H:%M:%S")
                self.attendance = {employee: [datetime.fromisoformat(time) for time in times] for employee, times in data.get("attendance", {}).items()}
                self.activity_history = data.get("activity_history", [])
                self.attendance = data.get("attendance", {})
                self.update_employee_tree()
                self.update_attendance_tree()
                for activity in self.activity_history:
                    self.history_listbox.insert(tk.END, activity)
        except FileNotFoundError:
            self.employees = []

if __name__ == "__main__":
    app = EmployeeManagementApp()
    app.mainloop()
