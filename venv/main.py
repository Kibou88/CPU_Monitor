import psutil
import tabulate
import time
import threading
import signal
from datetime import datetime
import cpuinfo
import argparse
import logging
import os

class CPUMonitor:
    def __init__(self, interval=5, tablefmt="fancy_grid", log_file=None):
        self.interval = interval
        self.tablefmt = tablefmt
        self.shutdown_event = threading.Event()
        self.log_file = log_file

        logging.basicConfig(filename=self.log_file,
                            level=logging.INFO,
                            format="%(asctime)s - %(levelname)s: %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    def handle_interrupt(self, signal, frame):
        self.shutdown_event.set()
        print("\nCtrl+C pressed. Stopping the program...")

    def get_cpu_info(self):
        try:
            info = cpuinfo.get_cpu_info()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_info={
                "Timestamp": timestamp,
                "Processor type": info.get("brand_raw", "Unknow"),
                "Physical cores": psutil.cpu_count(logical=False),
                "Total cores": psutil.cpu_count(logical=True),
                "Max frequency (MHz)": psutil.cpu_freq().max,
                "Min frequency (MHz)": psutil.cpu_freq().min,
                "Current frequency (MHz)": psutil.cpu_freq().current,
                "CPU usage": psutil.cpu_percent(interval=1)
            }
            logging.info(cpu_info)
            return cpu_info
        except cpuinfo.UnidentifiableCPUException as e:
            logging.error(f"Processor identification failed: {str(e)}")
            return {"Error":f"Processor identification failed: {str(e)}"}

    def print_cpu_info(self):
        while not self.shutdown_event.is_set():
            cpu_info = self.get_cpu_info()
            date = [(property, value) for property, value in cpu_info.items()]

            print("\nCPU Information:")
            print(tabulate.tabulate(date, headers="keys", tablefmt=self.tablefmt))

            time.sleep(self.interval)

    def cleanup(self):
        print("Cleanup: Stopping the CPU monitor thread ...")
        self.shutdown_event.set()

    def run(self):
        signal.signal(signal.SIGINT, self.handle_interrupt)

        try:
            cpu_info_thread = threading.Thread(target=self.print_cpu_info, daemon=True)
            cpu_info_thread.start()

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CPU Monitor with Table Formatting Options")
    parser.add_argument("--interval", type=int, default=5, help="Interval for updating CPU information (seconds)")
    parser.add_argument("--tablefmt", default="fancy_grid", help="Table format (e.g., plain, simple, fancy_grid)")
    parser.add_argument("--log_file", default="cpu_monitor.log", help="Path to the log file")

    args = parser.parse_args()
    os.system('cls')
    monitor = CPUMonitor(interval=args.interval, tablefmt=args.tablefmt, log_file=args.log_file)
    monitor.run()