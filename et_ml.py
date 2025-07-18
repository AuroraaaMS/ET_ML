import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import joblib
import pandas as pd
from catboost import Pool

# Cargar modelos
try:
    modelo_regresion = joblib.load("modelo_regresion.pkl")
    modelo_clasificacion = joblib.load("modelo_catboost.pkl")
except Exception as e:
    messagebox.showerror("Error", f"Error cargando modelos: {e}")
    exit()

# Constantes
FEATURES = ['RoundStartingEquipmentValue', 'TravelledDistance', 'Speed_mps', 'RoundKills',
            'RoundAssists', 'RoundHeadshots', 'TeamStartingEquipmentValue', 'Map', 'KillRate',
            'HeadshotRatio', 'EcoRound', 'DistancePerKill', 'EngagementIntensity',
            'PrimaryWeaponClass', 'round id', 'TimeAlive']

CAT_FEATURES = ['Map', 'PrimaryWeaponClass']
MAPS = ['de_dust2', 'de_inferno', 'de_mirage', 'de_nuke']
ARMAS = ['Rifle', 'SMG', 'Sniper', 'Shotgun', 'Pistola']

# Configuración de estilo
style = Style(theme='darkly')
root = style.master
root.title("🎯 CSGO Analytics - Predicción de Supervivencia")
root.geometry("1200x800")
root.minsize(1000, 700)

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=20, pady=20)

canvas = tk.Canvas(main_frame, bg='#2b3035')
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

header_frame = ttk.Frame(scrollable_frame)
header_frame.pack(fill='x', pady=(0, 20))

title_label = ttk.Label(header_frame, text="🎯 CSGO Analytics", 
                       font=('Segoe UI', 24, 'bold'))
title_label.pack(anchor='w')

subtitle_label = ttk.Label(header_frame, text="Predicción avanzada de supervivencia en Counter-Strike",
                          font=('Segoe UI', 11))
subtitle_label.pack(anchor='w', pady=(5, 0))

separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.pack(fill='x', pady=(0, 20))

# Notebook
notebook = ttk.Notebook(scrollable_frame)
notebook.pack(fill='both', expand=True)

# Función para crear controles modernos
def crear_control_moderno(parent, label, variable, tipo, valores=None, min_val=0, max_val=100, unit=""):
    frame = ttk.Frame(parent)
    frame.pack(fill='x', pady=8, padx=40)
    
    if tipo == 'slider':
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill='x', pady=(0, 5))
        
        label_widget = ttk.Label(top_frame, text=label, font=('Segoe UI', 10))
        label_widget.pack(side='left')
        
        value_label = ttk.Label(top_frame, text=f"{variable.get():.1f}{unit}", 
                               font=('Segoe UI', 10, 'bold'),
                               foreground='#17a2b8')
        value_label.pack(side='right')
        
        scale = ttk.Scale(frame, variable=variable, 
                         from_=min_val, to=max_val, 
                         orient='horizontal')
        scale.pack(fill='x', pady=(0, 5))
        
        def update_value(*args):
            val = variable.get()
            value_label.config(text=f"{val:.1f}{unit}")
        
        variable.trace_add('write', update_value)
        
        range_frame = ttk.Frame(frame)
        range_frame.pack(fill='x')
        
        ttk.Label(range_frame, text=f"{min_val}{unit}", 
                 font=('Segoe UI', 8)).pack(side='left')
        ttk.Label(range_frame, text=f"{max_val}{unit}", 
                 font=('Segoe UI', 8)).pack(side='right')
    
    elif tipo == 'combobox':
        ttk.Label(frame, text=label, font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        combo = ttk.Combobox(frame, textvariable=variable, values=valores, 
                            state="readonly", font=('Segoe UI', 10))
        combo.pack(fill='x')
    
    elif tipo == 'checkbox':
        check = ttk.Checkbutton(frame, text=label, variable=variable)
        check.pack(anchor='w')

# TAB 1: TIEMPO DE VIDA
frame_reg = ttk.Frame(notebook, padding= (40, 20))
frame_reg.pack(fill='both', expand=True)
notebook.add(frame_reg, text="⏱️ Tiempo de Vida")

# Título
ttk.Label(frame_reg, text="Predicción de Tiempo de Supervivencia", 
          font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

# Variables para regresión
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

# Crear controles
crear_control_moderno(frame_reg, "💰 Presupuesto de Equipamiento", vars_reg['RoundStartingEquipmentValue'], 'slider', min_val=0, max_val=10000, unit="$")
crear_control_moderno(frame_reg, "🎯 Kill Rate", vars_reg['KillRate'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(frame_reg, "🤝 Assist Rate", vars_reg['AssistRate'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(frame_reg, "🔥 Flank Kill Rate", vars_reg['FlankKillRate'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(frame_reg, "💥 Headshot Rate", vars_reg['HeadshotRate'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(frame_reg, "⚡ Fast Kill", vars_reg['FastKill'], 'checkbox')
crear_control_moderno(frame_reg, "🏃 Distancia Recorrida", vars_reg['TravelledDistance'], 'slider', min_val=0, max_val=2000, unit="m")
crear_control_moderno(frame_reg, "⚡ Velocidad", vars_reg['Speed_mps'], 'slider', min_val=0, max_val=5, unit="m/s")
crear_control_moderno(frame_reg, "📊 Equipment Ratio", vars_reg['EquipRatio'], 'slider', min_val=0, max_val=1, unit="%")

button_frame_reg = ttk.Frame(frame_reg)
button_frame_reg.pack(fill='x', pady=30)

predict_button_reg = ttk.Button(button_frame_reg, 
                               text="🔮 PREDECIR TIEMPO DE VIDA", 
                               command=lambda: predecir_regresion(),
                               bootstyle="success",
                               width=40)
predict_button_reg.pack(pady=20, ipady=15)

# TAB 2: SUPERVIVENCIA
frame_clasif = ttk.Frame(notebook, padding=20)
notebook.add(frame_clasif, text="🛡️ Supervivencia")

# Título
ttk.Label(frame_clasif, text="Predicción de Supervivencia", 
          font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))

# Variables para clasificación
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

# Valores por defecto
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

# Crear controles en dos columnas
columns_frame = ttk.Frame(frame_clasif)
columns_frame.pack(fill='both', expand=True)

left_column = ttk.Frame(columns_frame)
left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))

right_column = ttk.Frame(columns_frame)
right_column.pack(side='right', fill='both', expand=True, padx=(15, 0))

# Columna izquierda
crear_control_moderno(left_column, "🔫 Arma Principal", vars_clasif['PrimaryWeaponClass'], 'combobox', ARMAS)
crear_control_moderno(left_column, "💰 Presupuesto Personal", vars_clasif['RoundStartingEquipmentValue'], 'slider', min_val=0, max_val=10000, unit="$")
crear_control_moderno(left_column, "🏃 Distancia Recorrida", vars_clasif['TravelledDistance'], 'slider', min_val=0, max_val=2000, unit="m")
crear_control_moderno(left_column, "⚡ Velocidad", vars_clasif['Speed_mps'], 'slider', min_val=0, max_val=5, unit="m/s")
crear_control_moderno(left_column, "🎯 Kills", vars_clasif['RoundKills'], 'slider', min_val=0, max_val=20)
crear_control_moderno(left_column, "🤝 Asistencias", vars_clasif['RoundAssists'], 'slider', min_val=0, max_val=20)

# Columna derecha
crear_control_moderno(right_column, "💥 Headshots", vars_clasif['RoundHeadshots'], 'slider', min_val=0, max_val=20)
crear_control_moderno(right_column, "👥 Presupuesto del Equipo", vars_clasif['TeamStartingEquipmentValue'], 'slider', min_val=0, max_val=20000, unit="$")
crear_control_moderno(right_column, "📈 Kill Rate", vars_clasif['KillRate'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(right_column, "🎯 Ratio de Headshots", vars_clasif['HeadshotRatio'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(right_column, "📏 Distancia por Kill", vars_clasif['DistancePerKill'], 'slider', min_val=0, max_val=1000, unit="m")
crear_control_moderno(right_column, "⚔️ Intensidad de Combate", vars_clasif['EngagementIntensity'], 'slider', min_val=0, max_val=1, unit="%")
crear_control_moderno(right_column, "💸 Eco Round", vars_clasif['EcoRound'], 'checkbox')

# BOTÓN Y RESULTADOS
results_container = ttk.Frame(frame_clasif)
results_container.pack(fill='x', pady=30)

predict_button_clasif = ttk.Button(results_container, 
                                  text="🔮 PREDECIR SUPERVIVENCIA", 
                                  command=lambda: predecir_clasificacion(),
                                  bootstyle="info",
                                  width=40)
predict_button_clasif.pack(pady=20, ipady=15)

# Área de resultados
result_frame = ttk.LabelFrame(results_container, text="📊 Resultados", padding=20)
result_frame.pack(fill='x', pady=20)

resultado_label = ttk.Label(result_frame, 
                           text="💀 No Sobrevive: --.-%  |  ✅ Sobrevive: --.-%", 
                           font=('Segoe UI', 16, 'bold'),
                           foreground='#17a2b8')
resultado_label.pack(pady=10)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Funciones de predicción
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
        
        messagebox.showinfo("🎯 Resultado de Predicción", 
                          f"⏱️ Tiempo estimado de supervivencia: {pred:.1f} segundos\n\n"
                          f"📊 Análisis: {'Supervivencia alta' if pred > 30 else 'Supervivencia baja' if pred < 15 else 'Supervivencia media'}")
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo calcular la predicción:\n{e}")

def predecir_clasificacion():
    try:
        def arma_a_binaria(arma):
            return {
                'PrimaryAssaultRifle': 1 if arma == 'Rifle' else 0,
                'PrimarySniperRifle': 1 if arma == 'Sniper' else 0,
                'PrimaryHeavy': 1 if arma == 'Shotgun' else 0,
                'PrimarySMG': 1 if arma == 'SMG' else 0,
                'PrimaryPistol': 1 if arma == 'Pistola' else 0,
            }

        data = {
            'id': '0',
            'InternalTeamId': 1.0,
            'MatchId': '1',
            'RoundId': 0,
            'TimeAlive': 0,
            'TravelledDistance': vars_clasif['TravelledDistance'].get(),
            'RLethalGrenadesThrown': 0,
            'RNonLethalGrenadesThrown': 0,
            **arma_a_binaria(vars_clasif['PrimaryWeaponClass'].get()),
            'RoundKills': vars_clasif['RoundKills'].get(),
            'RoundAssists': vars_clasif['RoundAssists'].get(),
            'RoundHeadshots': vars_clasif['RoundHeadshots'].get(),
            'RoundFlankKills': 0,
            'RoundStartingEquipmentValue': vars_clasif['RoundStartingEquipmentValue'].get(),
            'TeamStartingEquipmentValue': vars_clasif['TeamStartingEquipmentValue'].get(),
            'MatchKills': 0,
            'MatchFlankKills': 0,
            'MatchAssists': 0,
            'MatchHeadshots': 0,
            'Speed_mps': vars_clasif['Speed_mps'].get()
        }

        df = pd.DataFrame([data], columns=[
            'id', 'InternalTeamId', 'MatchId', 'RoundId', 'TimeAlive',
            'TravelledDistance', 'RLethalGrenadesThrown', 'RNonLethalGrenadesThrown',
            'PrimaryAssaultRifle', 'PrimarySniperRifle', 'PrimaryHeavy', 'PrimarySMG', 'PrimaryPistol',
            'RoundKills', 'RoundAssists', 'RoundHeadshots', 'RoundFlankKills',
            'RoundStartingEquipmentValue', 'TeamStartingEquipmentValue',
            'MatchKills', 'MatchFlankKills', 'MatchAssists', 'MatchHeadshots', 'Speed_mps'
        ])

        proba = modelo_clasificacion.predict_proba(df)[0]
        prob_no = proba[0] * 100
        prob_si = proba[1] * 100
        
        resultado_label.config(text=f"💀 No Sobrevive: {prob_no:.1f}%  |  ✅ Sobrevive: {prob_si:.1f}%")
        
        analisis = "Alta probabilidad de supervivencia" if prob_si > 70 else \
                  "Baja probabilidad de supervivencia" if prob_si < 30 else \
                  "Probabilidad media de supervivencia"
        
        messagebox.showinfo("🎯 Análisis de Supervivencia", 
                          f"📊 {analisis}\n\n"
                          f"✅ Probabilidad de supervivencia: {prob_si:.1f}%\n"
                          f"💀 Probabilidad de muerte: {prob_no:.1f}%\n\n"
                          f"💡 Recomendación: {'Mantén la estrategia' if prob_si > 60 else 'Considera ajustar la táctica'}")
        
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error en predicción:\n{str(e)}")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

if __name__ == "__main__":
    root.mainloop()
