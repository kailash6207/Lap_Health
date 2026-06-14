# Laptop Health Suite Pro — Ultimate Edition 💻

A multi-threaded, native desktop hardware diagnostic and optimization suite built with Python and Tkinter. This tool hooks directly into the Windows Kernel (`MSAcpi_ThermalZoneTemperature`) and utilizes low-level system queries to provide deep hardware telemetry, proactive maintenance advice, and one-click optimization tools.

Perfect for students, developers, and professionals who need to monitor machine vitals during heavy compiler or simulation workloads.

## 🚀 Key Features

- **📊 Hardware Vitals Dashboard:** Real-time monitoring of CPU core temperatures, memory pressures, and battery levels.
- **🌐 Network Quality Diagnostics:** Track active ping latency and micro-stutter network jitter values to ensure connection stability during live calls or remote syncs.
- **🔋 True Battery Health Calculator:** Bypasses basic OS readings to parse hidden hardware capacity data blocks (`powercfg`), calculating design capacity vs. full charge capacity degradation.
- **🧠 Active RAM Bottleneck Identification:** Scans running background processes using `psutil` to call out the top 3 memory-hogging applications by name.
- **🗄️ Multi-Drive Partition Mapping:** Dynamically tracks spaces across all connected storage volumes (`C:\`, `D:\`, etc.) with customized smart alert colors.
- **📈 Real-Time Performance Graphing:** Logs snapshots to a local database (`health_history.csv`) and plots live vector trend lines inside a custom Tkinter UI.
- **🛠️ Integrated Windows Care Toolkit:** One-click macro execution for Windows Disk Cleanup, Task Manager, and an automated background network DNS cache flush.

## 🛠️ Tech Stack & Architecture

- **Language:** Python 3.12
- **GUI Framework:** Tkinter / TTK (Clam Theme Styles)
- **Concurrency:** Multi-threaded asynchronous polling loop (`threading`)
- **Hardware Hook Engines:** `psutil`, Native Windows Management Instrumentation (WMI / CIM Core Classes via PowerShell execution pipes)
- **Data Persistence:** Lightweight CSV database streaming

---

## 🏃‍♂️ Installation & Development Setup

### Prerequisites
Ensure you have Python 3.10+ installed on your Windows machine.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/Laptop-Health-Suite-Pro.git](https://github.com/YOUR_GITHUB_USERNAME/Laptop-Health-Suite-Pro.git)
   cd Laptop-Health-Suite-Pro

---

pip install psutil
python main.py
pip install pyinstaller
python -m PyInstaller --noconsole --onefile main.py
---

## 🚀 Step 3: Push to GitHub

Open your terminal in VS Code right inside your `Lap_Health` folder and run these Git commands to initialize your repository and push it online:

1. **Initialize Git in your project folder:**
   ```bash
   git init






   
