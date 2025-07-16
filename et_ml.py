import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import joblib
import pandas as pd
from catboost import Pool

try:
    modelo_regresion = joblib.load("modelo_regresion.pkl")
    modelo_clasificacion = joblib.load("modelo_catboost.pkl")
except Exception as e:
    messagebox.showerror("Error", f"Error cargando modelos: {e}")
    exit()

FEATURES = ['RoundStartingEquipmentValue', 'TravelledDistance', 'Speed_mps', 'RoundKills',
            'RoundAssists', 'RoundHeadshots', 'TeamStartingEquipmentValue', 'Map', 'KillRate',
            'HeadshotRatio', 'EcoRound', 'DistancePerKill', 'EngagementIntensity',
            'PrimaryWeaponClass', 'round id', 'TimeAlive']

CAT_FEATURES = ['Map', 'PrimaryWeaponClass']

MAPS = ['de_dust2', 'de_inferno', 'de_mirage', 'de_nuke']
ARMAS = ['Rifle', 'SMG', 'Sniper', 'Shotgun', 'Pistola']

style = Style(theme='minty')
root = style.master
root.title("CSGO - Predicción de Supervivencia")
root.geometry("1000x800")
root.minsize(900, 700)

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=20, pady=20)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

notebook = ttk.Notebook(scrollable_frame)
notebook.pack(fill='both', expand=True, padx=15, pady=15)

def crear_control(parent, label, var, tipo, valores=None, rango=None, width=30):
    frame = ttk.Frame(parent)
    frame.pack(fill='x', pady=5, padx=10)
    ttk.Label(frame, text=label, width=width).pack(side='left', padx=10)
    if tipo == 'combobox':
        combo = ttk.Combobox(frame, textvariable=var, values=valores, state="readonly", width=25)
        combo.pack(side='right', fill='x', expand=True, padx=10)
    elif tipo == 'entry':
        entry = ttk.Entry(frame, textvariable=var, width=27)
        entry.pack(side='right', fill='x', expand=True, padx=10)
    elif tipo == 'check':
        check = ttk.Checkbutton(frame, variable=var)
        check.pack(side='right', padx=10)
    elif tipo == 'scale':
        value_frame = ttk.Frame(frame)
        value_frame.pack(side='right', fill='x', expand=True)
        scale = ttk.Scale(value_frame, variable=var, from_=rango[0], to=rango[1], orient='horizontal')
        scale.pack(fill='x', expand=True)
        value_label = ttk.Label(value_frame, textvariable=var, width=10)
        value_label.pack(side='right', padx=10)

frame_reg = ttk.Frame(notebook, padding=20)
notebook.add(frame_reg, text="Tiempo de Vida")

vars_reg = {
    'RoundStartingEquipmentValue': tk.DoubleVar(value=2500),
    'KillRate': tk.DoubleVar(value=0.3),
    'AssistRate': tk.DoubleVar(value=0.1),
    'FlankKillRate': tk.DoubleVar(value=0.05),
    'HeadshotRate': tk.DoubleVar(value=0.2),
    'FastKill': tk.IntVar(value=1),
    'TravelledDistance': tk.DoubleVar(value=500),
    'Speed_mps': tk.DoubleVar(value=1.8),
    'EquipRatio': tk.DoubleVar(value=0.75)
}

for var in vars_reg.values():
    if isinstance(var, tk.DoubleVar):
        var.trace_add('write', lambda *_, v=var: v.set(round(v.get(), 2)))

crear_control(frame_reg, "Presupuesto equipamiento:", vars_reg['RoundStartingEquipmentValue'], 'scale', rango=[0, 10000])
crear_control(frame_reg, "Kill Rate:", vars_reg['KillRate'], 'scale', rango=[0, 1])
crear_control(frame_reg, "Assist Rate:", vars_reg['AssistRate'], 'scale', rango=[0, 1])
crear_control(frame_reg, "Flank Kill Rate:", vars_reg['FlankKillRate'], 'scale', rango=[0, 1])
crear_control(frame_reg, "Headshot Rate:", vars_reg['HeadshotRate'], 'scale', rango=[0, 1])
crear_control(frame_reg, "Fast Kill:", vars_reg['FastKill'], 'check')
crear_control(frame_reg, "Distancia (m):", vars_reg['TravelledDistance'], 'scale', rango=[0, 2000])
crear_control(frame_reg, "Velocidad (m/s):", vars_reg['Speed_mps'], 'scale', rango=[0, 5])
crear_control(frame_reg, "Equip Ratio:", vars_reg['EquipRatio'], 'scale', rango=[0, 1])

ttk.Button(frame_reg, text="Predecir Tiempo de Vida", command=lambda: predecir_regresion(), style='info.TButton').pack(pady=15, ipady=5)

frame_clasif = ttk.Frame(notebook, padding=20)
notebook.add(frame_clasif, text="Supervivencia")

vars_clasif = {}
for feat in FEATURES:
    if feat in CAT_FEATURES:
        vars_clasif[feat] = tk.StringVar()
    elif feat == 'EcoRound':
        vars_clasif[feat] = tk.IntVar(value=0)
    elif feat == 'round id':
        continue
    else:
        vars_clasif[feat] = tk.DoubleVar(value=0.0)

vars_clasif['RoundStartingEquipmentValue'].set(2500)
vars_clasif['TravelledDistance'].set(1000)
vars_clasif['Speed_mps'].set(1.5)
vars_clasif['RoundKills'].set(1)
vars_clasif['RoundAssists'].set(0)
vars_clasif['RoundHeadshots'].set(0)
vars_clasif['TeamStartingEquipmentValue'].set(12000)
vars_clasif['Map'].set(MAPS[0])
vars_clasif['KillRate'].set(0.3)
vars_clasif['HeadshotRatio'].set(0.2)
vars_clasif['EcoRound'].set(0)
vars_clasif['DistancePerKill'].set(300)
vars_clasif['EngagementIntensity'].set(0.5)
vars_clasif['PrimaryWeaponClass'].set(ARMAS[0])

crear_control(frame_clasif, "Mapa:", vars_clasif['Map'], 'combobox', MAPS)
crear_control(frame_clasif, "Arma principal:", vars_clasif['PrimaryWeaponClass'], 'combobox', ARMAS)
crear_control(frame_clasif, "Presupuesto:", vars_clasif['RoundStartingEquipmentValue'], 'entry')
crear_control(frame_clasif, "Distancia:", vars_clasif['TravelledDistance'], 'entry')
crear_control(frame_clasif, "Velocidad:", vars_clasif['Speed_mps'], 'entry')
crear_control(frame_clasif, "Kills:", vars_clasif['RoundKills'], 'entry')
crear_control(frame_clasif, "Asistencias:", vars_clasif['RoundAssists'], 'entry')
crear_control(frame_clasif, "Headshots:", vars_clasif['RoundHeadshots'], 'entry')
crear_control(frame_clasif, "Presupuesto equipo:", vars_clasif['TeamStartingEquipmentValue'], 'entry')
crear_control(frame_clasif, "Kill Rate:", vars_clasif['KillRate'], 'entry')
crear_control(frame_clasif, "Ratio Headshots:", vars_clasif['HeadshotRatio'], 'entry')
crear_control(frame_clasif, "Eco Round:", vars_clasif['EcoRound'], 'check')
crear_control(frame_clasif, "Distancia por Kill:", vars_clasif['DistancePerKill'], 'entry')
crear_control(frame_clasif, "Intensidad:", vars_clasif['EngagementIntensity'], 'entry')

result_frame = ttk.Frame(frame_clasif)
result_frame.pack(fill='x', pady=20)

resultado_label = ttk.Label(result_frame, text="Complete los datos y haga clic en Predecir", font=('Helvetica', 12, 'bold'), style='info.Inverse.TLabel')
resultado_label.pack(fill='x', expand=True, ipady=5)

ttk.Button(frame_clasif, text="Predecir Supervivencia", command=lambda: predecir_clasificacion(), style='info.TButton').pack(pady=15, ipady=5)

def predecir_regresion():
    try:
        data = {
            'KillRate': vars_reg['KillRate'].get(),
            'AssistRate': vars_reg['AssistRate'].get(),
            'FlankKillRate': vars_reg['FlankKillRate'].get(),
            'HeadshotRate': vars_reg['HeadshotRate'].get(),
            'FastKill': vars_reg['FastKill'].get(),
            'TravelledDistance': vars_reg['TravelledDistance'].get(),
            'Speed_mps': vars_reg['Speed_mps'].get(),
            'RoundStartingEquipmentValue': vars_reg['RoundStartingEquipmentValue'].get(),
            'EquipRatio': vars_reg['EquipRatio'].get()
        }
        df = pd.DataFrame([data])
        pred = modelo_regresion.predict(df)[0]
        messagebox.showinfo("Resultado", f"Tiempo estimado de vida: {pred:.2f} segundos")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo calcular la predicción: {e}")

def predecir_clasificacion():
    try:
        ARMAS_BIN = ['PrimaryAssaultRifle', 'PrimarySniperRifle', 'PrimaryHeavy', 'PrimarySMG', 'PrimaryPistol']
        def arma_a_binaria(arma_seleccionada):
            return {arma: 1 if arma == arma_seleccionada else 0 for arma in ARMAS_BIN}
        
        datos_arma = arma_a_binaria(vars_clasif['PrimaryWeaponClass'].get())
        
        data = {
            'id': "0",
            'InternalTeamId': 1.0,
            'MatchId': "1",
            'RoundId': 0,
            'TimeAlive': 0,
            'TravelledDistance': float(vars_clasif['TravelledDistance'].get()),
            'RLethalGrenadesThrown': 0,
            'RNonLethalGrenadesThrown': 0,
            **datos_arma,
            'RoundKills': float(vars_clasif['RoundKills'].get()),
            'RoundAssists': float(vars_clasif['RoundAssists'].get()),
            'RoundHeadshots': float(vars_clasif['RoundHeadshots'].get()),
            'RoundFlankKills': 0,
            'RoundStartingEquipmentValue': float(vars_clasif['RoundStartingEquipmentValue'].get()),
            'TeamStartingEquipmentValue': float(vars_clasif['TeamStartingEquipmentValue'].get()),
            'MatchKills': 0,
            'MatchFlankKills': 0,
            'MatchAssists': 0,
            'MatchHeadshots': 0,
            'Speed_mps': float(vars_clasif['Speed_mps'].get())
        }

        columnas_ordenadas = [
            'id', 'InternalTeamId', 'MatchId', 'RoundId', 'TimeAlive', 'TravelledDistance',
            'RLethalGrenadesThrown', 'RNonLethalGrenadesThrown',
            'PrimaryAssaultRifle', 'PrimarySniperRifle', 'PrimaryHeavy', 'PrimarySMG', 'PrimaryPistol',
            'RoundKills', 'RoundAssists', 'RoundHeadshots', 'RoundFlankKills', 'RoundStartingEquipmentValue',
            'TeamStartingEquipmentValue', 'MatchKills', 'MatchFlankKills', 'MatchAssists', 'MatchHeadshots', 'Speed_mps'
        ]

        df = pd.DataFrame([data], columns=columnas_ordenadas)

        proba = modelo_clasificacion.predict_proba(df)[0]
        prob_no = proba[0]*100
        prob_si = proba[1]*100
        resultado_label.config(text=f"No Sobrevive: {prob_no:.1f}%  |  Sobrevive: {prob_si:.1f}%")
    except Exception as e:
        messagebox.showerror("Error", f"Error en predicción: {str(e)}")

root.mainloop()
