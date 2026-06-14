# main.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import time
from analyzer import LaptopHealthAnalyzer

class LaptopHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Health Suite Pro - Ultimate Edition")
        self.root.geometry("640x900") # Expanded height slightly for deep hardware telemetry rows
        self.root.resizable(False, False)
        
        self.analyzer = LaptopHealthAnalyzer()
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Normal.Horizontal.TProgressbar", troughcolor='#E0E0E0', background='#4A90E2')
        self.style.configure("Warning.Horizontal.TProgressbar", troughcolor='#E0E0E0', background='#D9534F')
        
        self.last_b, self.last_s, self.last_t, self.last_r, self.last_a = {}, [], {}, {}, []
        
        self.create_widgets()
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.monitor_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_dashboard = ttk.Frame(self.notebook, padding="15")
        self.tab_actions = ttk.Frame(self.notebook, padding="15")
        self.tab_trends = ttk.Frame(self.notebook, padding="15")
        
        self.notebook.add(self.tab_dashboard, text=" 📊 Hardware Monitors ")
        self.notebook.add(self.tab_trends, text=" 📈 Performance Trends ")
        self.notebook.add(self.tab_actions, text=" 🧠 Optimization Actions ")

        # ==================== TAB 1: HARDWARE DASHBOARD ====================
        header = ttk.Label(self.tab_dashboard, text="💻 REAL-TIME SYSTEM HARDWARE TELEMETRY", font=("Helvetica", 12, "bold"))
        header.pack(pady=(0, 10))

        # Network Diagnostics Monitor Block
        net_frame = ttk.LabelFrame(self.tab_dashboard, text=" 🌐 Network Connection Quality ", padding="10")
        net_frame.pack(fill=tk.X, pady=4)
        self.lbl_net_status = ttk.Label(net_frame, text="Network State: Checking link latency & jitter stability...", font=("Helvetica", 10))
        self.lbl_net_status.pack(anchor=tk.W)

        # PANEL 1: BATTERY WITH NEW DEGRADATION ESTIMATOR METRICS
        battery_frame = ttk.LabelFrame(self.tab_dashboard, text=" Power & Battery Integrity ", padding="10")
        battery_frame.pack(fill=tk.X, pady=4)
        self.lbl_battery_perc = ttk.Label(battery_frame, text="Charge Level: Checking...", font=("Helvetica", 10))
        self.lbl_battery_perc.pack(anchor=tk.W)
        self.lbl_battery_status = ttk.Label(battery_frame, text="Power Connection: Checking...", font=("Helvetica", 10))
        self.lbl_battery_status.pack(anchor=tk.W)
        self.lbl_battery_wear = ttk.Label(battery_frame, text="Battery Health Index: Checking system files...", font=("Helvetica", 10, "bold"), foreground="#2C3E50")
        self.lbl_battery_wear.pack(anchor=tk.W, pady=(2, 1))
        self.lbl_battery_caps = ttk.Label(battery_frame, text="Full Capacity: Fetching | Factory Design: Fetching", font=("Helvetica", 9, "italic"), foreground="#666666")
        self.lbl_battery_caps.pack(anchor=tk.W)

        # PANEL 2: RAM
        ram_frame = ttk.LabelFrame(self.tab_dashboard, text=" Volatile Memory (RAM) Allocation ", padding="10")
        ram_frame.pack(fill=tk.X, pady=4)
        self.lbl_ram_space = ttk.Label(ram_frame, text="Active Footprint: Fetching...", font=("Helvetica", 10))
        self.lbl_ram_space.pack(anchor=tk.W, pady=(0, 2))
        self.ram_bar = ttk.Progressbar(ram_frame, orient="horizontal", mode="determinate", style="Normal.Horizontal.TProgressbar")
        self.ram_bar.pack(fill=tk.X, pady=(0, 8))
        self.lbl_processes = ttk.Label(ram_frame, text="Gathering system process allocations...", font=("Consolas", 10), foreground="#555555")
        self.lbl_processes.pack(anchor=tk.W, pady=(4, 0))

        # PANEL 3: STORAGE
        self.storage_frame = ttk.LabelFrame(self.tab_dashboard, text=" Storage Systems Space Metrics ", padding="10")
        self.storage_frame.pack(fill=tk.X, pady=4)
        self.storage_inner_frame = ttk.Frame(self.storage_frame)
        self.storage_inner_frame.pack(fill=tk.X)

        # PANEL 4: THERMALS
        temp_frame = ttk.LabelFrame(self.tab_dashboard, text=" Thermal Processing Matrix ", padding="10")
        temp_frame.pack(fill=tk.X, pady=4)
        self.lbl_temp = ttk.Label(temp_frame, text="CPU Core Temp: Fetching...", font=("Helvetica", 11, "bold"))
        self.lbl_temp.pack(anchor=tk.W)

        # ==================== TAB 2: HISTORICAL TRENDS ====================
        trends_header = ttk.Label(self.tab_trends, text="📊 HISTORICAL TIMELINE OVER TIME (LAST 15 CYCLES)", font=("Helvetica", 11, "bold"))
        trends_header.pack(pady=(0, 10))
        
        legend_frame = ttk.Frame(self.tab_trends)
        legend_frame.pack(fill=tk.X, pady=2)
        ttk.Label(legend_frame, text="🟩 Battery Level (%)", font=("Helvetica", 9, "bold"), foreground="#2ECC71").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="🟦 RAM Allocation (%)", font=("Helvetica", 9, "bold"), foreground="#4A90E2").pack(side=tk.LEFT, padx=10)

        self.graph_canvas = tk.Canvas(self.tab_trends, width=560, height=340, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CCCCCC")
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.lbl_graph_hint = ttk.Label(self.tab_trends, text="💡 The graph updates dynamically in real-time as data samples are saved into health_history.csv.", font=("Helvetica", 9, "italic"), foreground="#666666")
        self.lbl_graph_hint.pack(pady=5)

        # ==================== TAB 3: SYSTEM OPTIMIZATION ACTIONS ====================
        actions_header = ttk.Label(self.tab_actions, text="🧠 AUTOMATED DIAGNOSTICS & ADVISORY CONTROL", font=("Helvetica", 12, "bold"))
        actions_header.pack(pady=(0, 10))

        alerts_frame = ttk.LabelFrame(self.tab_actions, text=" Live Maintenance & Optimization Advice ", padding="10")
        alerts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        scroll_bar = ttk.Scrollbar(alerts_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.txt_alerts = tk.Text(alerts_frame, height=11, wrap=tk.WORD, font=("Consolas", 10), bg="#F8F9FA", yscrollcommand=scroll_bar.set)
        self.txt_alerts.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        scroll_bar.config(command=self.txt_alerts.yview)
        self.txt_alerts.config(state=tk.DISABLED)

        tools_frame = ttk.LabelFrame(self.tab_actions, text=" 🛠️ Quick Maintenance Optimization Tools ", padding="10")
        tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_grid_frame = ttk.Frame(tools_frame)
        btn_grid_frame.pack(fill=tk.X, pady=2)
        
        self.btn_clean = ttk.Button(btn_grid_frame, text="🧹 Disk Cleanup", command=self.run_disk_clean)
        self.btn_clean.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.btn_task = ttk.Button(btn_grid_frame, text="📋 Task Manager", command=self.run_task_mgr)
        self.btn_task.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.btn_dns = ttk.Button(btn_grid_frame, text="🌐 Flush DNS Cache", command=self.run_dns_flush)
        self.btn_dns.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_export = ttk.Button(self.tab_actions, text="💾 Generate Comprehensive Diagnostic Log Report to Desktop", command=self.trigger_log_export)
        self.btn_export.pack(fill=tk.X, ipady=4)

        self.lbl_footer = ttk.Label(self.root, text="System Core Loop Active (5s Auto-Refresh Cycle)...", font=("Helvetica", 8, "italic"), foreground="#7F8C8D")
        self.lbl_footer.pack(side=tk.BOTTOM, pady=5)

    def update_loop(self):
        while self.running:
            b_data = self.analyzer.get_battery_health()
            s_data = self.analyzer.get_storage_usage()
            t_data = self.analyzer.get_temperature()
            r_data = self.analyzer.get_ram_usage()
            p_data = self.analyzer.get_network_ping()
            
            if "percent" in b_data:
                self.analyzer.log_current_metrics(b_data["percent"], r_data["percent_used"], t_data["current"])
                
            a_data = self.analyzer.generate_predictive_alerts(b_data, s_data, t_data, r_data, p_data)
            self.last_b, self.last_s, self.last_t, self.last_r, self.last_a = b_data, s_data, t_data, r_data, a_data
            
            if self.running:
                self.root.after(0, self.refresh_gui_elements, b_data, s_data, t_data, r_data, p_data, a_data)
            time.sleep(5)

    def refresh_gui_elements(self, battery, storage_list, temp, ram, ping, alerts):
        if not self.running:
            return

        # Update Network Performance Dashboard With Jitter
        if ping["status"] == "Online":
            self.lbl_net_status.config(
                text=f"Network State: Connected  |  Ping: {ping['ping_ms']} ms  |  Jitter Stability: {ping['jitter_ms']} ms", 
                foreground="#2C3E50"
            )
        else:
            self.lbl_net_status.config(text=f"Network State: {ping['status']}", foreground="#D9534F")

        # Update Battery and True Capacity Degradation Data
        if "percent" in battery:
            status_str = "Plugged In (Charging)" if battery["power_plugged"] else "Discharging (On Battery)"
            self.lbl_battery_perc.config(text=f"Current Charge: {battery['percent']}%")
            self.lbl_battery_status.config(text=f"Power Connection: {status_str}")
            self.lbl_battery_wear.config(text=f"True Battery Health Score: {battery['wear_health']}")
            self.lbl_battery_caps.config(text=f"Full Charge Max: {battery['full_cap']}  |  Factory Design Specification: {battery['design_cap']}")

        # Update RAM
        self.lbl_ram_space.config(text=f"Active Footprint: {ram['used_gb']} GB / Total {ram['total_gb']} GB ({ram['percent_used']}% allocated)")
        self.ram_bar['value'] = ram['percent_used']
        self.ram_bar.config(style="Warning.Horizontal.TProgressbar" if ram['percent_used'] >= 80.0 else "Normal.Horizontal.TProgressbar")
        proc_str = "Top 3 Active Memory Consumers:\n" + "\n".join([f"  ▶ {name:<22} ──► Using {round(size)} MB" for name, size in ram["top_apps"]])
        self.lbl_processes.config(text=proc_str)

        # Update Disks
        for widget in self.storage_inner_frame.winfo_children():
            widget.destroy()
        for drive in storage_list:
            drive_lbl = ttk.Label(self.storage_inner_frame, text=f"Drive ({drive['drive']}) » Used: {drive['used_gb']} GB / Total: {drive['total_gb']} GB ({drive['percent_used']}% used)", font=("Helvetica", 9))
            drive_lbl.pack(anchor=tk.W, pady=(2, 1))
            bar_style = "Warning.Horizontal.TProgressbar" if drive['percent_used'] >= 85.0 else "Normal.Horizontal.TProgressbar"
            pbar = ttk.Progressbar(self.storage_inner_frame, orient="horizontal", mode="determinate", style=bar_style)
            pbar.pack(fill=tk.X, pady=(0, 4))
            pbar['value'] = drive['percent_used']

        # Update CPU Thermals
        if temp["status"] == "Success":
            current_val = temp["current"]
            self.lbl_temp.config(text=f"CPU Core Temperature: {current_val}°C")
            if current_val >= 85: self.lbl_temp.config(foreground="#D9534F")
            elif current_val >= 75: self.lbl_temp.config(foreground="#F0AD4E")
            else: self.lbl_temp.config(foreground="#2ECC71")
        else:
            self.lbl_temp.config(text=f"CPU Temperature: {temp['message']}", foreground="#7F8C8D")

        # Update Diagnostics Alerts
        self.txt_alerts.config(state=tk.NORMAL)
        self.txt_alerts.delete('1.0', tk.END)
        for alert in alerts:
            self.txt_alerts.insert(tk.END, alert + "\n\n")
        self.txt_alerts.config(state=tk.DISABLED)

        self.draw_trends_graph()

    def draw_trends_graph(self):
        self.graph_canvas.delete("all")
        history = self.analyzer.get_historical_data()
        
        if len(history) < 2:
            self.graph_canvas.create_text(280, 170, text="Collecting metrics... (Graph populates after 2 sample cycles)", font=("Helvetica", 10, "italic"), fill="#999999")
            return

        c_width = 560
        c_height = 340
        padding = 40
        
        self.graph_canvas.create_line(padding, c_height - padding, c_width - padding, c_height - padding, fill="#CCCCCC", width=2)
        self.graph_canvas.create_line(padding, padding, padding, c_height - padding, fill="#CCCCCC", width=2)
        
        x_step = (c_width - (2 * padding)) / 14
        
        def get_y_coord(val_percent):
            graph_height = c_height - (2 * padding)
            return (c_height - padding) - (val_percent / 100.0 * graph_height)

        for i in range(0, 101, 25):
            y_pos = get_y_coord(i)
            self.graph_canvas.create_text(padding - 15, y_pos, text=f"{i}%", font=("Helvetica", 8), fill="#666666")
            self.graph_canvas.create_line(padding, y_pos, c_width - padding, y_pos, fill="#F0F0F0", dash=(2, 4))

        for idx in range(len(history) - 1):
            x1 = padding + (idx * x_step)
            x2 = padding + ((idx + 1) * x_step)
            
            y1_bat = get_y_coord(history[idx]["battery"])
            y2_bat = get_y_coord(history[idx+1]["battery"])
            self.graph_canvas.create_line(x1, y1_bat, x2, y2_bat, fill="#2ECC71", width=3)
            self.graph_canvas.create_oval(x1-3, y1_bat-3, x1+3, y1_bat+3, fill="#27AE60", outline="")

            y1_ram = get_y_coord(history[idx]["ram"])
            y2_ram = get_y_coord(history[idx+1]["ram"])
            self.graph_canvas.create_line(x1, y1_ram, x2, y2_ram, fill="#4A90E2", width=3)
            self.graph_canvas.create_oval(x1-3, y1_ram-3, x1+3, y1_ram+3, fill="#2980B9", outline="")

            if idx % 3 == 0 or idx == len(history) - 2:
                self.graph_canvas.create_text(x1, c_height - padding + 15, text=history[idx]["time"], font=("Helvetica", 7), fill="#7F8C8D")

    def run_disk_clean(self): os.system("start cleanmgr")
    def run_task_mgr(self): os.system("start taskmgr")
    def run_dns_flush(self):
        success = self.analyzer.flush_dns()
        if success: messagebox.showinfo("Network Optimization", "DNS cache flushed clean!")
        else: messagebox.showerror("Error", "Unable to clear DNS cache.")

    def trigger_log_export(self):
        if not self.last_s:
            messagebox.showwarning("System Notice", "Data loop initializing, please retry in 2 seconds.")
            return
        target_path = self.analyzer.export_text_log(self.last_b, self.last_s, self.last_t, self.last_r, self.last_a)
        messagebox.showinfo("Export Successful", f"Full health log written to your Windows desktop!\n\nSaved to:\n{target_path}")

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LaptopHealthApp(root)
    root.mainloop()