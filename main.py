import tkinter
import tkinter as tk
import pyperclip
from collections import OrderedDict
from functools import partial
from tkinter import ttk, filedialog, StringVar, IntVar
from tkinter.messagebox import showinfo, showerror
from typing import Optional
from ppadb.client import Client
from utils import dut_connect as dut

HOST = 'localhost'
PORT = 5037
BASE_ADB = 'adb'
BASE_SERIAL_NO = 'serial_no'
BASE_SHELL = 'shell'
BASE_PATH = 'data/iperf'


class IperfCommand:
    def __init__(self):
        self.iperf_command_format = OrderedDict()
        self.add_base_parameters()
        self.param_added = False

    def add_base_parameters(self) -> None:
        self.iperf_command_format[BASE_ADB] = BASE_ADB
        self.iperf_command_format[BASE_SHELL] = BASE_SHELL
        self.iperf_command_format[BASE_PATH] = BASE_PATH

    def get_iperf_command(self) -> str:
        iperf_command_string = str()
        dut_selected = str()
        self.iperf_command_format.move_to_end(BASE_PATH, last=False)
        self.iperf_command_format.move_to_end(BASE_SHELL, last=False)
        if BASE_SERIAL_NO in self.iperf_command_format.keys():
            self.iperf_command_format.move_to_end(BASE_SERIAL_NO, last=False)
            dut_selected = str(self.iperf_command_format[BASE_SERIAL_NO]).split(' ')[1]

        self.iperf_command_format.move_to_end(BASE_ADB, last=False)
        for key, value in self.iperf_command_format.items():
            if value:
                iperf_command_string += value + ' '

        return (iperf_command_string, dut_selected)

    def add_remove_parameter(self, param_name: str, param_value: str) -> bool:
        param_name = param_name.lower()
        iperf_parameters_options = {'port': '-p',
                                    'time': '-t',
                                    'interval': '-i',
                                    'bandwidth': '-b',
                                    'length': '-l',
                                    'window size': '-w',
                                    'parallel': '-P'
                                    }

        if param_name not in self.iperf_command_format.keys():
            self.iperf_command_format[param_name] = iperf_parameters_options[param_name] + ' ' + param_value
            self.param_added = True
        else:
            if param_value == self.iperf_command_format[param_name].split(' ')[1]:
                self.iperf_command_format.pop(param_name, None)
                self.param_added = False
            else:
                self.iperf_command_format[param_name] = iperf_parameters_options[param_name] + ' ' + param_value
                self.param_added = True
        return self.param_added

    def add_remove_serial_number(self, serial_number: str) -> bool:
        if BASE_SERIAL_NO not in self.iperf_command_format.keys():
            self.iperf_command_format[BASE_SERIAL_NO] = '-s ' + serial_number
            self.param_added = True
        else:
            if self.iperf_command_format[BASE_SERIAL_NO].split(' ')[1] == serial_number:
                self.iperf_command_format.pop(BASE_SERIAL_NO, None)
                self.param_added = False
            else:
                self.iperf_command_format[BASE_SERIAL_NO] = '-s ' + serial_number
                self.param_added = True
        return self.param_added

    def add_remove_server_client(self, server_client_var: str, client_address: str) -> Optional[bool]:
        server_client_var = server_client_var.lower()
        if server_client_var == 'server/client':
            return None
        server_client_check = 'server_client'
        iperf_server_client_param_options = {'server': '-s',
                                             'client': '-c'}
        if server_client_var == 'server':
            client_address = ''

        if server_client_check not in self.iperf_command_format.keys():
            self.iperf_command_format[server_client_check] = iperf_server_client_param_options[
                                                                 server_client_var] + ' ' + client_address
            self.param_added = True
        else:
            if ('-c' in self.iperf_command_format[server_client_check] and server_client_var == 'client') or (
                    '-s' in self.iperf_command_format[server_client_check] and server_client_var == 'server'):
                self.iperf_command_format.pop(server_client_check, None)
                self.param_added = False
            else:
                self.iperf_command_format[server_client_check] = iperf_server_client_param_options[
                                                                     server_client_var] + ' ' + client_address
                self.param_added = True
        return self.param_added

    def add_remove_udp_tcp(self, udp_tcp_var: str) -> bool:
        udp_tcp_var = udp_tcp_var.lower()
        udp_tcp_check = 'udp'
        udp_var = '-u'

        if udp_tcp_check not in self.iperf_command_format.keys():
            self.iperf_command_format[udp_tcp_check] = udp_var
            self.param_added = True
        else:
            self.iperf_command_format.pop(udp_tcp_check, None)
            self.param_added = False
        return self.param_added


class View:
    def __init__(self, master: tkinter.Tk, dut_connect: dut.DUTConnect, logging_mode, iperf_command=IperfCommand):
        self.iperf_command = iperf_command
        self.dut_connect = dut_connect
        self.logging_mode = logging_mode
        self.folder_selected = str()

        self.title_label = tk.Label(master, text='Welcome to the Throughputter', font=('Arial', 16))
        self.title_label.place(relx=0.5, rely=0.02, anchor=tk.N)

        self.devices_frame = tk.LabelFrame(master, text="Devices", height=60, width=540)
        self.devices_frame.place(relx=0.5, rely=0.1, anchor=tk.N)

        self.parameters_frame = tk.LabelFrame(master, text="Parameters", height=180, width=540)
        self.parameters_frame.place(relx=0.5, rely=0.41, anchor=tk.N)

        self.server_client_frame = tk.LabelFrame(master, text="Server/Client", height=110, width=342)
        self.server_client_frame.place(relx=0.05, rely=0.3, anchor=tk.W)

        self.logging_frame = tk.LabelFrame(master, text="Logging", height=110, width=180)
        self.logging_frame.place(relx=0.65, rely=0.3, anchor=tk.W)

        self.logging_widget = LoggingWidget(master, relx=0.8, rely=0.27, logging_mode=self.logging_mode,
                                            folder_selected=self.folder_selected)

        self.parameter_serial_number = WidgetSerialNumber(master, parameter_name='Serial number',
                                                          default_value=None, relx=0.2,
                                                          rely=0.15)

        self.parameter_server_client = WidgetServerClient(master, parameter_name='Server/Client',
                                                          default_value=None,
                                                          relx=0.1, rely=0.33)

        self.parameter_udp_tcp = WidgetUdpTcp(master, parameter_name='UDP/TCP',
                                              default_value='UDP',
                                              relx=0.27, rely=0.47)

        self.parameter_port = WidgetAddRemoveParameter(master, parameter_name='Port',
                                                       default_value=5001, relx=0.15, rely=0.53)

        self.parameter_interval = WidgetAddRemoveParameter(master, parameter_name='Interval',
                                                           default_value=1, relx=0.15, rely=0.58)

        self.parameter_time = WidgetAddRemoveParameter(master, parameter_name='Time',
                                                       default_value=10, relx=0.15, rely=0.63)

        self.parameter_bandwidth = WidgetAddRemoveParameter(master, parameter_name='Bandwidth',
                                                            default_value='100m', relx=0.6, rely=0.48)

        self.parameter_length = WidgetAddRemoveParameter(master, parameter_name='Length',
                                                         default_value=1480, relx=0.6, rely=0.53)

        self.parameter_windows_size = WidgetAddRemoveParameter(master, parameter_name='Window size',
                                                               default_value='32m', relx=0.6, rely=0.58)

        self.parameter_parallel = WidgetAddRemoveParameter(master, parameter_name='Parallel',
                                                           default_value=1, relx=0.6, rely=0.63)

        self.iperf_textbox = tk.Text(master, width=60, height=3)
        self.iperf_textbox.place(relx=0.5, rely=0.77, anchor=tk.CENTER)

        self.button_run = tk.Button(master, text='Run iperf', width=15)
        self.button_run.place(relx=0.27, rely=0.9, anchor=tk.S)

        self.button_copy = tk.Button(master, text='Copy to clipboard', width=15)
        self.button_copy.place(relx=0.5, rely=0.9, anchor=tk.S)

        self.button_refresh = tk.Button(master, text='Refresh', width=15)
        self.button_refresh.place(relx=0.73, rely=0.9, anchor=tk.S)

        self.button_close_iperf = tk.Button(master, text='Close iperf', width=15)
        self.button_close_iperf.place(relx=0.27, rely=0.95, anchor=tk.S)

        self.button_about = tk.Button(master, text='About', width=15)
        self.button_about.place(relx=0.5, rely=0.95, anchor=tk.S)

        self.button_close_program = tk.Button(master, text='Close program', width=15)
        self.button_close_program.place(relx=0.73, rely=0.95, anchor=tk.S)

    def widgets_clear_and_refresh(self) -> None:
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ParameterWidget):
                attr.clear_value()
                attr.insert_default_value()
                attr.added_toggle(False)
            if isinstance(attr, LoggingWidget):
                attr.toggle_logging_mode(logging_mode_to_set=False)

    def refresh_iperf_command_textbox(self) -> None:
        self.iperf_textbox.delete(1.0, tk.END)
        self.iperf_command.iperf_command_format.clear()
        self.iperf_command.add_base_parameters()
        self.iperf_textbox.insert(tk.INSERT, self.iperf_command.get_iperf_command()[0])


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


class Controller:
    def __init__(self):
        self.root = tk.Tk()
        self.dut_connect = dut.DUTConnect(devices_connected=None, adb_client=Client(host=HOST, port=PORT), process=None)
        self.logging_mode = IntVar()
        self.iperf_command = IperfCommand()
        self.view = View(self.root, self.dut_connect, self.logging_mode, self.iperf_command)
        self.clear_and_refresh(event=None)

        self.view.parameter_serial_number.entry.bind('<<ComboboxSelected>>',
                                                     partial(self.update_iperf_command,
                                                             function=self.iperf_command.add_remove_serial_number,
                                                             parameter=None,
                                                             get_value=self.view.parameter_serial_number.get_parameter_value,
                                                             added_toggle=self.view.parameter_serial_number.added_toggle,
                                                             server_mode=False
                                                             ))

        self.view.logging_widget.button.bind('<ButtonRelease>', self.view.logging_widget.popup_browse_dir)

        self.view.parameter_serial_number.button.bind('<ButtonRelease>',
                                                      self.get_dut_serial_numbers_avi)

        self.view.parameter_udp_tcp.button.bind('<ButtonRelease>',
                                                partial(self.update_iperf_command,
                                                        function=self.iperf_command.add_remove_udp_tcp,
                                                        parameter=None,
                                                        get_value=self.view.parameter_udp_tcp.get_parameter_value,
                                                        added_toggle=self.view.parameter_udp_tcp.added_toggle,
                                                        server_mode=None
                                                        ))

        self.view.parameter_server_client.button_a.bind('<ButtonRelease>', partial(
            self.view.parameter_server_client.set_server_client_mode, server_client_mode='server'))

        self.view.parameter_server_client.button_b.bind('<ButtonRelease>', partial(
            self.view.parameter_server_client.set_server_client_mode, server_client_mode='client'))

        self.view.parameter_server_client.button.bind('<ButtonRelease>',
                                                      partial(self.update_iperf_command,
                                                              function=self.iperf_command.add_remove_server_client,
                                                              parameter=self.view.parameter_server_client.parameter_name,
                                                              get_value=self.view.parameter_server_client.get_parameter_value,
                                                              added_toggle=self.view.parameter_server_client.added_toggle,
                                                              server_mode=True
                                                              ))

        self.view.parameter_interval.button.bind('<ButtonRelease>',
                                                 partial(self.update_iperf_command,
                                                         function=self.iperf_command.add_remove_parameter,
                                                         parameter=self.view.parameter_interval.parameter_name,
                                                         get_value=self.view.parameter_interval.get_parameter_value,
                                                         added_toggle=self.view.parameter_interval.added_toggle,
                                                         server_mode=None
                                                         ))

        self.view.parameter_port.button.bind('<ButtonRelease>',
                                             partial(self.update_iperf_command,
                                                     function=self.iperf_command.add_remove_parameter,
                                                     parameter=self.view.parameter_port.parameter_name,
                                                     get_value=self.view.parameter_port.get_parameter_value,
                                                     added_toggle=self.view.parameter_port.added_toggle,
                                                     server_mode=None
                                                     ))

        self.view.parameter_time.button.bind('<ButtonRelease>',
                                             partial(self.update_iperf_command,
                                                     function=self.iperf_command.add_remove_parameter,
                                                     parameter=self.view.parameter_time.parameter_name,
                                                     get_value=self.view.parameter_time.get_parameter_value,
                                                     added_toggle=self.view.parameter_time.added_toggle,
                                                     server_mode=None
                                                     ))

        self.view.parameter_parallel.button.bind('<ButtonRelease>',
                                                 partial(self.update_iperf_command,
                                                         function=self.iperf_command.add_remove_parameter,
                                                         parameter=self.view.parameter_parallel.parameter_name,
                                                         get_value=self.view.parameter_parallel.get_parameter_value,
                                                         added_toggle=self.view.parameter_parallel.added_toggle,
                                                         server_mode=None
                                                         ))

        self.view.parameter_length.button.bind('<ButtonRelease>',
                                               partial(self.update_iperf_command,
                                                       function=self.iperf_command.add_remove_parameter,
                                                       parameter=self.view.parameter_length.parameter_name,
                                                       get_value=self.view.parameter_length.get_parameter_value,
                                                       added_toggle=self.view.parameter_length.added_toggle,
                                                       server_mode=None
                                                       ))

        self.view.parameter_windows_size.button.bind('<ButtonRelease>',
                                                     partial(self.update_iperf_command,
                                                             function=self.iperf_command.add_remove_parameter,
                                                             parameter=self.view.parameter_windows_size.parameter_name,
                                                             get_value=self.view.parameter_windows_size.get_parameter_value,
                                                             added_toggle=self.view.parameter_windows_size.added_toggle,
                                                             server_mode=None
                                                             ))

        self.view.parameter_bandwidth.button.bind('<Button>',
                                                  partial(self.update_iperf_command,
                                                          function=self.iperf_command.add_remove_parameter,
                                                          parameter=self.view.parameter_bandwidth.parameter_name,
                                                          get_value=self.view.parameter_bandwidth.get_parameter_value,
                                                          added_toggle=self.view.parameter_bandwidth.added_toggle,
                                                          server_mode=None
                                                          ))

        self.view.iperf_textbox.bind('<Return>', self.exec_iperf_command)
        self.view.button_run.bind('<ButtonRelease>', self.exec_iperf_command)
        self.view.button_copy.bind('<ButtonRelease>', self.copy_iperf_command)
        self.view.button_refresh.bind('<ButtonRelease>', self.clear_and_refresh)
        self.view.button_close_iperf.bind('<ButtonRelease>', self.close_iperf)
        self.view.button_about.bind('<ButtonRelease>', self.popup_about_window)
        self.view.button_close_program.bind('<ButtonRelease>', self.close_program)

    def get_dut_serial_numbers_avi(self, event: tk.Event) -> None:
        self.dut_connect.connect()
        dut_serial_numbers_avi = self.dut_connect.get_dut_serial_numbers_avi(event=None)
        self.view.parameter_serial_number.update_dut_serial_numbers_avi(dut_serial_numbers_avi=dut_serial_numbers_avi)

    def update_iperf_command(self, event: tk.Event, function, parameter, get_value, added_toggle,
                             server_mode: bool) -> None:
        if server_mode:
            parameter = self.view.parameter_server_client.parameter_name
        if parameter:
            flag_added = function(parameter, get_value())
        else:
            flag_added = function(get_value())
        added_toggle(flag_added)
        function_to_update_iperf_command = self.iperf_command.get_iperf_command()[0]
        self.view.iperf_textbox.delete(0.0, tk.END)
        self.view.iperf_textbox.insert(tk.INSERT, chars=function_to_update_iperf_command)

    def exec_iperf_command(self, event: tk.Event) -> None:
        logging = self.logging_mode.get()
        device_to_send = str()
        selected_folder = self.view.logging_widget.folder_selected
        if logging and not selected_folder:
            showerror('TPtter Error', 'Error: No directory selected')
            raise ValueError('No directory selected')
        iperf_command_final = self.view.iperf_textbox.get(0.0, tk.END).strip()

        if self.iperf_command.get_iperf_command()[1]:
            device_to_send = self.iperf_command.get_iperf_command()[1]
        elif self.dut_connect.devices_connected and len(self.dut_connect.devices_connected) == 1:
            device_to_send = self.dut_connect.devices_connected[0]
        else:
            showerror('TPtter Error', 'Error: No device available')
            raise ValueError('No device available')

        self.dut_connect.send_iperf_msg(iperf_command_final, device_to_send, logging, selected_folder)

    def copy_iperf_command(self, event: tk.Event) -> None:
        pyperclip.copy(self.view.iperf_textbox.get(0.0, tk.END))

    def clear_and_refresh(self, event: tk.Event) -> None:
        self.get_dut_serial_numbers_avi(event=None)
        self.view.widgets_clear_and_refresh()
        self.view.refresh_iperf_command_textbox()

    def close_iperf(self, event: tk.Event) -> None:
        self.dut_connect.close_prompt_window()

    def close_program(self, event: tk.Event) -> None:
        self.root.destroy()

    @staticmethod
    def popup_about_window(event: tk.Event) -> None:
        showinfo('About',
                 'Throughputter v.1.0\nA graphical UI to iperf, designed to run throughput tests over adb protocol\nBy: m.banaszczyk')

    def run(self) -> None:
        self.root.title('Throughputter')
        self.root.geometry('600x650')
        self.root.resizable(width=False, height=False)
        self.root.mainloop()


def main():
    tputter = Controller()
    tputter.run()


if __name__ == '__main__':
    main()
