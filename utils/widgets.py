import tkinter as tk
from functools import partial
from tkinter import filedialog, StringVar, ttk
from typing import Optional


class LoggingWidget:
    def __init__(self, master, relx: float, rely: float, logging_mode, folder_selected: str):
        self.logging_mode = logging_mode
        self.folder_selected = folder_selected
        self.button = tk.Button(master, text='Directory', width=8, state=tk.DISABLED)
        self.checkbox = tk.Checkbutton(text='Log output', variable=self.logging_mode, onvalue=1, offvalue=0,
                                       command=partial(self.toggle_logging_mode, None))
        self.place_widget(relx, rely)

    def toggle_logging_mode(self, logging_mode_to_set) -> Optional[str]:
        if type(logging_mode_to_set) is bool:
            self.logging_mode.set(logging_mode_to_set)
        self.button.config(state=tk.ACTIVE if self.logging_mode.get() else tk.DISABLED)
        return self.logging_mode.get()

    def popup_browse_dir(self, event: tk.Event) -> Optional[str]:
        if self.logging_mode.get():
            self.folder_selected = filedialog.askdirectory()
        return self.folder_selected

    def place_widget(self, relx: float, rely: float) -> None:
        self.button.place(relx=relx, rely=rely + 0.07, anchor=tk.CENTER)
        self.checkbox.place(relx=relx, rely=rely, anchor=tk.CENTER)


class ParameterWidget:
    def __init__(self, master, parameter_name, default_value, relx, rely):
        self.parameter_name = parameter_name
        self.added = False
        self.button = None
        self.entry = None
        self.label = None
        self.default_value = default_value
        self.add_remove = StringVar(value='Add')

    def check_if_entry_changed(self, var) -> None:
        getter = var.get()
        if not self.added and getter:
            self.added = True
            self.add_remove.set('Adjust')

    def place_widget(self, relx: float, rely: float) -> None:
        self.label.place(relx=relx, rely=rely, anchor=tk.CENTER)
        self.entry.place(relx=relx + 0.1, rely=rely, anchor=tk.CENTER)
        self.button.place(relx=relx + 0.21, rely=rely, anchor=tk.CENTER)

    def get_parameter_value(self) -> str:
        return self.entry.get()

    def clear_value(self) -> None:
        if self.entry:
            self.entry.delete(0, tk.END)

    def insert_default_value(self) -> None:
        if self.default_value:
            self.entry.insert(tk.INSERT, self.default_value)

    def added_toggle(self, value: bool) -> None:
        self.added = not value
        self.add_remove.set('Remove' if value else 'Add')


class WidgetUdpTcp(ParameterWidget):
    def __init__(self, master, parameter_name, default_value, relx, rely):
        super().__init__(master, parameter_name, default_value, relx, rely)
        self.default_value = default_value
        self.add_remove = StringVar(value=self.default_value)
        self.parameter_name = parameter_name
        self.button = tk.Button(master, textvariable=self.add_remove, width=15)
        self.place_widget(relx, rely)

    def get_parameter_value(self) -> str:
        return self.default_value

    def place_widget(self, relx: float, rely: float) -> None:
        self.button.place(relx=relx, rely=rely, anchor=tk.CENTER)

    def added_toggle(self, value: bool) -> None:
        if value:
            self.added = False
            self.add_remove.set('TCP')
        else:
            self.added = True
            self.add_remove.set('UDP')

    def insert_default_value(self) -> None:
        self.added_toggle(False)


class WidgetServerClient(ParameterWidget):
    def __init__(self, master, parameter_name, default_value, relx, rely):
        super().__init__(master, parameter_name, default_value, relx, rely)
        self.button = tk.Button(master, textvariable=self.add_remove, width=8)
        self.entry_var = StringVar()
        self.entry_var.trace(tk.W,
                             lambda name, index, mode, var=self.entry_var: self.check_if_entry_changed(self.entry_var))
        self.entry = tk.Entry(master, width=15, state=tk.DISABLED, textvariable=self.entry_var)
        self.server_client = StringVar(master, '0')
        self.server_client.trace(tk.W, lambda name, index, mode, var=self.server_client: self.check_if_entry_changed(
            self.server_client))
        self.button_a = tk.Radiobutton(master, text='Server (DL)', variable=self.server_client, value='server',
                                       command=lambda: self.set_to_server_or_client(var='server'))
        self.button_b = tk.Radiobutton(master, text='Client (UL)', variable=self.server_client, value='client',
                                       command=lambda: self.set_to_server_or_client(var='client'))
        self.place_widget(relx, rely)

    def set_to_server_or_client(self, var) -> None:
        if var == 'server':
            self.parameter_name = 'server'
            self.entry.config(state=tk.DISABLED)
        elif var == 'client':
            self.parameter_name = 'client'
            self.entry.config(state=tk.NORMAL)
        elif var == 'default':
            self.parameter_name = 'Server/Client'

    def set_server_client_mode(self, event: tk.Event, server_client_mode: str) -> str:
        self.parameter_name = server_client_mode
        return self.parameter_name

    def clear_value(self) -> None:
        self.set_to_server_or_client(var='default')
        self.server_client.set('0')
        if self.entry:
            self.entry.delete(0, tk.END)
        self.entry.config(state=tk.DISABLED)

    def place_widget(self, relx: float, rely: float) -> None:
        self.entry.place(relx=relx + 0.23, rely=rely, anchor=tk.CENTER)
        self.button_a.place(relx=relx + 0.05, rely=rely - 0.05, anchor=tk.CENTER)
        self.button_b.place(relx=relx + 0.05, rely=rely, anchor=tk.CENTER)
        self.button.place(relx=relx + 0.4, rely=rely - 0.02, anchor=tk.CENTER)


class WidgetSerialNumber(ParameterWidget):
    def __init__(self, master, parameter_name, default_value, relx, rely):
        super().__init__(master, parameter_name, default_value, relx, rely)
        self.entry = ttk.Combobox(master, width=35, state='readonly')
        self.label = tk.Label(master, text=parameter_name + ':')
        self.button = tk.Button(master, text='Get devices', width=10)
        self.place_widget(relx, rely)

    def place_widget(self, relx: float, rely: float) -> None:
        self.label.place(relx=relx, rely=rely, anchor=tk.CENTER)
        self.entry.place(relx=relx + 0.3, rely=rely, anchor=tk.CENTER)
        self.button.place(relx=relx + 0.6, rely=rely, anchor=tk.CENTER)

    def update_dut_serial_numbers_avi(self, dut_serial_numbers_avi) -> None:
        if dut_serial_numbers_avi:
            self.entry['values'] = dut_serial_numbers_avi
        else:
            self.entry['values'] = []
            self.entry.set('')

    def clear_value(self) -> None:
        self.entry.set('')
        self.entry.delete(0, tk.END)


class WidgetAddRemoveParameter(ParameterWidget):
    def __init__(self, master, parameter_name, default_value, relx, rely):
        super().__init__(master, parameter_name, default_value, relx, rely)
        self.default_value = default_value
        self.entry_var = StringVar()
        self.entry_var.trace(tk.W,
                             lambda name, index, mode, var=self.entry_var: self.check_if_entry_changed(self.entry_var))
        self.button = tk.Button(master, textvariable=self.add_remove, width=8)
        self.label = tk.Label(master, text=parameter_name + ':')
        self.entry = tk.Entry(master, width=5, textvariable=self.entry_var)
        self.place_widget(relx, rely)
