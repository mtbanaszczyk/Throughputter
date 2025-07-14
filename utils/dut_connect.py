import logging
import subprocess
from datetime import datetime
from typing import Optional


class DUTConnect:
    def __init__(self, devices_connected, adb_client, process):
        self.devices_connected = devices_connected
        self.devices_connected = self.get_dut_serial_numbers_avi(event=None)
        self.adb_client = adb_client
        self.process = process
        self.logger = None
        self.file_handler = None

    @staticmethod
    def start_adb_server() -> None:
        subprocess.run(['adb', 'start-server'], shell=True)

    def connect(self) -> None:
        self.start_adb_server()
        try:
            self.adb_client.create_connection()
        except ConnectionError:
            return None

        self.devices_connected = self.adb_client.devices()
        if not self.devices_connected:
            return None
        return self.devices_connected

    def get_dut_serial_numbers_avi(self, event) -> Optional[list]:
        if self.devices_connected:
            self.devices_connected = [device.serial for device in self.devices_connected]
        else:
            return None
        return self.devices_connected

    def configure_logging(self, selected_folder: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        format_file_name = selected_folder + '/TPutter_iperf_test_' + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        format_message = '%(asctime)s %(message)s'
        format_date = '%m/%d/%Y %I:%M:%S %p'

        self.file_handler = logging.FileHandler(format_file_name)
        formatter = logging.Formatter(fmt=format_message, datefmt=format_date)
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

    def send_iperf_msg(self, iperf_command: str, dut_serial_number: str, if_logging: bool,
                       selected_folder: str) -> Optional[subprocess.Popen]:

        if self.devices_connected:
            iperf_msg = self.adb_client.device(dut_serial_number).shell(iperf_command)
            if if_logging:
                self.configure_logging(selected_folder)
                self.logger.info(iperf_msg)
                self.file_handler.close()
                self.logger.removeHandler(self.file_handler)

            messages = iperf_msg.split('\n')
            command_parts = ['echo ' + message.strip() for message in messages if message.strip()]
            command_final = ['cmd.exe', '/k', ' & '.join(command_parts)]

            self.process = subprocess.Popen(command_final, encoding='utf-8',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE)
            return self.process
        return None

    def close_prompt_window(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
