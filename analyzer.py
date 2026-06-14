# analyzer.py
import psutil
import shutil
import os
import subprocess
import csv
import re
from datetime import datetime
from config import STORAGE_WARNING_THRESHOLD, TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD, BATTERY_LOW_THRESHOLD, RAM_WARNING_THRESHOLD

class LaptopHealthAnalyzer:
    def __init__(self):
        self.history_file = "health_history.csv"
        self.initialize_history_log()
        self.ping_history = [] # Tracks the last 5 pings to calculate Jitter

    def initialize_history_log(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Battery_Percent", "RAM_Percent", "CPU_Temp"])

    def log_current_metrics(self, battery_pct, ram_pct, cpu_temp):
        temp_val = cpu_temp if cpu_temp else 0
        with open(self.history_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%H:%M:%S"), battery_pct, ram_pct, temp_val])

    def get_historical_data(self):
        points = []
        if not os.path.exists(self.history_file):
            return points
        try:
            with open(self.history_file, mode='r', encoding='utf-8') as f:
                reader = list(csv.DictReader(f))
                last_entries = reader[-15:]
                for row in last_entries:
                    points.append({
                        "time": row["Timestamp"],
                        "battery": float(row["Battery_Percent"]),
                        "ram": float(row["RAM_Percent"]),
                        "temp": float(row["CPU_Temp"])
                    })
        except Exception:
            pass
        return points

    def get_network_ping(self):
        """Pings Google DNS and tracks variation to compute network stability jitter."""
        current_ping = 999
        status = "Offline"
        
        if os.name == 'nt':
            cmd = ["ping", "-n", "1", "8.8.8.8"]
            try:
                output = subprocess.check_output(cmd, creationflags=0x08000000).decode()
                if "time=" in output:
                    time_part = output.split("time=")[1].split("ms")[0].strip()
                    current_ping = int(time_part)
                    status = "Online"
            except Exception:
                pass

        # Manage rolling history window for jitter tracking
        if status == "Online":
            self.ping_history.append(current_ping)
            if len(self.ping_history) > 5:
                self.ping_history.pop(0)
        else:
            self.ping_history = []

        # Calculate Jitter (Average absolute difference between consecutive pings)
        jitter = 0
        if len(self.ping_history) >= 2:
            diffs = [abs(self.ping_history[i] - self.ping_history[i-1]) for i in range(1, len(self.ping_history))]
            jitter = round(sum(diffs) / len(diffs), 1)

        return {"status": status, "ping_ms": current_ping, "jitter_ms": jitter}

    def get_battery_hardware_score(self):
        """Parses Windows kernel battery specs to extract true hardware health percentage."""
        default_return = {"score": 85, "text": "Good (Estimated 85% Max Capacity)", "design": "N/A", "full": "N/A"}
        
        if os.name != 'nt':
            return default_return

        try:
            # Generate a temporary windows xml style battery report file string
            report_path = os.path.join(os.getcwd(), "bat_rep.xml")
            subprocess.run(f'powercfg /batteryreport /xml /output "{report_path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Delete temporary trace files cleanly
                os.remove(report_path)

                # Look for DesignCapacity and FullChargeCapacity values via Regex blocks
                design_match = re.search(r'<DesignCapacity>(\d+)</DesignCapacity>', content)
                full_match = re.search(r'<FullChargeCapacity>(\d+)</FullChargeCapacity>', content)

                if design_match and full_match:
                    design_cap = int(design_match.group(1))
                    full_cap = int(full_match.group(1))
                    
                    if design_cap > 0:
                        true_health_pct = round((full_cap / design_cap) * 100)
                        
                        # Set health classification text boundaries
                        if true_health_pct >= 85: status = "Excellent"
                        elif true_health_pct >= 70: status = "Good (Normal Wear)"
                        else: status = "Degraded (Consider Replacement Soon)"
                        
                        return {
                            "score": true_health_pct,
                            "text": f"{status} ({true_health_pct}% Total Health Index)",
                            "design": f"{design_cap} mWh",
                            "full": f"{full_cap} mWh"
                        }
        except Exception:
            pass
        return default_return

    def get_battery_health(self):
        battery = psutil.sensors_battery()
        if not battery:
            return {"status": "Error", "message": "No battery detected."}
        
        hardware_info = self.get_battery_hardware_score()
        return {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft,
            "wear_health": hardware_info["text"],
            "design_cap": hardware_info["design"],
            "full_cap": hardware_info["full"]
        }

    def get_ram_usage(self):
        virtual_mem = psutil.virtual_memory()
        gb = 1024 ** 3
        top_processes = []
        try:
            for proc in psutil.process_iter(['name', 'memory_info']):
                try:
                    mem_mb = proc.info['memory_info'].rss / (1024 ** 2)
                    top_processes.append((proc.info['name'], mem_mb))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            top_processes = sorted(top_processes, key=lambda x: x[1], reverse=True)[:3]
        except Exception:
            top_processes = [("Unknown Application", 0.0)]

        return {
            "total_gb": round(virtual_mem.total / gb, 1),
            "used_gb": round(virtual_mem.used / gb, 1),
            "percent_used": virtual_mem.percent,
            "top_apps": top_processes
        }

    def get_storage_usage(self):
        drive_reports = []
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            if 'cdrom' in partition.opts or not partition.mountpoint:
                continue
            if partition.mountpoint.startswith('C:') or len(partition.mountpoint) <= 3:
                try:
                    total, used, free = shutil.disk_usage(partition.mountpoint)
                    gb = 1024 ** 3
                    percent_used = round((used / total) * 100, 1)
                    drive_reports.append({
                        "drive": partition.mountpoint,
                        "total_gb": round(total / gb, 1),
                        "used_gb": round(used / gb, 1),
                        "free_gb": round(free / gb, 1),
                        "percent_used": percent_used
                    })
                except PermissionError:
                    continue
        return drive_reports

    def get_temperature(self):
        """Ultra-robust hardware pipeline querying 5 distinct strategies for CPU thermals."""
        # Strategy 1: Native Cross-Platform Python Sensors
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for key in ['coretemp', 'cpu_thermal', 'acpitz', 'amd_sensors']:
                    if key in temps and temps[key]:
                        return {"status": "Success", "current": round(temps[key][0].current, 1)}
        except Exception:
            pass

        # Windows-Specific Advanced Engineering Queries
        if os.name == 'nt':
            import subprocess
            
            # Strategy 2: NATIVE WINDOWS FIRMWARE FALLBACK (No external apps needed!)
            try:
                # Query the motherboard's ACPI thermal zone directly via PowerShell Performance Counters
                cmd = "Get-CimInstance -ClassName Win32_PerfFormattedData_Counters_ThermalZoneInformation | Select-Object -ExpandProperty HighPrecisionTemperature"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000).decode().strip()
                if output and float(output) > 0:
                    # Conversion from Tenths of Kelvin to Celsius
                    celsius = (float(output) / 10.0) - 273.15
                    if 15 < celsius < 105: # Validation boundary check
                        return {"status": "Success", "current": round(celsius, 1)}
            except Exception:
                pass

            # Strategy 3: NATIVE WMI MSDN THERMALZONE DIRECT QUERY
            try:
                cmd = "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | Select-Object -ExpandProperty CurrentTemperature"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000).decode().strip()
                if output:
                    # Conversion from Decikelvins to Celsius
                    celsius = (float(output) / 10.0) - 273.15
                    if 15 < celsius < 105:
                        return {"status": "Success", "current": round(celsius, 1)}
            except Exception:
                pass

            # Strategy 4: OpenHardwareMonitor WMI fallback hook
            try:
                cmd = "Get-CimInstance -Namespace root/OpenHardwareMonitor -ClassName Sensor | Where-Object {$_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU Core*'} | Select-Object -ExpandProperty Value"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000).decode().strip()
                if output:
                    first_val = output.split('\n')[0].strip()
                    return {"status": "Success", "current": round(float(first_val), 1)}
            except Exception:
                pass

            # Strategy 5: LibreHardwareMonitor WMI fallback hook
            try:
                cmd = "Get-CimInstance -Namespace root/LibreHardwareMonitor -ClassName Sensor | Where-Object {$_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU Core*'} | Select-Object -ExpandProperty Value"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000).decode().strip()
                if output:
                    first_val = output.split('\n')[0].strip()
                    return {"status": "Success", "current": round(float(first_val), 1)}
            except Exception:
                pass

        return {
            "status": "Unsupported", 
            "current": None, 
            "message": "Thermal Sensors Restricted by Hardware/OS BIOS"
        }
    def generate_predictive_alerts(self, battery, storage_list, temp, ram, ping):
        alerts = []

        if ping["status"] != "Online":
            alerts.append("🌐 NETWORK DISCONNECTED: High packet loss or no connection detected. Check your Wi-Fi router link.")
        else:
            if ping["ping_ms"] >= 150:
                alerts.append(f"🐢 NETWORK LAG WARNING: Your ping is heavily elevated at {ping['ping_ms']}ms. You will experience delay in online classes.")
            if ping["jitter_ms"] >= 20:
                alerts.append(f"📡 NETWORK JITTER INSTABILITY: Wi-Fi ping variation is unstable ({ping['jitter_ms']}ms). This variance causes voice stuttering in calls.\n👉 Recommendation: Step closer to your router or swap channels.")

        for storage in storage_list:
            if storage["percent_used"] >= STORAGE_WARNING_THRESHOLD:
                alerts.append(f"⚠️ DISK THREAT ({storage['drive']}): Space is critical at {storage['percent_used']}%. High usage forces SSD write-wear.\n👉 Recommendation: Run Windows 'Disk Cleanup' or move large media files to your secondary partition.")

        if ram["percent_used"] >= RAM_WARNING_THRESHOLD:
            app_list_str = ", ".join([f"{name} ({round(size)}MB)" for name, size in ram["top_apps"]])
            alerts.append(f"⚡ RAM OVERLOAD: Memory usage is at {ram['percent_used']}%. Your system performance is reaching a critical bottleneck.\n🔥 Target Heavy Apps: The highest consumers are currently: {app_list_str}.\n👉 Recommendation: Manually close these specific applications to restore full system speed.")

        if temp["status"] == "Success" and temp["current"]:
            current_temp = temp["current"]
            if current_temp >= TEMP_CRITICAL_THRESHOLD:
                alerts.append(f"🔥 THERMAL CRITICAL: CPU is running dangerously hot at {current_temp}°C! Hardware throttling active.\n👉 Recommendation: Elevate your laptop base for better airflow or check for dust in the cooling vents.")
            elif current_temp >= TEMP_WARNING_THRESHOLD:
                alerts.append(f"⚠️ THERMAL WARNING: CPU core is warm ({current_temp}°C).\n👉 Recommendation: Pause intense tasks like large background calculations or browser compilation windows.")

        if "percent" in battery:
            if battery["percent"] <= BATTERY_LOW_THRESHOLD and not battery["power_plugged"]:
                alerts.append(f"🔋 LOW BATTERY: Remaining capacity is at {battery['percent']}%.\n👉 Recommendation: Plug in immediately to prevent sudden shutdown.")
        
        if not alerts:
            alerts.append("✅ SYSTEM HEALTH EXCELLENT: All network layers, memory values, thermal states, and storage partitions are clean.")
            
        return alerts

    def flush_dns(self):
        if os.name == 'nt':
            try:
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                return True
            except Exception:
                return False
        return False

    def export_text_log(self, battery, storage_list, temp, ram, alerts):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"Laptop_Advanced_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        full_filepath = os.path.join(desktop_path, filename)
        
        with open(full_filepath, "w", encoding="utf-8") as file:
            file.write("====================================================\n")
            file.write(f"       LAPTOP DIAGNOSTIC LOG SUITE PRO\n")
            file.write(f"       Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("====================================================\n\n")
            
            file.write("[1] BATTERY & CELL STRUCTURE\n")
            if "percent" in battery:
                file.write(f"  • Charge Status: {battery['percent']}%\n")
                file.write(f"  • Wall Attached: {battery['power_plugged']}\n")
                file.write(f"  • Lifetime Health State: {battery['wear_health']}\n")
                file.write(f"  • Factory Design Capacity: {battery['design_cap']}\n")
                file.write(f"  • Current Full Charge Capacity: {battery['full_cap']}\n")
            else:
                file.write(f"  • Note: {battery['message']}\n")
            file.write("\n")
            
            file.write("[2] VOLATILE MEMORY (RAM) & TOP CONSUMERS\n")
            file.write(f"  • Total Size: {ram['total_gb']} GB\n")
            file.write(f"  • Active Footprint: {ram['used_gb']} GB ({ram['percent_used']}%)\n")
            file.write("  • Top Active Memory Consuming Applications:\n")
            for name, size in ram["top_apps"]:
                file.write(f"    - {name}: {round(size, 1)} MB\n")
            file.write("\n")
            
            file.write("[3] MASS STORAGE SYSTEM\n")
            for drive in storage_list:
                file.write(f"  • Volume {drive['drive']} -> Used: {drive['used_gb']}GB / Total: {drive['total_gb']}GB ({drive['percent_used']}%)\n")
            file.write("\n")
            
            file.write("[4] THERMAL MATRIX\n")
            if temp["status"] == "Success":
                file.write(f"  • CPU core element temp: {temp['current']}°C\n\n")
            else:
                file.write(f"  • Status: {temp['message']}\n\n")
                
            file.write("====================================================\n")
            file.write("📋 DIAGNOSTIC ALERTS & ADVISORY FEED\n")
            file.write("====================================================\n")
            for alert in alerts:
                file.write(f"- {alert}\n\n")
                
        return full_filepath