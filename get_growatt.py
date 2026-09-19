import growattServer

# ==========================================
# KONFIGURATION
# ==========================================
USERNAME = '<USER>'
PASSWORD = '<PASSWORD>'
DEVICE_SN = '<DEVICE_SN>'  # Hier die Seriennummer eintragen

try:
    api = growattServer.GrowattApi()
    api.server_url = 'https://server.growatt.com/'
    api.session.headers.update({'User-Agent': 'Mozilla/5.0 (Android; Mobile)'})

    login_response = api.login(USERNAME, PASSWORD)
    user_id = login_response.get('user', {}).get('id') or login_response.get('back', {}).get('user', {}).get('id')

    plant_list = api.plant_list(user_id)
    plants = plant_list.get('data', []) if isinstance(plant_list, dict) else plant_list
    plant_id = plants[0]['plantId']

    # OPTIONAL: Falls du die Seriennummer automatisch vom ersten Gerät der Anlage abrufen möchtest:
    # devices = api.device_list(plant_id)
    # DEVICE_SN = devices[0]['deviceSn']

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

    # Farb-Formatierung für PV-Leistung
    if pv_power < 0.05:
        pv_str = "${color #888888}0.0 kW${color}"
    else:
        pv_str = f"${{color #ffffff}}{pv_power:.1f} kW${{color}}"

    # Farb-Formatierung für Netz
    if grid_export > 0.05:
        grid_status = f"${{color #00ff00}}{grid_export:.1f} kW ▲${{color}}"
    elif grid_import > 0.05:
        grid_status = f"${{color #ff4500}}{grid_import:.1f} kW ▼${{color}}"
    else:
        grid_status = "${color #888888}0.0 kW${color}"

    # Farb-Formatierung für Einspeisung (kWh)
    if e_to_grid < 0.05:
        grid_today_str = "${color #888888}0.0 kWh${color}"
    else:
        grid_today_str = f"${{color #00ff00}}{e_to_grid:.1f} kWh${{color}}"

    # Farb-Formatierung für Bezug (kWh)
    if e_to_user < 0.05:
        user_today_str = "${color #888888}0.0 kWh${color}"
    else:
        user_today_str = f"${{color #ff4500}}{e_to_user:.1f} kWh${{color}}"

    # Akku-Status
    filled = round((soc / 100) * 6)
    bar = "█" * filled + "░" * (6 - filled)

    if charge_kw > 0.05:
        bat_status = f"${{color #00ff00}}▲ {charge_kw:.1f}kW${{color}}"
    elif discharge_kw > 0.05:
        bat_status = f"${{color #ff4500}}▼ {discharge_kw:.1f}kW${{color}}"
    else:
        bat_status = "${color #888888}Standby${color}"

    # Ausgabe (Conky-Syntax)
    print("${color #ffffff}PV-Leistung:${goto 110}" + pv_str)
    print("${color #ffffff}Verbrauch:${goto 110}" + f"{house_load:.1f}" + " kW")
    print("${color #ffffff}Netz:${goto 110}" + grid_status)
    print("${color #ffffff}Einspeis.:${goto 110}" + grid_today_str)
    print("${color #ffffff}Bezug:${goto 110}" + user_today_str)

except Exception as e:
    print(f"Fehler beim Abrufen der Daten: {e}")
    print("${color #ffffff}Akku:${goto 110}" + f"{soc}" + "% [" + bar + "] " + bat_status)

except Exception as e:
    print("Fehler bei Abfrage")
