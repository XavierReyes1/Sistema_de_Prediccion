import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import random

def create_sample_excel():
    """
    Crea un archivo Excel de ejemplo con el formato requerido:
    - A1: Ubicación (latitud, longitud)
    - A3, B3: Encabezados de tabla
    - A4+: Datos
    """
    wb = openpyxl.Workbook()
    
    # Eliminar hoja por defecto
    wb.remove(wb.active)
    
    # Zonas de ejemplo en Honduras
    zones = [
        {
            'name': 'Tegucigalpa Centro',
            'lat': 14.0723,
            'lon': -87.1921,
            'capacity': 8.5
        },
        {
            'name': 'Comayagüela Norte',
            'lat': 14.0844,
            'lon': -87.2067,
            'capacity': 7.2
        },
        {
            'name': 'Colonia Kennedy',
            'lat': 14.1094,
            'lon': -87.1767,
            'capacity': 9.0
        },
        {
            'name': 'El Hatillo',
            'lat': 14.0375,
            'lon': -87.1544,
            'capacity': 6.5
        },
        {
            'name': 'San Pedro Sula Centro',
            'lat': 15.5041,
            'lon': -88.0250,
            'capacity': 10.0
        }
    ]
    
    for zone in zones:
        # Crear hoja
        ws = wb.create_sheet(title=zone['name'])
        
        # A1: Ubicación (en formato texto con latitud y longitud)
        location_text = f"Latitud: {zone['lat']}, Longitud: {zone['lon']}"
        ws['A1'] = location_text
        ws['A1'].font = Font(bold=True, size=12, color="0066CC")
        ws['A1'].fill = PatternFill(start_color="E6F2FF", end_color="E6F2FF", fill_type="solid")
        
        # A2: Información adicional
        ws['A2'] = f"Zona: {zone['name']}"
        ws['A2'].font = Font(italic=True, size=10)
        
        # A3, B3: Encabezados
        ws['A3'] = "Capacidad_Drenaje_mm_h"
        ws['B3'] = "Area_Metros_Cuadrados"
        
        # Estilo para encabezados
        for cell in ['A3', 'B3']:
            ws[cell].font = Font(bold=True, color="FFFFFF")
            ws[cell].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            ws[cell].alignment = Alignment(horizontal="center", vertical="center")
        
        # Datos de ejemplo (registros históricos o configuraciones)
        num_records = random.randint(5, 10)
        for i in range(num_records):
            row = 4 + i
            # Capacidad de drenaje varía alrededor de la capacidad base
            capacity = round(zone['capacity'] + random.uniform(-2, 2), 2)
            # Área varía
            area = random.randint(1000, 10000)
            
            ws[f'A{row}'] = capacity
            ws[f'B{row}'] = area
            
            # Alternancia de colores
            if i % 2 == 0:
                for col in ['A', 'B']:
                    ws[f'{col}{row}'].fill = PatternFill(start_color="F2F2F2", 
                                                          end_color="F2F2F2", 
                                                          fill_type="solid")
        
        # Ajustar anchos de columna
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 25
        
        # Agregar notas
        note_row = 4 + num_records + 2
        ws[f'A{note_row}'] = "Notas:"
        ws[f'A{note_row}'].font = Font(bold=True)
        ws[f'A{note_row + 1}'] = "- Estos datos son históricos de la zona"
        ws[f'A{note_row + 2}'] = "- La simulación usa estos valores como referencia"
        
    # Guardar archivo
    filename = 'datos_zonas.xlsx'
    wb.save(filename)
    print(f"✅ Archivo '{filename}' creado exitosamente")
    print(f"📊 Se crearon {len(zones)} hojas con zonas de ejemplo")
    print("\nEstructura de cada hoja:")
    print("  A1: Ubicación (Latitud, Longitud)")
    print("  A2: Información de zona")
    print("  A3, B3: Encabezados (Capacidad_Drenaje_mm_h, Area_Metros_Cuadrados)")
    print("  A4+: Datos históricos/configuración")
    
    return filename

if __name__ == "__main__":
    create_sample_excel()