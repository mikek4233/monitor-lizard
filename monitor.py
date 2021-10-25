#!/usr/bin/env python3
import psutil
import time
import sys
import re
import os
import pyshark
import subprocess
from prettytable import PrettyTable
from gi.repository import Notify
from badwords import words
from datetime import datetime
import math
from tabulate import tabulate

class MonitorLizzard:

    def __init__(self):
        self.home = os.path.expanduser("~")
        self.interface_count = 0
        self.networks = {}
        print(self.network_info())
        choice = self.get_choice("Please select a network interface to monitor: ", self.interface_count)
        self.interface = self.networks[choice]
        self.cut_off = input("Please select a amount of time (in seconds) to alert if you spend to much running an app: ")
        

    def get_choice(self, input_text, max_valid_value):
            """
            Returns the number of the selected wifi.

            Parameters
            ----------
            input_text: str
                The text to be printed when asking for input.
            max_valid_value: int
                The max valid value for the choices.
            terminator: int
                The value to terminate the procedure.
            """
            while True:
                try:
                    inserted_value = int(input(input_text))
                    if inserted_value <= max_valid_value:
                        return inserted_value
                    else:
                        print(
                            "Invalid input! Enter a number from the"
                            "choices provided.")
                except ValueError:
                    print(
                        "Invalid input! Enter a number from the choices provided.")

    def handle_key_log_file(self):
        if os.path.isfile(f"{self.home}/.ssl-key.log"):
            print('Using Existing Key Log File')
        else:
            print(f"Creating New Key Log File in {self.home} -- Closing Chrome")
            subprocess.run(["sudo", "pkill", "-9", "chrome"])
            f = open(f"{self.home}/.ssl-key.log", "x")
            open_site = subprocess.Popen(["google-chrome", "https://github.com/mikek4233/monitor-lizard"])
            time.sleep(5)
            open_site.terminate()

    def battery_info(self):
        battery = psutil.sensors_battery().percent
        return("----Battery Available: %d " % (battery,) + "%\n")

    def network_info(self):
        count = 1
        table = PrettyTable(['Number', 'Network', 'Status', 'Speed'])
        for key in psutil.net_if_stats().keys():
            num  = count
            name = key
            up = "Up" if psutil.net_if_stats()[key].isup else "Down"
            speed = psutil.net_if_stats()[key].speed
            table.add_row([num, name, up, speed])
            count += 1
            self.networks[num] = name
        self.interface_count = count
        return(table)

    def memory_info(self):
        memory_table = PrettyTable(["Total", "Used",
        "Available", "Percentage"])
        vm = psutil.virtual_memory()
        memory_table.add_row([
        vm.total,
        vm.used,
        vm.available,
        vm.percent
        ])
        return(memory_table)

    def processes_info(self):
        process_table = PrettyTable(['PID', 'PNAME', 'STATUS',
        'CPU', 'NUM THREADS'])

        for process in psutil.pids()[-10:]:

        # While fetching the processes, some of the subprocesses may exit
        # Hence we need to put this code in try-except block
            try:
                p = psutil.Process(process)
                process_table.add_row([
                str(process),
                p.name(),
                p.status(),
                str(p.cpu_percent())+"%",
                p.num_threads()
                ])

            except Exception as e:
                pass
        return(process_table)


    def find_sys_processes(self):
        processes = []
        subprocess.Popen(["ps -t - | awk -v p='CMD' 'NR==1 {n=index($0, p); next} {print substr($0, n)}' > sys_processes.txt"], shell=True)
        time.sleep(1)
        with open('sys_processes.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "/" in line:
                    processes.append(line.strip().split('/')[0].lower())
                elif "-" in line:
                    processes.append(line.strip().lower())
                    spl = line.split('-')
                    for char in spl:
                        processes.append(char.strip().lower())
                else:
                    processes.append(line.strip().lower())

        f.close()
        processes.extend(['xorg', 'gnome-shell'])

        return processes
        
    def send_notification(self, msg):
            Notify.init("Monitor Lizard")
            Notify.Notification.new(msg).show()
            Notify.uninit()

    def split_on_slash(self, word):
        return word.split('/')[0]

    def apps_info(self):
        processes = self.find_sys_processes()
        process_list = {}
        pretty_table = []
        for process in psutil.process_iter():
            with process.oneshot():
                create_time = datetime.fromtimestamp(process.create_time())
                create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
                name = process.name()
                status = process.status()
                duration = datetime.now() - create_time
                total_seconds = duration.total_seconds()
                minutes = math.floor(total_seconds/60)
                hours = math.floor(total_seconds/3600)
                duration_str = str(hours)+":"+str(minutes)
                process_list[name] = {'name': name, 'create_time': create_time_str, 'duration': duration_str, 'status': status, 'total_seconds': total_seconds}

        for key, value in process_list.items():
            slash = '/' in value['name']
            if slash:
                new_name = self.split_on_slash(value['name'])
            else:
                new_name = value['name']
            if value['status'] == 'running' and new_name.lower() not in processes:
                pretty_table.append([value['name'], value['status'], value['duration']])
                if (value["total_seconds"] > int(self.cut_off) and 'python' not in value['name']):
                    self.send_notification(f"{value['duration']} spent on: {value['name']}")
        print(tabulate(pretty_table, headers=['Name', 'Status', 'Duration'], tablefmt='orgtbl'))



    def monitor_network_requests(self):
        capture = pyshark.LiveCapture(interface=self.interface, display_filter='http2', override_prefs={'ssl.keylog_file': f"{self.home}/.ssl-key.log"})
        capture.sniff(timeout=3)

        for packet in capture.sniff_continuously(packet_count=3):
            try:
                if 'HTTP2' in packet:
                    stringed_version = str(packet.http2)
                    data = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', stringed_version)
                    for url in data:
                        j_url = ''.join(url)
                        print(j_url)
                        for word in words:
                            if word in j_url:
                                print(j_url)
                                self.send_notification(f"Alert!!! You are going to a bad site: {j_url}")                 
            except (Exception) as _:
                # ignore packets other than TCP, UDP and IPv4
                pass

    def run_loop(self):
        if len(sys.argv) > 1 and sys.argv[1] == 'chrome-manual':
            pass
        else:
            subprocess.run(["sudo", "pkill", "-9", "chrome"])
            subprocess.Popen(["google-chrome", "https://github.com/mikek4233/monitor-lizard"])
        # Run an infinite loop to constantly monitor the system
        while True:
            # Clear the screen using a bash command
            subprocess.run(["clear"])

            print("==============================  Process Monitor\
            ======================================\n")

            # Fetch the battery information
            print(self.battery_info())

            # Fetch the Network information
            print("----Networks----")
            print(self.network_info())

            # Fetch the memory information
            print("\n----Memory----")
            print(self.memory_info())

            # Fetch the last 10 processes from available processes
            print("\n----Processes----")
            print(self.processes_info())

            print("\n----App Info----")
            self.apps_info()

            print("\n----Network Requests----")
            self.monitor_network_requests()
        
            # Create a 1 second delay
            # time.sleep(1)


if __name__ == "__main__":
    monitor = MonitorLizzard()
    monitor.handle_key_log_file()
    monitor.run_loop()

