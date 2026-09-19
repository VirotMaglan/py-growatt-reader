import threading
import time
from PIL import Image, ImageDraw
import pystray
import growattServer

# ================= AKTION: Zugangsdaten anpassen =================
USERNAME = '<User>'
PASSWORD = '<Password>'
DEVICE_SN = '<Device_SN>'
UPDATE_INTERVAL = 300            # Abruf-Intervall in Sekunden
# =================================================================

# Globale Variablen für den Tray-Status
soc = 0
tooltip_text = "Growatt: Lade Daten..."
is_running = True

def get_growatt_data():
    """ Holt alle Live- und Tagesdaten vom Growatt Server """
    global soc, tooltip_text
    try:
        api = growattServer.GrowattApi()
        api.server_url = 'https://server.growatt.com/'
        api.session.headers.update({'User-Agent': 'Mozilla/5.0 (Android; Mobile)'})

        # Login & Plant-ID automatisch ermitteln
        login_response = api.login(USERNAME, PASSWORD)
        user_id = login_response.get('user', {}).get('id') or login_response.get('back', {}).get('user', {}).get('id')

        plant_list = api.plant_list(user_id)
        plants = plant_list.get('data', []) if isinstance(plant_list, dict) else plant_list
        plant_id = plants[0]['plantId']

        # 1. Live-Daten abrufen
        mix_data = api.mix_system_status(DEVICE_SN, plant_id)

        pv_power = float(mix_data.get('ppv', 0))
        house_load = float(mix_data.get('pLocalLoad', 0))
        charge_kw = float(mix_data.get('chargePower', 0))
        discharge_kw = float(mix_data.get('pdisCharge1', 0))
        soc = int(float(mix_data.get('SOC', 0)))

        grid_export = float(mix_data.get('pactogrid', 0))
        grid_import = float(mix_data.get('pactouser', 0))

        # 2. Tageswerte berechnen
        e_to_grid = 0.0
        e_to_user = 0.0

        try:
            totals = api.mix_totals(DEVICE_SN, plant_id)
            e_to_grid = float(totals.get('etoGridToday') or 0)
            
            load_today = float(totals.get('elocalLoadToday') or 0)
            pv_today = float(totals.get('epvToday') or 0)
            charge_today = float(totals.get('echargetoday') or 0)
            discharge_today = float(totals.get('edischarge1Today') or 0)

            calc_user = (load_today + charge_today + e_to_grid) - (pv_today + discharge_today)
            e_to_user = max(0.0, calc_user)
        except Exception:
            pass

        # Text-Formatierung für den Netz-Status
        if grid_export > 0.05:
            grid_str = f"Netz: {grid_export:.1f} kW ▲ (Einspeisung)"
        elif grid_import > 0.05:
            grid_str = f"Netz: {grid_import:.1f} kW ▼ (Bezug)"
        else:
            grid_str = "Netz: 0.0 kW"

        # Text-Formatierung für den Akku-Status
        if charge_kw > 0.05:
            bat_str = f"Akku: {soc}% [▲ {charge_kw:.1f} kW]"
        elif discharge_kw > 0.05:
            bat_str = f"Akku: {soc}% [▼ {discharge_kw:.1f} kW]"
        else:
            bat_str = f"Akku: {soc}% [Standby]"

        # Mehrzeiligen Tooltip zusammenbauen (wird beim Überfahren mit der Maus angezeigt)
        lines = [
            f"PV-Leistung: {pv_power:.1f} kW",
            f"Verbrauch: {house_load:.1f} kW",
            grid_str,
            f"Einspeis. Heute: {e_to_grid:.1f} kWh",
            f"Bezug Heute: {e_to_user:.1f} kWh",
            bat_str
        ]
        tooltip_text = "\n".join(lines)

    except Exception:
        tooltip_text = "Growatt: Fehler bei Abfrage"

def create_battery_icon(percentage):
    """ Erstellt das kleine Akku-Icon für die Taskleiste """
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Farbwechsel je nach SOC
    if percentage > 30:
        color = (0, 220, 0)      # Grün
    elif percentage > 15:
        color = (255, 165, 0)    # Orange
    else:
        color = (230, 0, 0)      # Rot

    # Gehäuse der Batterie zeichnen
    draw.rectangle([8, 16, 50, 48], outline=(255, 255, 255), width=4)
    draw.rectangle([50, 26, 56, 38], fill=(255, 255, 255)) # Batterie-Pol

    # Füllstand zeichnen
    fill_width = int((42 * percentage) / 100)
    if fill_width > 0:
        draw.rectangle([12, 20, 12 + fill_width, 44], fill=color)

    return image

def update_loop(icon):
    """ Aktualisiert im Hintergrund schrittweise die Daten """
    while is_running:
        get_growatt_data()
        
        # Icon-Grafik und Tooltip-Text aktualisieren
        icon.icon = create_battery_icon(soc)
        icon.title = tooltip_text
        
        # Intervall abwarten
        time.sleep(UPDATE_INTERVAL)

def on_quit(icon, item):
    """ Beendet die Anwendung sauber """
    global is_running
    is_running = False
    icon.stop()

# Tray Icon initialisieren
initial_icon = create_battery_icon(0)
menu = pystray.Menu(pystray.MenuItem("Beenden", on_quit))
icon = pystray.Icon("GrowattTray", initial_icon, "Growatt: Lade Daten...", menu)

# Hintergrund-Thread starten
thread = threading.Thread(target=update_loop, args=(icon,), daemon=True)
thread.start()

# Tray-App starten
icon.run()