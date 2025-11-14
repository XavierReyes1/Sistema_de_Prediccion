import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import openpyxl

class DrainageSimulationModel:
    """
    Modelo para simular lluvia horaria y evaluar excedentes de drenaje
    """
    
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.zones_data = {}
        self.load_data()
    
    def load_data(self):
        """Carga datos de todas las hojas del archivo Excel"""
        wb = openpyxl.load_workbook(self.excel_file)
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Leer ubicación de A1 (formato: "lat, lon" o similar)
            location_text = ws['A1'].value
            lat, lon = self.parse_location(location_text)
            
            # Leer encabezados de A3 y B3
            header1 = ws['A3'].value
            header2 = ws['B3'].value
            
            # Leer datos desde A4 en adelante
            data = []
            for row in ws.iter_rows(min_row=4, values_only=True):
                if row[0] is not None:
                    data.append(row[:2])
            
            df = pd.DataFrame(data, columns=[header1, header2])
            
            self.zones_data[sheet_name] = {
                'latitude': lat,
                'longitude': lon,
                'data': df,
                'headers': [header1, header2]
            }
        
        wb.close()
    
    def parse_location(self, location_text):
        """Extrae latitud y longitud del texto"""
        if not location_text:
            return 0.0, 0.0
        
        # Buscar números en el texto
        import re
        numbers = re.findall(r'-?\d+\.?\d*', str(location_text))
        
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
        return 0.0, 0.0
    
    def simulate_rainfall(self, zone_name, hours=24, intensity='moderate'):
        """
        Simula lluvia horaria
        
        Args:
            zone_name: Nombre de la zona (hoja de Excel)
            hours: Número de horas a simular
            intensity: 'light', 'moderate', 'heavy', 'extreme'
        """
        # Patrones de intensidad de lluvia (mm/hora)
        intensity_patterns = {
            'light': {'mean': 2, 'std': 1, 'max': 5},
            'moderate': {'mean': 5, 'std': 3, 'max': 15},
            'heavy': {'mean': 15, 'std': 8, 'max': 40},
            'extreme': {'mean': 30, 'std': 15, 'max': 80}
        }
        
        pattern = intensity_patterns.get(intensity, intensity_patterns['moderate'])
        
        # Generar lluvia con distribución gamma (más realista)
        shape = (pattern['mean'] / pattern['std']) ** 2
        scale = pattern['std'] ** 2 / pattern['mean']
        
        rainfall = np.random.gamma(shape, scale, hours)
        rainfall = np.clip(rainfall, 0, pattern['max'])
        
        return rainfall
    
    def calculate_drainage_excess(self, zone_name, rainfall_data, 
                                  drainage_capacity=10.0, area_m2=1000):
        """
        Calcula el excedente de agua respecto a la capacidad de drenaje
        
        Args:
            zone_name: Nombre de la zona
            rainfall_data: Array de precipitación horaria (mm/hora)
            drainage_capacity: Capacidad de drenaje (mm/hora)
            area_m2: Área de la zona en metros cuadrados
        
        Returns:
            DataFrame con análisis horario
        """
        results = []
        accumulated_excess = 0
        
        for hour, rainfall in enumerate(rainfall_data):
            # Calcular excedente por hora
            excess = max(0, rainfall - drainage_capacity)
            accumulated_excess += excess
            
            # Volumen de agua en litros
            volume_liters = (rainfall * area_m2) / 1000
            excess_volume = (excess * area_m2) / 1000
            
            results.append({
                'hora': hour + 1,
                'lluvia_mm': round(rainfall, 2),
                'capacidad_drenaje_mm': drainage_capacity,
                'excedente_mm': round(excess, 2),
                'excedente_acumulado_mm': round(accumulated_excess, 2),
                'volumen_agua_litros': round(volume_liters, 2),
                'excedente_volumen_litros': round(excess_volume, 2),
                'estado': self.get_risk_level(excess)
            })
        
        return pd.DataFrame(results)
    
    def get_risk_level(self, excess):
        """Determina nivel de riesgo según excedente"""
        if excess == 0:
            return 'Normal'
        elif excess < 5:
            return 'Precaución'
        elif excess < 15:
            return 'Alerta'
        elif excess < 30:
            return 'Peligro'
        else:
            return 'Emergencia'
    
    def evaluate_scenario(self, zone_name, scenario_config):
        """
        Evalúa un escenario preventivo
        
        Args:
            zone_name: Nombre de la zona
            scenario_config: Dict con configuración del escenario
                {
                    'hours': 24,
                    'intensity': 'heavy',
                    'drainage_capacity': 10,
                    'area_m2': 1000
                }
        """
        if zone_name not in self.zones_data:
            raise ValueError(f"Zona '{zone_name}' no encontrada")
        
        # Simular lluvia
        rainfall = self.simulate_rainfall(
            zone_name,
            hours=scenario_config.get('hours', 24),
            intensity=scenario_config.get('intensity', 'moderate')
        )
        
        # Calcular excedentes
        results = self.calculate_drainage_excess(
            zone_name,
            rainfall,
            drainage_capacity=scenario_config.get('drainage_capacity', 10),
            area_m2=scenario_config.get('area_m2', 1000)
        )
        
        # Resumen del escenario
        summary = {
            'zona': zone_name,
            'latitud': self.zones_data[zone_name]['latitude'],
            'longitud': self.zones_data[zone_name]['longitude'],
            'total_lluvia_mm': round(rainfall.sum(), 2),
            'lluvia_maxima_mm': round(rainfall.max(), 2),
            'excedente_total_mm': round(results['excedente_acumulado_mm'].iloc[-1], 2),
            'horas_con_excedente': len(results[results['excedente_mm'] > 0]),
            'max_nivel_riesgo': results.loc[results['excedente_mm'].idxmax(), 'estado'],
            'volumen_total_litros': round(results['volumen_agua_litros'].sum(), 2),
            'volumen_excedente_litros': round(results['excedente_volumen_litros'].sum(), 2)
        }
        
        return results, summary
    
    def get_zones_list(self):
        """Retorna lista de zonas disponibles"""
        return list(self.zones_data.keys())
    
    def export_results(self, results, summary, output_file='resultados_simulacion.xlsx'):
        """Exporta resultados a Excel"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Hoja de resumen
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja de resultados detallados
            results.to_excel(writer, sheet_name='Detalle_Horario', index=False)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear modelo
    modelo = DrainageSimulationModel('datos_zonas.xlsx')
    
    # Listar zonas disponibles
    print("Zonas disponibles:", modelo.get_zones_list())
    
    # Configurar escenario
    escenario = {
        'hours': 24,
        'intensity': 'heavy',  # light, moderate, heavy, extreme
        'drainage_capacity': 8.0,  # mm/hora
        'area_m2': 5000  # metros cuadrados
    }
    
    # Evaluar zona
    zona = modelo.get_zones_list()[0]
    resultados, resumen = modelo.evaluate_scenario(zona, escenario)
    
    # Mostrar resumen
    print("\n=== RESUMEN DEL ESCENARIO ===")
    for key, value in resumen.items():
        print(f"{key}: {value}")
    
    # Mostrar primeras horas
    print("\n=== PRIMERAS 6 HORAS ===")
    print(resultados.head(6))
    
    # Exportar resultados
    modelo.export_results(resultados, resumen)