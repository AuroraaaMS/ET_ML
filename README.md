#  ET\_ML - Predicción de Supervivencia en CSGO

Este repositorio contiene una aplicación de escritorio basada en `Tkinter` para predecir el **tiempo de vida** y la **probabilidad de supervivencia** en una ronda de CS\:GO, utilizando modelos de regresión y clasificación previamente entrenados.

## Estructura del proyecto

```
ET_ML/
│
├── et_ml.py                  # Interfaz gráfica de la aplicación
├── modelo_regresion.pkl      # Modelo de regresión (Tiempo de Vida)
├── modelo_catboost.pkl       # Modelo de clasificación (Supervivencia)
└── README.md                 # Este archivo
```

---

## Requisitos

- Python 3.8 o superior (idealmente 3.8–3.12)
- pip

---

## Instalación (con entorno virtual recomendado)

1. Clona o descarga el repositorio.

2. Abre una terminal en la carpeta del proyecto y crea un entorno virtual:

   ```bash
   python -m venv venv
   ```

3. Activa el entorno virtual:

   - En PowerShell (Windows):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - En CMD (Windows):
     ```bash
     .\venv\Scripts\activate.bat
     ```

4. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

   Si no tienes un archivo `requirements.txt`, puedes instalar manualmente:

   ```bash
   pip install pandas catboost scikit-learn joblib ttkbootstrap
   ```

---

## Ejecución

Ejecuta la aplicación con:

```bash
python et_ml.py
```

Se abrirá una ventana gráfica con dos pestañas:

- **Tiempo de Vida**: usa un modelo de regresión para predecir la duración de vida estimada.
- **Supervivencia**: usa un modelo CatBoost para estimar la probabilidad de sobrevivir la ronda.

---

##et Solución de errores comunes

- ❌ `No module named 'sklearn'`: Instala con `pip install scikit-learn`
- ❌ `No module named 'ttkbootstrap'`: Instala con `pip install ttkbootstrap`
- ❌ La ventana no se abre: asegúrate de no estar en WSL, SSH o entornos sin GUI.
