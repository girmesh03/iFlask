import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image
import phonenumbers
from tkinter import messagebox, filedialog
from typing import Callable
import webbrowser
import xlsxwriter
import subprocess
import psutil
import os

import customtkinter as ctk
from settings.configuration import Configuration


class View(ctk.CTk):
    def __init__(self, controller) -> None:
        super().__init__()

        self.controller = controller
        self.title("iFlask")
        self.geometry("800x500")
        self.icon_path = "./images/icon.ico"
        self.config = Configuration("settings/config.ini")
        self.theme = self.config.get_value("Settings", "theme")

        self.selected_option = tk.StringVar()
        self.selected_option.set("Admin")

        self.create_user_interface()
        self.apply_theme()

    def create_user_interface(self):
        """Create the entire user interface"""
        self.create_menu_bar()
        self.create_main_frame()
        self.create_header_frame()
        self.create_left_frame()
        self.create_treeview_frame()
        self.create_search_entry()
        self.create_search_option_menu()
        self.create_admin_option_menu()
        self.create_name_entries()
        self.create_email_entry()
        self.create_phone_number_widgets()
        self.create_gender_combobox()
        self.create_membership_combobox()
        self.create_buttons()
        self.create_treeview()

    def create_menu_bar(self):
        """Create menu bar and menu items"""
        self.menu_bar = tk.Menu(self)
        self.configure(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit)

        self.esp32_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Esp32", menu=self.esp32_menu)
        self.esp32_menu.add_command(
            label="Connect", command=self.connect_to_esp32)
        self.esp32_menu.add_command(
            label="Disconnect", command=self.disconnect_from_esp32)

        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)

        self.change_theme_submenu = tk.Menu(self.tools_menu, tearoff=0)
        self.tools_menu.add_cascade(
            label="Change Theme", menu=self.change_theme_submenu)
        self.change_theme_submenu.add_radiobutton(
            label="Light", command=lambda: self.change_theme("light"))
        self.change_theme_submenu.add_radiobutton(
            label="Dark", command=lambda: self.change_theme("dark"))

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(
            label="Documentation", command=self.show_documentation)

    def create_main_frame(self):
        """Create the main frame"""
        self.main_frame = ctk.CTkFrame(master=self)
        self.main_frame.pack(fill='both', expand=True)

    def create_header_frame(self):
        """Create the header frame with logo and logo text"""
        self.header_frame = ctk.CTkFrame(
            master=self.main_frame, height=50, border_width=1)
        self.header_frame.pack(fill='x', padx=5, pady=5)

        # Add logo
        png_image_logo = ctk.CTkImage(light_image=Image.open(
            "images/fingerprint.png"), size=(40, 40))
        logo_label = ctk.CTkLabel(
            master=self.header_frame, image=png_image_logo, text='')
        logo_label.grid(row=0, column=0, sticky='e', padx=(10, 0))

        # Add logo text
        png_image_text = ctk.CTkImage(light_image=Image.open(
            "./images/iFlask.png"), size=(128, 40))
        logo_text_label = ctk.CTkLabel(
            master=self.header_frame, image=png_image_text, text='')
        logo_text_label.grid(row=0, column=1, sticky='w')

        # Configure header frame
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=10)
        self.header_frame.grid_columnconfigure(2, weight=10)

    def create_left_frame(self):
        """Create the left frame containing various widgets"""
        self.left_frame = ctk.CTkScrollableFrame(
            master=self.main_frame, border_width=1, width=270)
        self.left_frame.pack(fill='y', side='left', padx=5, pady=5)

        self.create_admin_option_menu()
        ttk.Separator(self.left_frame).grid(
            row=1, column=0, padx=10, pady=15, sticky='ew')
        self.create_name_entries()
        self.create_email_entry()
        self.create_phone_number_widgets()
        self.create_gender_combobox()
        self.create_membership_combobox()
        ttk.Separator(self.left_frame).grid(
            row=8, column=0, padx=10, pady=15, sticky='ew')
        self.create_buttons()

    def create_search_entry(self):
        """Create the search entry"""
        self.search_entry = ctk.CTkEntry(
            master=self.header_frame,
            placeholder_text='First Name or Last Name',
            width=200)
        self.search_entry.grid(
            row=0, column=1, padx=10, pady=10, sticky='e')
        self.search_entry.bind(
            '<Return>', lambda args: self.search_user())

    def create_search_option_menu(self):
        """Create the search option menu"""
        self.search_option_menu = ctk.CTkOptionMenu(
            master=self.header_frame,
            values=["Search User", "Refresh"],
            command=lambda args: self.search_user())
        self.search_option_menu.grid(
            row=0, column=2, padx=10, pady=10, sticky='w')

    def create_admin_option_menu(self):
        """Create the admin option menu"""
        self.admin_option_menu = ctk.CTkOptionMenu(
            master=self.left_frame,
            values=["Login", "Logout", "Add Admin User"],
            variable=self.selected_option, anchor='center',
            command=self.on_admin_option_changed)
        self.admin_option_menu.grid(row=0, column=0, padx=(
            35, 35), pady=(25, 5), sticky='ew')

    def on_admin_option_changed(self, *args):
        selected_option = self.selected_option.get()
        # print(f"view Selected option: {selected_option}")
        self.controller.admin(selected_option)

    def create_name_entries(self):
        """Create first name and last name entries"""
        self.first_name_entry = ctk.CTkEntry(
            master=self.left_frame,
            placeholder_text="First Name"
        )
        self.first_name_entry.grid(
            row=2, column=0, padx=(35, 35), pady=5, sticky="ew")

        self.last_name_entry = ctk.CTkEntry(
            master=self.left_frame, placeholder_text="Last Name")
        self.last_name_entry.grid(
            row=3, column=0, padx=(35, 35), pady=5, sticky="ew")

    def create_email_entry(self):
        """Create email entry"""
        self.email_entry = ctk.CTkEntry(
            master=self.left_frame, placeholder_text="Email")
        self.email_entry.grid(row=4, column=0, padx=(
            35, 35), pady=5, sticky="ew")

    def create_phone_number_widgets(self):
        """Create country code combobox and phone number entry"""
        self.country_codes = [
            f"+{codes}"
            for codes in phonenumbers.COUNTRY_CODE_TO_REGION_CODE.keys()]

        self.phone_number_frame = ctk.CTkFrame(
            master=self.left_frame)
        self.phone_number_frame.grid(
            row=5, column=0, padx=(35, 35), pady=5)

        self.country_code_combobox = ctk.CTkComboBox(
            self.phone_number_frame,
            values=self.country_codes, width=70)
        self.country_code_combobox.grid(
            row=5, column=0, sticky='w')
        self.country_code_combobox.set(
            self.country_codes[82])

        self.phone_number_entry = ctk.CTkEntry(
            master=self.phone_number_frame,
            placeholder_text="Phone Number")
        self.phone_number_entry.grid(
            row=5, column=1, sticky='ew')

    def create_gender_combobox(self):
        """Create gender combobox"""
        self.gender_option_menu = ctk.CTkOptionMenu(
            master=self.left_frame, values=["Male", "Female"])
        self.gender_option_menu.grid(
            row=6, column=0, padx=(35, 35), pady=5, sticky='ew')
        self.gender_option_menu.set('Select Gender')

    def create_membership_combobox(self):
        """Create membership combobox"""
        self.member_option_menu = ctk.CTkOptionMenu(
            master=self.left_frame, values=["Member", "Not Member"])
        self.member_option_menu.grid(
            row=7, column=0, padx=(35, 35), pady=5, sticky='ew')
        self.member_option_menu.set('Membership Type')

    def create_buttons(self):
        """Create buttons"""
        self.enroll_button = ctk.CTkButton(
            master=self.left_frame, text="Enroll New User")
        self.enroll_button.grid(row=9, column=0, padx=(
            35, 35), pady=(10, 5), sticky='ew')

        self.clear_button = ctk.CTkButton(
            master=self.left_frame,
            text="Clear Fields",
            command=self.clear_entry_fields)

        self.clear_button.grid(
            row=10, column=0, padx=(35, 35), pady=5, sticky='ew')

        self.delete_button = ctk.CTkButton(
            master=self.left_frame, text="Delete Selected User")
        self.delete_button.grid(
            row=12, column=0, padx=(35, 35), pady=5, sticky='ew')

        self.update_button = ctk.CTkButton(
            master=self.left_frame, text="Update Selected User")
        self.update_button.grid(
            row=13, column=0, padx=(35, 35), pady=5, sticky='ew')

        self.generate_report_button = ctk.CTkButton(
            master=self.left_frame, text="Generate Report")
        self.generate_report_button.grid(
            row=14, column=0, padx=(35, 35), pady=5, sticky='ew')

    def create_treeview_frame(self):
        """Create the treeview frame with vertical and
        horizontal scrollbars"""
        self.treeview_frame = ctk.CTkFrame(
            master=self.main_frame, border_width=1)
        self.treeview_frame.pack(
            fill='both', side='left', padx=5, pady=5, expand=True)

        self.vertical_scrollbar = ctk.CTkScrollbar(
            self.treeview_frame, orientation='vertical')
        self.vertical_scrollbar.pack(side='right', fill='y')

        self.horizontal_scrollbar = ctk.CTkScrollbar(
            self.treeview_frame, orientation='horizontal')
        self.horizontal_scrollbar.pack(side='bottom', fill='x')

    def create_treeview(self):
        """Create the treeview with specified columns"""
        self.column_names = [
            'User ID', 'First Name', 'Last Name', 'Email',
            'Country Code', 'Phone Number', 'Gender',
            'Last Check In', 'Membership Type', 'Next Payment',
            'Remaining Days'
        ]

        self.treeview = ttk.Treeview(
            self.treeview_frame, columns=self.column_names, show='headings',
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set, height=20
        )
        self.treeview.pack(fill='both', expand=True, padx=10, pady=10)

        self.vertical_scrollbar.configure(command=self.treeview.yview)
        self.horizontal_scrollbar.configure(command=self.treeview.xview)

        # Configure treeview column names and widths
        column_widths = [10, 50, 50, 150, 60, 80, 20, 50, 90, 70, 90]
        for i, column in enumerate(self.column_names):
            self.treeview.heading(column, text=column)
            self.treeview.column(
                column, width=column_widths[i], anchor='center')

        # Bind Treeview selection event to on_select method
        self.treeview.bind('<<TreeviewSelect>>', lambda args: self.on_select())

    def generate_report(self, all_users):
        """Generate a report based on the provided user data."""
        if not all_users:
            messagebox.showerror(
                title="Error", message="You Have Empty Database")
            return

        # Get the file path from the user using file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=(("xlsx files", "*.xlsx"),
                       ("all files", "*.*"))
        )

        try:
            # Create workbook
            workbook = xlsxwriter.Workbook(file_path)

            # Create worksheet
            worksheet = workbook.add_worksheet()

            # Create header format
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#1E90FF',
                'border': 1
            })

            # Create data format
            data_format = workbook.add_format({'border': 1})

            # Header row
            headers = ['User ID', 'First Name', 'Last Name',
                       'Email', 'Country Code', 'Phone Number',
                       'Gender', 'Last Check In', 'Membership Type',
                       'Next Payment', 'Start Date', 'Updated Date',
                       'Remaining Days'
                       ]

            # Write header
            worksheet.write_row('A1', headers, header_format)

            # Set column widths manually
            column_widths = [10, 15, 15, 35, 12,
                             15, 10, 15, 15, 15, 12, 12, 15]
            for col, width in enumerate(column_widths):
                worksheet.set_column(col, col, width)

            # Write data
            for index, user in enumerate(all_users, start=1):
                worksheet.write_row(index, 0, [
                    user.id,
                    user.first_name,
                    user.last_name,
                    user.email,
                    '+' + str(user.country_code),
                    user.phone_number,
                    user.gender,
                    str(user.last_check_in).split()[
                        0] if user.last_check_in else '',
                    user.membership_type,
                    str(user.next_payment).split()[
                        0] if user.next_payment else '',
                    str(user.created_at).split()[0] if user.created_at else '',
                    str(user.updated_at).split()[0] if user.updated_at else '',
                    str(user.remaining_days).split()[
                        0] if user.remaining_days else '',
                ], data_format)

            workbook.close()

            # Display success message
            messagebox.showinfo("Message", "Report Generated")
        except xlsxwriter.exceptions.FileCreateError:
            # messagebox.showerror("Error", "Please enter a valid file path")
            pass

    def save_file(self):
        """Save the report file."""
        all_users = self.controller.get_all_users()
        self.generate_report(all_users)

    def exit(self):
        """Exit the application."""
        result = messagebox.askquestion(
            "Exit", "Are you sure you want to exit?")
        if result == "yes":
            self.destroy()

    def change_theme(self, theme):
        """Change the theme of the application."""
        self.theme = theme
        self.apply_theme()

    def apply_theme(self):
        """Apply the selected theme to all widgets."""
        if self.theme == 'light':
            ctk.set_appearance_mode('light')
        elif self.theme == 'dark':
            ctk.set_appearance_mode('dark')
        else:
            ctk.set_default_color_theme(self.theme)

        self.config.set_value('Settings', 'theme', self.theme)
        self.config.save_changes()

    def show_about(self):
        """Show the 'About' page in the browser."""
        webbrowser.open(
            "https://girmesh03.github.io/iFlask-Landing-Page/")

    def show_documentation(self):
        """Show the documentation in the browser."""
        webbrowser.open(
            "https://github.com/girmesh03/iFlask/blob/main/README.md")

    def admin_login_window(self, action):
        """Create the admin login window"""
        self.top_level = tk.Toplevel(master=self)
        self.top_level.title("Admin")
        self.top_level.geometry('400x400+500+200')
        self.top_level.resizable(False, False)

        icon_path = "images/icon.ico"
        self.top_level.iconbitmap(icon_path)

        self.top_level_frame = ctk.CTkFrame(master=self.top_level)
        self.top_level_frame.pack(fill='both', expand=True)

        # Admin login label
        self.admin_login_label = ctk.CTkLabel(
            master=self.top_level_frame,
            font=("Helvetica", 20, 'bold'))
        self.admin_login_label.pack(padx=10, pady=50)

        if action == 'Login':
            self.admin_login_label.configure(text="Login")

            # Admin email
            self.admin_email_entry = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="Email", width=250)
            self.admin_email_entry.pack(padx=10, pady=10)

            # Password entry
            self.admin_password_entry = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="Password", width=250, show="*")
            self.admin_password_entry.pack(padx=10, pady=10)

            self.admin_login_button = ctk.CTkButton(
                master=self.top_level_frame,
                text="Login", width=250,
                command=lambda: self.admin_login(action))
            self.admin_login_button.pack(padx=10, pady=5)

        elif action == 'Add Admin User':
            self.admin_login_label.configure(text="Add Admin User")
            self.admin_login_label.pack_configure(pady=20)

            # Admin first name
            self.first_name = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="First Name", width=250)
            self.first_name.pack(padx=10, pady=10)

            # Admin last name
            self.last_name = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="Last Name", width=250)
            self.last_name.pack(padx=10, pady=10)

            # Admin email
            self.admin_email_entry = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="Email", width=250)
            self.admin_email_entry.pack(padx=10, pady=10)

            # Password entry
            self.admin_password_entry = ctk.CTkEntry(
                master=self.top_level_frame,
                placeholder_text="Password", width=250, show="*")
            self.admin_password_entry.pack(padx=10, pady=10)

            self.admin_signup_button = ctk.CTkButton(
                master=self.top_level_frame,
                text="Add Admin", width=250,
                command=lambda: self.admin_login(action))
            self.admin_signup_button.pack(padx=10, pady=5)

    def admin_login(self, action):
        """Perform admin login or signup"""
        admin_dict = {}
        if action == 'Add Admin User':
            admin_dict['first_name'] = self.first_name.get()
            admin_dict['last_name'] = self.last_name.get()

        admin_dict['email'] = self.admin_email_entry.get()
        admin_dict['password'] = self.admin_password_entry.get()

        is_valid = self.controller.validate_admin_inputs(action, **admin_dict)
        if is_valid is not None:
            messagebox.showerror("Error", is_valid, parent=self.top_level)
            return

        if action == 'Login':
            is_user_exists = self.controller.admin_user(action, **admin_dict)
            if is_user_exists:
                self.top_level.destroy()
            else:
                messagebox.showerror(
                    "Error", "Please Sign Up first", parent=self.top_level)
                return

        elif action == 'Add Admin User':
            self.controller.admin_user(action, **admin_dict)
            self.top_level.destroy()

    def clear_entry_fields(self):
        """Clear entry fields and set default values"""
        self.first_name_entry.delete(0, 'end')
        self.last_name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.country_code_combobox.set('')
        self.phone_number_entry.delete(0, 'end')
        self.gender_option_menu.set('')
        self.member_option_menu.set('')
        self.first_name_entry.configure(placeholder_text="First Name")
        self.last_name_entry.configure(placeholder_text="Last Name")
        self.email_entry.configure(placeholder_text="Email")
        self.country_code_combobox.set(self.country_codes[82])
        self.phone_number_entry.configure(placeholder_text="Phone Number")
        self.gender_option_menu.set('Select Gender')
        self.member_option_menu.set('Membership Type')

    def search_user(self):
        """Search for users based on the selected option"""
        search_query = self.search_entry.get().strip().title()
        option = self.search_option_menu.get()
        all_users = self.controller.get_all_users()
        filtered_users = []

        if option == 'Search User':
            for user in all_users:
                if user.first_name == search_query\
                        or user.last_name == search_query:
                    filtered_users.append(user)

            if not filtered_users:
                self.display_message("No matching users found")
                return

            self.treeview.delete(*self.treeview.get_children())
            for user in filtered_users:
                self.add_user_to_treeview(user, update=False)
            self.configure_treeview()

        elif option == 'Refresh':
            self.treeview.delete(*self.treeview.get_children())
            self.refresh_treeview()

        self.search_option_menu.set("Search User")
        self.search_entry.delete(0, 'end')
        self.search_entry.configure(placeholder_text='First Name or Last Name')

    def on_select(self):
        """Populate entry fields with the selected user's information"""
        selected_row = self.treeview.focus()
        values = self.treeview.item(selected_row)['values']
        self.clear_entry_fields()

        if selected_row == '':
            return
        self.first_name_entry.insert(0, values[1])
        self.last_name_entry.insert(0, values[2])
        self.email_entry.insert(0, values[3])
        self.country_code_combobox.set('+' + str(values[4]))
        self.phone_number_entry.insert(0, values[5])
        self.gender_option_menu.set(values[6])
        self.member_option_menu.set(values[8])

    def get_user_entry_fields(self):
        """Get user information from entry fields"""
        user_info = {}
        user_info['first_name'] = self.first_name_entry.get().lower().title()
        user_info['last_name'] = self.last_name_entry.get().lower().title()
        user_info['email'] = self.email_entry.get()
        user_info['country_code'] = self.country_code_combobox.get()
        user_info['phone_number'] = self.phone_number_entry.get()
        user_info['gender'] = self.gender_option_menu.get()
        user_info['membership_type'] = self.member_option_menu.get()
        user_info['remaining_days'] = 30
        return user_info

    def add_user_to_treeview(self, new_user, update=False):
        """Add a user to the treeview"""
        treeview_column = {
            'User ID': new_user.id,
            'First Name': new_user.first_name,
            'Last Name': new_user.last_name,
            'Email': new_user.email,
            'Country Code': '+' + str(new_user.country_code),
            'Phone Number': new_user.phone_number,
            'Gender': new_user.gender,
            'Last Check In': str(new_user.last_check_in).split()[0],
            'Membership Type': new_user.membership_type,
            'Next Payment': str(new_user.next_payment).split()[0],
            'Remaining Days': new_user.remaining_days
        }

        if not update:
            self.treeview.insert(
                '', 'end', values=list(treeview_column.values()))
        else:
            self.treeview.item(self.treeview.focus(),
                               values=list(treeview_column.values()))

    def delete_user_from_treeview(self):
        """Delete the selected user from the treeview"""
        selected_row = self.treeview.focus()
        self.treeview.delete(selected_row)
        for index, row in enumerate(self.treeview.get_children()):
            if index % 2 == 0:
                self.treeview.item(row, tags=('even',))
            else:
                self.treeview.item(row, tags=('odd',))

    def get_selected_user(self):
        """Get the selected user from the treeview"""
        selected_row = self.treeview.focus()
        if selected_row == '':
            return None
        values = self.treeview.item(selected_row)['values']
        user_id = values[0]
        user = self.controller.get_user_by_id(user_id)
        return user

    def configure_treeview(self):
        """Configure the treeview with alternating row colors"""
        self.treeview.tag_configure('odd', background='#E8E8E8')
        self.treeview.tag_configure('even', background='lightblue')
        for index, row in enumerate(self.treeview.get_children()):
            if index % 2 == 0:
                self.treeview.item(row, tags=('even',))
            else:
                self.treeview.item(row, tags=('odd',))

    def display_message(self, message, user_id=None):
        """Display a message in a messagebox"""
        if user_id:
            messagebox.showinfo("Message", f"{message} {user_id}", parent=self)
        else:
            messagebox.showerror("Error", message, parent=self)

    def refresh_treeview(self):
        """Refresh the treeview with all users"""
        self.treeview.delete(*self.treeview.get_children())
        users = self.controller.get_all_users()
        if not users:
            return
        for user in users:
            self.add_user_to_treeview(user)
        self.configure_treeview()

    def bind_enroll_user_task(
            self, callback: Callable[[tk.Event], None]) -> None:
        """Bind the enroll_button to a callback function."""
        self.enroll_button.bind("<Button-1>", callback)

    def bind_delete_user_task(
            self, callback: Callable[[tk.Event], None]) -> None:
        """Bind the delete_button to a callback function."""
        self.delete_button.bind("<Button-1>", callback)

    def bind_update_user_task(
            self, callback: Callable[[tk.Event], None]) -> None:
        """Bind the update_button to a callback function."""
        self.update_button.bind("<Button-1>", callback)

    def bind_generate_report_task(
            self, callback: Callable[[tk.Event], None]) -> None:
        """Bind the generate_report_button to a callback function."""
        self.generate_report_button.bind("<Button-1>", callback)

    def update_user_treeview(self, user_id):
        """Update the user information in the treeview."""
        user = self.controller.get_user_by_id(user_id)
        self.add_user_to_treeview(user, update=True)

    def on_admin_option_changed(self, *args):
        """Handle changes in the admin option menu."""
        selected_option = self.selected_option.get()
        self.controller.admin(selected_option)

    def stop_flask_api(self):
        """Stop the Flask API running in the background."""
        flask_api_pid = self.find_process_by_name('pythonw.exe')
        if flask_api_pid:
            try:
                parent = psutil.Process(flask_api_pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except psutil.NoSuchProcess:
                pass

    def find_process_by_name(self, process_name):
        """Find a process by its name and return its PID."""
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name in proc.info['name']:
                return proc.info['pid']
        return None

    def connect_to_esp32(self):
        """Connect to the ESP32."""
        with open('output.log', 'w') as log_file:
            subprocess.Popen(['pythonw', 'api.py'],
                             stdout=log_file,
                             stderr=subprocess.STDOUT)

    def disconnect_from_esp32(self):
        """Disconnect from the ESP32 and stop the API."""
        self.stop_flask_api()
