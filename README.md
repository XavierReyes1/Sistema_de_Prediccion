# 🌧️ Sistema de Predicción de Drenaje Pluvial

Sistema completo para simular lluvia horaria y evaluar excedentes de capacidad de drenaje en diferentes zonas, con interfaz web interactiva.

## 📋 Características

- ✅ Lectura automática de datos desde archivos Excel (XLSX)
- ✅ Simulación de lluvia horaria con diferentes intensidades
- ✅ Cálculo de excedentes respecto a capacidad de drenaje
- ✅ Interfaz web con mapa interactivo
- ✅ Visualización de resultados con gráficos
- ✅ Evaluación de escenarios preventivos
- ✅ Niveles de riesgo automáticos

## 🔧 Instalación

### 1. Requisitos Previos

```bash
# Python 3.8 o superior
python --version
```

### 2. Instalar Dependencias

```bash
pip install pandas numpy openpyxl flask
```

### 3. Estructura de Archivos

Crea la siguiente estructura de carpetas:

```
proyecto_drenaje/
├── drainage_model.py          # Modelo de simulación
├── web_drainage_app.py        # Aplicación web
├── create_excel_example.py    # Script para crear Excel de ejemplo
├── datos_zonas.xlsx           # Archivo de datos (generado)
└── README.md                  # Este archivo
```

## 📊 Formato del Archivo Excel

Cada hoja del Excel representa una zona y debe tener:

```
A1: "Latitud: 14.0723, Longitud: -87.1921"
A2: (Opcional) Información adicional
A3: Capacidad_Drenaje_mm_h
B3: Area_Metros_Cuadrados
A4+: Datos numéricos
```

### Ejemplo de Hoja:

| Celda | Contenido |
|-------|-----------|
| A1 | Latitud: 14.0723, Longitud: -87.1921 |
| A2 | Zona: Tegucigalpa Centro |
| A3 | Capacidad_Drenaje_mm_h |
| B3 | Area_Metros_Cuadrados |
| A4 | 8.5 |
| B4 | 5000 |
| A5 | 9.2 |
| B5 | 6500 |

## 🚀 Uso Rápido

### 1. Crear Archivo Excel de Ejemplo

```bash
python create_excel_example.py
```

Esto genera `datos_zonas.xlsx` con 5 zonas de ejemplo en Honduras.

### 2. Usar el Modelo Directamente (Python)

```python
from drainage_model import DrainageSimulationModel

# Cargar modelo
modelo = DrainageSimulationModel('datos_zonas.xlsx')

# Ver zonas disponibles
print(modelo.get_zones_list())

# Configurar escenario
escenario = {
    'hours': 24,                    # Duración en horas
    'intensity': 'heavy',           # light, moderate, heavy, extreme
    'drainage_capacity': 8.0,       # mm/hora
    'area_m2': 5000                 # metros cuadrados
}

# Ejecutar simulación
resultados, resumen = modelo.evaluate_scenario('Tegucigalpa Centro', escenario)

# Ver resultados
print(resumen)
print(resultados.head())

# Exportar a Excel
modelo.export_results(resultados, resumen, 'resultados.xlsx')
```

### 3. Iniciar Aplicación Web

```bash
python web_drainage_app.py
```

Luego abre tu navegador en: `http://localhost:5000`

## 🎯 Uso de la Aplicación Web

1. **Seleccionar Ubicación:**
   - Haz clic en el mapa o usa el menú desplegable
   - Los marcadores muestran todas las zonas disponibles

2. **Configurar Escenario:**
   - **Intensidad de Lluvia:**
     - Ligera: 2-5 mm/h (llovizna)
     - Moderada: 5-15 mm/h (lluvia normal)
     - Fuerte: 15-40 mm/h (tormenta)
     - Extrema: 30-80 mm/h (evento extremo)
   
   - **Duración:** Horas a simular (1-72)
   - **Capacidad de Drenaje:** mm/h que puede evacuar el sistema
   - **Área de la Zona:** Superficie en metros cuadrados

3. **Ejecutar Simulación:**
   - Clic en "Ejecutar Simulación"
   - Espera los resultados (1-2 segundos)

4. **Interpretar Resultados:**
   - **Lluvia Total:** Precipitación acumulada en el evento
   - **Excedente Total:** Agua que no pudo evacuar el sistema
   - **Nivel de Riesgo:**
     - 🟢 Normal: Sin excedentes
     - 🟡 Precaución: Excedente < 5 mm
     - 🟠 Alerta: Excedente 5-15 mm
     - 🔴 Peligro: Excedente 15-30 mm
     - ⚫ Emergencia: Excedente > 30 mm

## 📈 Interpretación de Gráficos

El gráfico muestra tres líneas:

1. **Azul (Lluvia):** Intensidad de lluvia por hora
2. **Verde punteada (Capacidad):** Límite del sistema de drenaje
3. **Roja (Excedente Acumulado):** Agua no evacuada acumulándose

**Cuando la línea azul está por encima de la verde:** El sistema está saturado y se acumula agua.

## 🔬 Metodología de Simulación

### Generación de Lluvia

La lluvia se simula usando distribución gamma para reflejar patrones naturales:

- **Distribución:** Gamma (más realista que normal)
- **Parámetros:** Ajustados según intensidad
- **Variabilidad:** Cada hora es independiente pero realista

### Cálculo de Excedentes

```
Excedente_Hora = max(0, Lluvia_Hora - Capacidad_Drenaje)
Excedente_Acumulado = Σ Excedente_Hora
Volumen_Litros = (Lluvia_mm × Area_m²) / 1000
```

## 🎨 Personalización

### Agregar Nuevas Zonas

1. Abre `datos_zonas.xlsx`
2. Crea una nueva hoja con el nombre de la zona
3. Sigue el formato descrito arriba
4. Reinicia la aplicación web

### Modificar Intensidades de Lluvia

En `drainage_model.py`, edita el diccionario `intensity_patterns`:

```python
intensity_patterns = {
    'custom': {'mean': 20, 'std': 10, 'max': 50}
}
```

### Cambiar Niveles de Riesgo

En `drainage_model.py`, método `get_risk_level`:

```python
def get_risk_level(self, excess):
    if excess == 0:
        return 'Normal'
    elif excess < 10:  # Cambiar umbrales aquí
        return 'Precaución'
    # ...
```

## 🌍 Despliegue en Servidor

### Opción 1: Servidor Local en Red

```bash
# Modificar en web_drainage_app.py:
app.run(host='0.0.0.0', port=5000)

# Acceder desde otra computadora:
http://[IP_DEL_SERVIDOR]:5000
```

### Opción 2: Heroku (Gratis)

```bash
# Crear Procfile
echo "web: python web_drainage_app.py" > Procfile

# Crear requirements.txt
pip freeze > requirements.txt

# Desplegar
heroku create mi-app-drenaje
git push heroku main
```

### Opción 3: PythonAnywhere (Gratis)

1. Sube los archivos a PythonAnywhere
2. Crea una nueva Web App (Flask)
3. Configura el WSGI file apuntando a `web_drainage_app.py`

## 🐛 Solución de Problemas

### Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### Error: "Zona no encontrada"
- Verifica que el nombre de la hoja en Excel sea exacto
- Revisa que el archivo `datos_zonas.xlsx` esté en la carpeta correcta

### Gráfico no se muestra
- Verifica que Chart.js se cargue correctamente (requiere internet)
- Revisa la consola del navegador (F12) para errores

### Mapa no aparece
- Verifica conexión a internet (usa tiles de OpenStreetMap)
- Revisa que las coordenadas en A1 sean válidas

## 📞 Soporte

Este sistema fue diseñado para:
- Gestión municipal de riesgos de inundación
- Planificación urbana preventiva
- Evaluación de infraestructura de drenaje
- Estudios de impacto ambiental

## 📝 Licencia

Software libre para uso educativo y gubernamental.

## 🔄 Actualizaciones Futuras

- [ ] Integración con APIs de pronóstico meteorológico
- [ ] Base de datos para almacenar simulaciones históricas
- [ ] Exportar reportes en PDF
- [ ] Análisis de múltiples zonas simultáneas
- [ ] Mapas de calor de riesgo
- [ ] Alertas automáticas por email/SMS
- [ ] Integración con sensores IoT de nivel de agua

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025