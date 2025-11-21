from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import os
import requests
from drainage_model import DrainageSimulationModel

app = Flask(__name__)
CORS(app)

DATA_FILE = os.environ.get('DATA_FILE', 'datos.xlsx')
# Si DATA_FILE es una URL pública, descargarla localmente al inicio
if DATA_FILE.startswith('http'):
    r = requests.get(DATA_FILE, timeout=30)
    open('datos.xlsx', 'wb').write(r.content)
    DATA_FILE = 'datos.xlsx'

# Inicializar modelo
modelo = DrainageSimulationModel(DATA_FILE)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Predicción de Drenaje Pluvial</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .panel h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        #map {
            height: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: 600;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        #results {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 15px;
            display: none;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }
        
        .stat-value {
            color: #667eea;
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .risk-normal { background: #4caf50; color: white; }
        .risk-precaucion { background: #ffeb3b; color: #333; }
        .risk-alerta { background: #ff9800; color: white; }
        .risk-peligro { background: #f44336; color: white; }
        .risk-emergencia { background: #b71c1c; color: white; }
        
        #chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-size: 1.2em;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌧️ Sistema de Predicción de Drenaje Pluvial</h1>
        <p class="subtitle">Evaluación de escenarios preventivos ante eventos de lluvia</p>
        
        <div class="grid">
            <div class="panel">
                <h2>📍 Selección de Ubicación</h2>
                <div id="map"></div>
                <div class="form-group" style="margin-top: 20px;">
                    <label>Zona Seleccionada:</label>
                    <select id="zone-select">
                        <option value="">Seleccione una zona...</option>
                    </select>
                </div>
            </div>
            
            <div class="panel">
                <h2>⚙️ Configuración del Escenario</h2>
                
                <div class="form-group">
                    <label>Intensidad de Lluvia:</label>
                    <select id="intensity">
                        <option value="historical" selected>📊 Basada en Datos Históricos</option>
                        <option value="light">Ligera (2-5 mm/h)</option>
                        <option value="moderate">Moderada (5-15 mm/h)</option>
                        <option value="heavy">Fuerte (15-40 mm/h)</option>
                        <option value="extreme">Extrema (30-80 mm/h)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Duración (horas):</label>
                    <input type="number" id="hours" value="24" min="1" max="72">
                </div>
                
                <div class="form-group">
                    <label>Capacidad de Drenaje (mm/h):</label>
                    <input type="number" id="drainage" value="10" min="1" max="50" step="0.5">
                </div>
                
                <div class="form-group">
                    <label>Área de la Zona (m²):</label>
                    <input type="number" id="area" value="5000" min="100" max="100000" step="100">
                </div>
                
                <button class="btn" onclick="runSimulation()">🔍 Ejecutar Simulación</button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            Procesando simulación...
        </div>
        
        <div id="results">
            <h2 style="color: #667eea; margin-bottom: 20px;">📊 Resultados de la Simulación</h2>
            
            <div class="summary-grid" id="summary"></div>
            
            <div id="chart-container">
                <canvas id="resultsChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let chart;
        
        // Inicializar mapa centrado en Honduras
        map = L.map('map').setView([14.0723, -87.1921], 7);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Cargar zonas disponibles
        fetch('/api/zones')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('zone-select');
                data.zones.forEach(zone => {
                    const option = document.createElement('option');
                    option.value = zone.name;
                    option.textContent = zone.name;
                    option.dataset.lat = zone.lat;
                    option.dataset.lon = zone.lon;
                    select.appendChild(option);
                    
                    // Agregar marcador al mapa
                    const marker = L.marker([zone.lat, zone.lon])
                        .addTo(map)
                        .bindPopup(`<b>${zone.name}</b><br>Lat: ${zone.lat}<br>Lon: ${zone.lon}`);
                    
                    marker.on('click', function() {
                        select.value = zone.name;
                    });
                    
                    markers.push(marker);
                });
            });
        
        // Actualizar mapa cuando se selecciona zona
        document.getElementById('zone-select').addEventListener('change', function() {
            const selected = this.options[this.selectedIndex];
            if (selected.dataset.lat && selected.dataset.lon) {
                const lat = parseFloat(selected.dataset.lat);
                const lon = parseFloat(selected.dataset.lon);
                map.setView([lat, lon], 12);
            }
        });
        
        function runSimulation() {
            const zone = document.getElementById('zone-select').value;
            if (!zone) {
                alert('Por favor seleccione una zona');
                return;
            }
            
            const config = {
                intensity: document.getElementById('intensity').value,
                hours: parseInt(document.getElementById('hours').value),
                drainage_capacity: parseFloat(document.getElementById('drainage').value),
                area_m2: parseInt(document.getElementById('area').value)
            };
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    zone: zone,
                    config: config
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Error en el servidor');
                    });
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                console.log('Datos recibidos:', data); // Para debug
                displayResults(data);
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                console.error('Error completo:', error);
                alert('Error en la simulación: ' + error.message);
            });
        }
        
        function displayResults(data) {
            const results = document.getElementById('results');
            results.style.display = 'block';
            
            // Verificar que los datos existan
            if (!data || !data.summary || !data.summary.simulacion) {
                console.error('Datos inválidos:', data);
                alert('Error: Datos de simulación inválidos');
                return;
            }
            
            // Mostrar resumen
            const summary = data.summary;
            const sim = summary.simulacion;
            const hist = summary.datos_historicos || {};
            
            let summaryHTML = `
                <div class="stat-card">
                    <div class="stat-label">Lluvia Total Simulada</div>
                    <div class="stat-value">${sim.total_lluvia_mm || 0} mm</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Excedente Total</div>
                    <div class="stat-value">${sim.excedente_total_mm || 0} mm</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Lluvia Máxima (hora)</div>
                    <div class="stat-value">${sim.lluvia_maxima_mm || 0} mm/h</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Horas con Excedente</div>
                    <div class="stat-value">${sim.horas_con_excedente || 0}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Volumen Total</div>
                    <div class="stat-value">${(sim.volumen_total_litros || 0).toLocaleString()} L</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Nivel de Riesgo</div>
                    <div class="risk-badge risk-${(sim.max_nivel_riesgo || 'normal').toLowerCase()}">${sim.max_nivel_riesgo || 'Normal'}</div>
                </div>
            `;
            
            // Agregar estadísticas históricas si existen
            if (hist.total_dias && hist.total_dias > 0) {
                summaryHTML += `
                    <div class="stat-card" style="grid-column: span 2; background: #e3f2fd;">
                        <div class="stat-label">📊 Datos Históricos (${hist.total_dias} días)</div>
                        <div style="font-size: 0.9em; margin-top: 10px;">
                            Lluvia total: ${hist.lluvia_total_historica || 0} mm<br>
                            Promedio: ${hist.lluvia_promedio_historica || 0} mm/día<br>
                            Máximo registrado: ${hist.lluvia_maxima_historica || 0} mm
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('summary').innerHTML = summaryHTML;
            
            // Crear gráfico
            createChart(data.hourly);
            
            // Scroll a resultados
            results.scrollIntoView({ behavior: 'smooth' });
        }
        
        function createChart(hourlyData) {
            const ctx = document.getElementById('resultsChart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hourlyData.map(d => `Hora ${d.hora}`),
                    datasets: [
                        {
                            label: 'Lluvia (mm)',
                            data: hourlyData.map(d => d.lluvia_mm),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Capacidad Drenaje (mm)',
                            data: hourlyData.map(d => d.capacidad_drenaje_mm),
                            borderColor: '#4caf50',
                            borderDash: [5, 5],
                            fill: false
                        },
                        {
                            label: 'Excedente Acumulado (mm)',
                            data: hourlyData.map(d => d.excedente_acumulado_mm),
                            borderColor: '#f44336',
                            backgroundColor: 'rgba(244, 67, 54, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Análisis Horario de Lluvia y Drenaje',
                            font: {
                                size: 16
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Milímetros (mm)'
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/zones')
def get_zones():
    zones = []
    for name, data in modelo.zones_data.items():
        zones.append({
            'name': name,
            'lat': data['latitude'],
            'lon': data['longitude']
        })
    return jsonify({'zones': zones})

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        zone = data['zone']
        config = data['config']
        
        results, summary = modelo.evaluate_scenario(zone, config)
        
        # Aplanar el resumen para facilitar el acceso en JavaScript
        response = {
            'summary': {
                'zona': summary['zona'],
                'latitud': summary['latitud'],
                'longitud': summary['longitud'],
                'datos_historicos': summary['datos_historicos'],
                'simulacion': summary['simulacion']
            },
            'hourly': results.to_dict('records')
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)