# Linux 
## how to use
I use it in conky to see different things about my PV.

### Features

- **System Tray Icon:** Dynamic battery icon reflecting your current SOC (State of Charge) with color coding (Green > 30%, Orange > 15%, Red ≤ 15%).
- **Hover Tooltip:** Shows detailed live and daily metrics when hovering over the tray icon:
  - Current PV power generation
  - Current household consumption
  - Grid import/export status
  - Today's grid feed-in (kWh)
  - Today's grid import (kWh)
  - Battery SOC and charge/discharge status
- **Zero Overhead:** Runs silently in the background without opening a terminal window.

---

### How to run
```
~/.config/venv/bin/python3 ~/.config/python/get_growatt.py

${color #ffffff}PV-Leistung:${goto 110}${color #ffffff}6.1 kW${color}
${color #ffffff}Verbrauch:${goto 110}0.8 kW
${color #ffffff}Netz:${goto 110}${color #00ff00}3.2 kW ▲${color}
${color #ffffff}Einspeis.:${goto 110}${color #00ff00}0.5 kWh${color}
${color #ffffff}Bezug:${goto 110}${color #ff4500}0.7 kWh${color}
${color #ffffff}Akku:${goto 110}94% [██████] ${color #00ff00}▲ 2.1kW${color}
```

# Windows
## Growatt Solar & Battery Windows Taskbar Monitor 

A lightweight Python script that runs in the background on Windows and displays your Growatt solar system and battery status directly in the system tray (taskbar).

---

### Features

- **System Tray Icon:** Dynamic battery icon reflecting your current SOC (State of Charge) with color coding (Green > 30%, Orange > 15%, Red ≤ 15%).
- **Hover Tooltip:** Shows detailed live and daily metrics when hovering over the tray icon:
  - Current PV power generation
  - Current household consumption
  - Grid import/export status
  - Today's grid feed-in (kWh)
  - Today's grid import (kWh)
  - Battery SOC and charge/discharge status
- **Zero Overhead:** Runs silently in the background without opening a terminal window.

---

### Prerequisites & Installation

#### 1. Install Python on Windows

1. Download the latest Python installer from the official site: [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer and **ensure you check the box:**
   > **`[x] Add python.exe to PATH`**
3. Complete the installation by clicking **Install Now**.

#### 2. Install Required Python Packages

Open Command Prompt (`cmd.exe`) or PowerShell and install the required dependencies:

```cmd
pip install pystray pillow growattServer
```

### Use the Script File
  1. Create a dedicated folder for your script (e.g., C:\GrowattTray\).
  2.   Use the file named growatt_tray.pyw .
        Note: Using the .pyw extension ensures that Windows executes the script silently without opening a black Command Prompt window.
  3. Change your user, password and device.

### To make the script run automatically every time Windows boots:
   1. Press Windows Key + R to open the Run dialog.
   2. Type shell:startup and press Enter. This opens your personal Startup folder.
   3. Right-click inside the folder and select New > Shortcut.
   4. Browse to and select your growatt_tray.pyw file.
