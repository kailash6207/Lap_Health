# Laptop Health Suite Pro — Ultimate Edition 💻

A multi-threaded, native desktop hardware diagnostic and optimization suite built with Python and Tkinter. This tool hooks directly into the Windows Kernel (`MSAcpi_ThermalZoneTemperature`) and utilizes low-level system queries to provide deep hardware telemetry, proactive maintenance advice, and one-click optimization tools.

Perfect for students, developers, and professionals who need to monitor machine vitals during heavy compiler, rendering, or engineering simulation workloads.

---

## 🚀 Key Features

- **📊 Hardware Vitals Dashboard:** Real-time monitoring of CPU core temperatures, memory pressures, and battery levels.
- **🌐 Network Quality Diagnostics:** Track active ping latency and micro-stutter network jitter values to ensure connection stability during live calls or remote syncs.
- **🔋 True Battery Health Calculator:** Bypasses basic OS readings to parse hidden hardware capacity data blocks (`powercfg`), calculating design capacity vs. full charge capacity degradation.
- **🧠 Active RAM Bottleneck Identification:** Scans running background processes using `psutil` to call out the top 3 memory-hogging applications by name.
- **🗄️ Multi-Drive Partition Mapping:** Dynamically tracks spaces across all connected storage volumes (`C:\`, `D:\`, etc.) with customized smart alert colors.
- **📈 Real-Time Performance Graphing:** Logs snapshots to a local database (`health_history.csv`) and plots live vector trend lines inside a custom Tkinter UI.
- **🛠️ Integrated Windows Care Toolkit:** One-click macro execution for Windows Disk Cleanup, Task Manager, and an automated background network DNS cache flush.

---

## 🛠️ Tech Stack & Architecture

- **Language:** Python 3.12
- **GUI Framework:** Tkinter / TTK (Clam Theme Styles)
- **Concurrency:** Multi-threaded asynchronous polling loop (`threading`)
- **Hardware Hook Engines:** `psutil`, Native Windows Management Instrumentation (WMI / CIM Core Classes via PowerShell execution pipes)
- **Data Persistence:** Lightweight CSV database streaming

---

## 🏃‍♂️ Installation & Development Setup

### 📋 Prerequisites
Ensure you have Python 3.10+ installed on your Windows machine.

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/kailash6207/Lap_Health.git
cd Lap_Health
2. Install Dependencies
Install the required system monitoring package:

Bash
pip install psutil
3. Run the Source Application
Note: Because the tool interacts directly with kernel-level motherboard thermal zones and system power management configs, you must launch your terminal or IDE as an Administrator.

Bash
python main.py
📦 Compiling Into a Standalone Desktop App (.exe)
To bundle the entire project into a single, independent executable application that can be run on any Windows device without Python installed:

Install PyInstaller:

Bash
pip install pyinstaller
Compile the Package:

Bash
python -m PyInstaller --noconsole --onefile main.py
Run the Executable:
Navigate to the newly generated dist/ directory to find your standalone main.exe application.
Right-click the executable file and select "Run as Administrator" to allow the native WMI thermal paths and battery metrics to initialize.

⚙️ How It Works (Under the Hood)
Asynchronous Telemetry: The UI stays responsive at 60 FPS because all heavy system hardware polls (pinging external servers, querying disk speeds, calculating process memory allocations) run on a detached, non-blocking background thread.

Kernel-Level Thermals: If third-party utilities are blocked, the engine falls back onto calling direct WMI queries into Win32_PerfFormattedData_Counters_ThermalZoneInformation to pull raw temperature sensor indices directly from the motherboard.

Local Persistence Data: Performance logs write cleanly to an appended health_history.csv spreadsheet vector file every 5 seconds, which the graphing module calculates into pixel coordinate offsets to draw vector performance curves inside a standard tk.Canvas grid.
