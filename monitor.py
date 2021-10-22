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
from datetime import datetime, timedelta
from time import time
import math

HOME = os.path.expanduser("~")

def handle_key_log_file():
    if os.path.isfile(f"{HOME}/.ssl-key.log"):
        print('Using Existing Key Log File')
    else:
        print(f"Creating New Key Log File in {HOME} -- Closing Chrome")
        subprocess.run(["sudo", "pkill", "-9", "chrome"])
        f = open(f"{HOME}/.ssl-key.log", "x")
        open_site = subprocess.Popen(["google-chrome", "https://github.com/mikek4233/monitor-lizard"])
        time.sleep(5)
        open_site.terminate()


def battery_info():
    battery = psutil.sensors_battery().percent
    return("----Battery Available: %d " % (battery,) + "%\n")

def network_info():
    table = PrettyTable(['Network', 'Status', 'Speed'])
    for key in psutil.net_if_stats().keys():
        name = key
        up = "Up" if psutil.net_if_stats()[key].isup else "Down"
        speed = psutil.net_if_stats()[key].speed
        table.add_row([name, up, speed])
    return(table)

def memory_info():
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

def processes_info():
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

def apps_info():
    process_list = {}
    for process in psutil.process_iter():
        with process.oneshot():
            create_time = datetime.fromtimestamp(process.create_time())
            create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = datetime.now() - create_time
            total_seconds = duration.total_seconds()
            minutes = str(math.floor(total_seconds/60))
            hours = str(math.floor(total_seconds/3600))
            duration_str = hours+":"+minutes
            process_list[process.name()] = {'name': process.name(), 'create_time': create_time_str, 'duration': duration_str}

    dictionary_items = process_list.items()
    for item in dictionary_items:
        print(item)

def send_notification(msg):
        Notify.init("Monitor Lizard")
        Notify.Notification.new(msg).show()
        Notify.uninit()

def monitor_network_requests():
    capture = pyshark.LiveCapture(interface='wlp2s0', display_filter='http2', override_prefs={'ssl.keylog_file': f"{HOME}/.ssl-key.log"})
    capture.sniff(timeout=10)
    
    for packet in capture.sniff_continuously(packet_count=10):
        try:
            if 'HTTP2' in packet:
                stringed_version = str(packet.http2).splitlines()
                data = [line.strip().split(':', 1) for line in stringed_version]
                for pair in data:
                    head_type = str(pair[0])
                    if head_type == 'Header':
                        site = str(pair[1]).strip()
                        value = site.split(' ')
                        if value[0] == 'referer:':
                            print(value[1])
                            for word in words:
                                if word in site:
                                    send_notification(f"Alert!!! You are going to a bad site: {site}")
                    elif head_type == 'Value':
                        reg = re.compile('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
                        site = str(pair[1]).strip()
                        if bool(reg.search(site)):
                            print(site)
                            for word in words:
                                if word in site:
                                    send_notification(f"Alert!!! You are going to a bad site: {site}")
                    elif len(pair) > 1:
                        reg = re.compile('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
                        site = str(pair[1]).strip()
                        if bool(reg.search(site)):
                            print(site)
                            for word in words:
                                if word in site:
                                    send_notification(f"Alert!!! You are going to a bad site: {site}")                    

        except AttributeError as e:
            # ignore packets other than TCP, UDP and IPv4
            pass


def run_loop():
    apps_info()
    return
    if len(sys.argv) > 1 and sys.argv[1] == 'chrome-manual':
        pass
    else:
        subprocess.run(["sudo", "pkill", "-9", "chrome"])
        subprocess.Popen(["google-chrome", "https://github.com/mikek4233/monitor-lizard"])
    # Run an infinite loop to constantly monitor the system
    while True:
        # Clear the screen using a bash command
        # subprocess.call('clear')

        print("==============================  Process Monitor\
        ======================================\n")

        # Fetch the battery information
        print(battery_info())

        # Fetch the Network information
        print("----Networks----")
        print(network_info())

        # Fetch the memory information
        print("\n----Memory----")
        print(memory_info()
        )
        # Fetch the last 10 processes from available processes
        print("\n----Processes----")
        print(processes_info())

        # List all the pgms with create time and how long it's been running

        print("\n----Network Requests----")
        monitor_network_requests()

    # Create a 1 second delay
    time.sleep(1)


if __name__ == "__main__":
    handle_key_log_file()
    run_loop()