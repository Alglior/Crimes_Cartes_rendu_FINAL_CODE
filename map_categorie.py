import pandas as pd
import folium 
import os
from datetime import datetime
import branca.colormap as cm
import json
import plotly.express as px
import plotly.io as pio
from folium import plugins
import plotly.graph_objs as go

def create_crime_trend_graph(df, country):
    """
    Create a single HTML file for crime trends per country across all years
    
    Args:
        df: DataFrame with crime data
        country: Name of the country
    
    Returns:
        str: HTML content for the trends visualization
    """
    # Prepare the data by grouping by country and year
    country_data = df[df['NAME'] == country].copy()
    # Sort by year to ensure chronological order
    country_data = country_data.sort_values('Year')
    
    # Convert to list of dictionaries for JSON serialization
    data_list = []
    for year in country_data['Year'].unique():
        year_data = country_data[country_data['Year'] == year]
        row = {'year': int(year)}
        for _, crime_row in year_data.iterrows():
            crime_type = crime_row['Crime Type']
            value = crime_row['Value']
            row[crime_type] = float(value) if pd.notna(value) else None
        data_list.append(row)
        
    categories = {
        'Crimes violents': ['Homicide intentionnel', "Tentative d'homicide volontaire", 'Attaque grave',
                           'Violence sexuelle', 'Agression sexuelle', 'Viol', 'Exploitation sexuelle'],
        'Crimes contre la propriété': ['Vol', 'Vol par effraction', 'Vol par effraction de résidences privées',
                                     "Vol d'un véhicule motorisé ou de pièces de celui-ci", 'Vol qualifié', 'Fraude'],
        'Crime organisé': ['Participation à un groupe criminel organisé', "Blanchiment d'argent",
                          'Corruption', 'Actes illicites impliquant des drogues ou des précurseurs contrôlés'],
        'Cyber et autres': ['Actes contre les systèmes informatiques', 'Pédopornographie', 'Enlèvement', 'pots-de-vin']
    }

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crime Trends - {country}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            :root {{
                --primary-color: #3b82f6;
                --primary-hover: #2563eb;
                --background-color: #f8fafc;
                --border-color: #e2e8f0;
                --text-color: #1e293b;
                --shadow-color: rgba(0, 0, 0, 0.06);
                --transition-speed: 0.3s;
            }}
            
            body, html {{ 
                margin: 0; 
                padding: 0; 
                height: 100%; 
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            
            .container {{ 
                width: 100%; 
                height: 100vh; 
                display: flex; 
                flex-direction: column; 
                padding: 24px; 
                box-sizing: border-box; 
                gap: 24px;
                max-width: 2560px;
                margin: 0 auto;
            }}
            
            .controls {{ 
                background: white; 
                padding: 24px; 
                border-radius: 16px; 
                box-shadow: 0 4px 6px var(--shadow-color);
                transition: all var(--transition-speed);
            }}
            
            .controls:hover {{
                box-shadow: 0 6px 12px var(--shadow-color);
            }}
            
            .controls-row {{
                display: flex;
                align-items: center;
                gap: 24px;
                flex-wrap: wrap;
            }}
            
            .view-controls {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            
            .content {{
                flex: 1;
                min-height: 0;
                overflow: auto;
                padding-right: 20px;
                scrollbar-width: thin;
                scrollbar-color: var(--primary-color) var(--background-color);
            }}
            
            .content::-webkit-scrollbar {{
                width: 8px;
            }}
            
            .content::-webkit-scrollbar-track {{
                background: var(--background-color);
            }}
            
            .content::-webkit-scrollbar-thumb {{
                background-color: var(--primary-color);
                border-radius: 4px;
            }}
            
            .category-section {{
                background: white;
                border-radius: 16px;
                padding: 32px;
                margin-bottom: 24px;
                box-shadow: 0 4px 6px var(--shadow-color);
                transition: all var(--transition-speed);
            }}
            
            .category-section:hover {{
                box-shadow: 0 6px 12px var(--shadow-color);
            }}
            
            .category-title {{
                font-size: 1.75rem;
                font-weight: 600;
                margin-bottom: 24px;
                padding-bottom: 16px;
                border-bottom: 2px solid var(--border-color);
                color: var(--text-color);
            }}
            
            .charts-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                gap: 32px;
            }}
            
            .chart-wrapper {{ 
                background: white;
                border-radius: 12px;
                padding: 24px;
                height: 600px;
                position: relative;
                transition: all var(--transition-speed);
            }}
            
            .chart-wrapper:hover {{
                box-shadow: 0 6px 12px var(--shadow-color);
            }}
            
            .chart-container {{
                position: absolute;
                top: 24px;
                left: 24px;
                right: 24px;
                bottom: 24px;
            }}
            
            select {{ 
                padding: 10px 16px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
                font-size: 15px;
                background: white;
                cursor: pointer;
                transition: all var(--transition-speed);
                color: var(--text-color);
                min-width: 160px;
            }}
            
            select:hover {{
                border-color: var(--primary-color);
            }}
            
            select:focus {{
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            .radio-group {{
                display: flex;
                gap: 20px;
                align-items: center;
            }}
            
            .radio-label {{
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                font-size: 15px;
                transition: all var(--transition-speed);
            }}
            
            .radio-label:hover {{
                color: var(--primary-color);
            }}
            
            .category-buttons {{ 
                display: flex; 
                gap: 16px; 
                flex-wrap: wrap;
                margin-top: 20px;
            }}
            
            button {{ 
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
                background: white;
                color: var(--text-color);
                font-size: 15px;
                cursor: pointer;
                transition: all var(--transition-speed);
                font-weight: 500;
            }}
            
            button:hover {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            button.active {{ 
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            @media (min-width: 2000px) {{
                .charts-grid {{
                    grid-template-columns: repeat(3, 1fr);
                }}
                
                .chart-wrapper {{
                    height: 600px;
                }}
            }}
            
            @media (max-width: 1400px) {{
                .charts-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}
            
            @media (max-width: 1200px) {{
                .charts-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 16px;
                }}
                
                .controls {{
                    padding: 20px;
                }}
                
                .chart-wrapper {{
                    height: 400px;
                }}
                
                .category-title {{
                    font-size: 1.5rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="controls">
                <div class="controls-row">
                    <select id="chartType" aria-label="Chart Type">
                        <option value="lines+markers">Graphique linéaire</option>
                        <option value="bar">Diagramme à barres</option>
                    </select>
                    
                    <div class="view-controls">
                        <div class="radio-group" role="radiogroup" aria-label="View Type">
                            <label class="radio-label">
                                <input type="radio" name="view" value="category" checked>
                                Vue des catégories
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="view" value="individuel">
                                Crimes individuels
                            </label>
                        </div>
                    </div>
                </div>
                 
                <div class="category-buttons" id="categoryButtons" role="toolbar" aria-label="Crime Categories">  <button onclick="window.location.href='index.html'" class="button outline">
                    <i class="fas fa-arrow-left"></i> Retour à la carte
                </button></div>
                              
            </div>
            
            <div class="content">
                <div id="categoryView">
                    <div class="chart-wrapper">
                        <div id="mainChart" class="chart-container"></div>
                    </div>
                </div>
                
                <div id="individualView" style="display: none;">
                </div>
            </div>
        </div>
        
        <script>
            // Initialize data and state
            const data = {json.dumps(data_list)};
            const categories = {json.dumps(categories)};
            let currentCategory = Object.keys(categories)[0];
            let currentType = 'lines+markers';
            
            
function createLayout(title) {{
  return {{
    title: {{
      text: title,
      font: {{
        size: 20,
        color: '#1e293b',
        weight: 600
      }}
    }},
    autosize: true,
    margin: {{ t: 60, l: 70, r: 150, b: 60 }},
    plot_bgcolor: 'white',
    paper_bgcolor: 'white',
    yaxis: {{
      title: 'Rate per 100,000 inhabitants',
      zeroline: true,
      zerolinecolor: '#94a3b8',
      zerolinewidth: 1,
      gridcolor: '#f1f5f9',
      titlefont: {{ size: 16 }},
      tickfont: {{ size: 14 }},
      tickformat: '.1f'
    }},
    xaxis: {{
      title: 'Year',
      showspikes: true,
      spikemode: 'across',
      spikesnap: 'cursor',
      spikecolor: '#94a3b8',
      spikethickness: 2,
      gridcolor: '#f1f5f9',
      titlefont: {{ size: 16 }},
      tickfont: {{ size: 14 }}
    }},
    hovermode: 'x unified',  // Back to unified mode
    hoverlabel: {{
      align: 'left',
      bgcolor: 'white',  // Solid white background
      bordercolor: '#64748b',  // Darker border
      borderwidth: 1,
      font: {{ 
        size: 13,
        color: '#1e293b'  // Darker text
      }},
      namelength: -1
    }},
    showlegend: true,
    legend: {{
      font: {{ size: 12 }},
      bgcolor: 'rgba(255,255,255,0.9)',
      bordercolor: '#e2e8f0',
      borderwidth: 1,
      borderradius: 4
    }},
    transition: {{
      duration: 500,
      easing: 'cubic-in-out'
    }}
  }};
}}

function createTrace(crime) {{
  const trace = {{
    x: data.map(d => d.year),
    y: data.map(d => d[crime]),
    name: crime,
    type: currentType === 'lines+markers' ? 'scatter' : 'bar',
    hovertemplate: `<b>${{crime}}</b>: %{{y:.1f}}<extra></extra>`,  // Bold crime name
    opacity: 0.9,
  }};

  if (currentType === 'lines+markers') {{
    trace.mode = 'lines+markers';
    trace.line = {{
      width: 3,
      shape: 'spline',
      smoothing: 1.3
    }};
    trace.marker = {{
      size: 8,
      symbol: 'circle',
    }};
    trace.connectgaps = true;
  }} else {{
    trace.marker = {{
      line: {{
        width: 1,
        color: 'white'
      }}
    }};
  }}

  return trace;
}}
            
            // Rest of the JavaScript remains the same, just add the new configs
            
            // Create buttons with smooth transitions
            function createButtons() {{
                const container = document.getElementById('categoryButtons');
                Object.keys(categories).forEach(category => {{
                    const btn = document.createElement('button');
                    btn.textContent = category;
                    btn.onclick = () => updateCurrentCategory(category);
                    if (category === currentCategory) btn.className = 'active';
                    container.appendChild(btn);
                }});
            }}
            
            // Add smooth transitions for view changes
            function handleViewChange(view) {{
                const categoryView = document.getElementById('categoryView');
                const individualView = document.getElementById('individualView');
                
                categoryView.style.transition = 'opacity 0.3s ease-in-out';
                individualView.style.transition = 'opacity 0.3s ease-in-out';
                
                if (view === 'category') {{
                    individualView.style.opacity = 0;
                    setTimeout(() => {{
                        individualView.style.display = 'none';
                        categoryView.style.display = 'block';
                        setTimeout(() => {{
                            categoryView.style.opacity = 1;
                            updateCategoryView();
                        }}, 50);
                    }}, 300);
                }} else {{
                    categoryView.style.opacity = 0;
                    setTimeout(() => {{
                        categoryView.style.display = 'none';
                        individualView.style.display = 'block';
                        setTimeout(() => {{
                            individualView.style.opacity = 1;
                            updateIndividualView();
                        }}, 50);
                    }}, 300);
                }}
                
                localStorage.setItem('preferredView', view);
            }}
            
            // Initialize event listeners and state
            window.addEventListener('load', () => {{
                const savedChartType = localStorage.getItem('preferredChartType');
                const savedView = localStorage.getItem('preferredView');
                const savedCategory = localStorage.getItem('preferredCategory');
                
                // Enhanced initialization with smooth transitions
                document.body.style.opacity = '0';
                
                // Set chart type with animation
                if (savedChartType) {{
                    currentType = savedChartType;
                    document.getElementById('chartType').value = savedChartType;
                }}
                
                // Set view with animation
                if (savedView) {{
                    const viewRadio = document.querySelector(`input[name="view"][value="${{savedView}}"]`);
                    if (viewRadio) {{
                        viewRadio.checked = true;
                    }}
                }}
                
                // Set category
                if (savedCategory && categories[savedCategory]) {{
                    currentCategory = savedCategory;
                }}
                
                createButtons();
                
                // Fade in the entire interface
                requestAnimationFrame(() => {{
                    document.body.style.transition = 'opacity 0.5s ease-in-out';
                    document.body.style.opacity = '1';
                    handleViewChange(savedView || 'category');
                }});
            }});
            
            // Enhanced chart type update with smooth transitions
            function updateChartType(newType) {{
                const oldType = currentType;
                currentType = newType;
                
                const view = document.querySelector('input[name="view"]:checked').value;
                
                // Add transition animation
                Plotly.animate('mainChart', {{
                    data: [],
                    layout: {{}}
                }}, {{
                    transition: {{
                        duration: 500,
                        easing: 'cubic-in-out'
                    }},
                    frame: {{
                        duration: 500
                    }}
                }}).then(() => {{
                    if (view === 'category') {{
                        updateCategoryView();
                    }} else {{
                        updateIndividualView();
                    }}
                }});
                
                localStorage.setItem('preferredChartType', newType);
            }}
            
            // Enhanced category update with smooth transitions
            function updateCurrentCategory(category) {{
                const oldCategory = currentCategory;
                currentCategory = category;
                
                // Animate button transitions
                document.querySelectorAll('.category-buttons button').forEach(btn => {{
                    if (btn.textContent === category) {{
                        btn.classList.add('active');
                        btn.style.transform = 'scale(1.05)';
                        setTimeout(() => btn.style.transform = 'scale(1)', 200);
                    }} else {{
                        btn.classList.remove('active');
                    }}
                }});
                
                const view = document.querySelector('input[name="view"]:checked').value;
                
                // Add fade transition
                const content = document.querySelector('.content');
                content.style.opacity = '0';
                
                setTimeout(() => {{
                    if (view === 'category') {{
                        updateCategoryView();
                    }} else {{
                        updateIndividualView();
                    }}
                    content.style.transition = 'opacity 0.3s ease-in-out';
                    content.style.opacity = '1';
                }}, 300);
                
                localStorage.setItem('preferredCategory', category);
            }}
            
            // Enhanced category view update with improved animations
            function updateCategoryView() {{
                const crimes = categories[currentCategory];
                const traces = crimes.map(createTrace);
                
                const layout = createLayout(`Crime Trends in {country} - ${{currentCategory}}`);
                
                Plotly.newPlot('mainChart', traces, layout, {{ 
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                    toImageButtonOptions: {{
                        format: 'png',
                        filename: `crime_trends_{country}_${{currentCategory}}`,
                        height: 800,
                        width: 1200,
                        scale: 2
                    }}
                }});
            }}
            
            // Enhanced individual view update with improved animations
            function updateIndividualView() {{
                const container = document.getElementById('individualView');
                container.innerHTML = '';
                container.style.opacity = '0';
                
                const crimes = categories[currentCategory];
                const section = document.createElement('div');
                section.className = 'category-section';
                
                const title = document.createElement('div');
                title.className = 'category-title';
                title.textContent = currentCategory;
                section.appendChild(title);
                
                const grid = document.createElement('div');
                grid.className = 'charts-grid';
                
                crimes.forEach((crime, index) => {{
                    const wrapper = document.createElement('div');
                    wrapper.className = 'chart-wrapper';
                    wrapper.style.opacity = '0';
                    wrapper.style.transform = 'translateY(20px)';
                    
                    const chartDiv = document.createElement('div');
                    chartDiv.id = `chart_${{crime.replace(/ /g, '_')}}`;
                    chartDiv.className = 'chart-container';
                    wrapper.appendChild(chartDiv);
                    grid.appendChild(wrapper);
                    
                    const trace = createTrace(crime);
                    
                    // Stagger the animation of individual charts
                    setTimeout(() => {{
                        Plotly.newPlot(chartDiv, [trace],
                            createLayout(crime),
                            {{ 
                                responsive: true,
                                displayModeBar: false,
                                displaylogo: false
                            }}
                        );
                        
                        wrapper.style.transition = 'all 0.5s ease-in-out';
                        wrapper.style.opacity = '1';
                        wrapper.style.transform = 'translateY(0)';
                    }}, index * 100);
                }});
                
                section.appendChild(grid);
                container.appendChild(section);
                
                // Fade in the container
                requestAnimationFrame(() => {{
                    container.style.transition = 'opacity 0.5s ease-in-out';
                    container.style.opacity = '1';
                }});
            }}
            
            // Enhanced resize handler with debounce
            let resizeTimeout;
            window.addEventListener('resize', () => {{
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {{
                    const view = document.querySelector('input[name="view"]:checked').value;
                    if (view === 'category') {{
                        updateCategoryView();
                    }} else {{
                        updateIndividualView();
                    }}
                }}, 250);
            }});
            
            // Add smooth transitions for color theme changes
            function updateColorTheme(isDark) {{
                document.documentElement.style.transition = 'all 0.3s ease-in-out';
                if (isDark) {{
                    document.documentElement.style.setProperty('--background-color', '#1a1a1a');
                    document.documentElement.style.setProperty('--text-color', '#ffffff');
                    document.documentElement.style.setProperty('--border-color', '#333333');
                }} else {{
                    document.documentElement.style.setProperty('--background-color', '#f8fafc');
                    document.documentElement.style.setProperty('--text-color', '#1e293b');
                    document.documentElement.style.setProperty('--border-color', '#e2e8f0');
                }}
            }}
            
            // Initialize chart type change listener
            document.getElementById('chartType').addEventListener('change', (e) => {{
                updateChartType(e.target.value);
            }});
            
            // Initialize view change listeners
            document.querySelectorAll('input[name="view"]').forEach(radio => {{
                radio.addEventListener('change', (e) => handleViewChange(e.target.value));
            }});
        </script>
    </body>
    </html>
    """
    return html_template

def get_crime_categories():
    """Define and return crime categories with their properties"""
    return {
        'Tous les crimes': None,  # Changed from 'Tous les crimes'
        'Crimes violents': {     # Changed from 'Violent Crimes'
            'color': '#cc0000',
            'crimes': ['Homicide intentionnel', "Tentative d'homicide volontaire", 'Attaque grave',
                      'Violence sexuelle', 'Agression sexuelle', 'Viol', 'Exploitation sexuelle']
        },
        'Crimes contre la propriété': {  # Changed from 'Property Crimes'
            'color': '#006600',
            'crimes': ['Vol', 'Vol par effraction', 'Vol par effraction de résidences privées',
                      "Vol d'un véhicule motorisé ou de pièces de celui-ci", 'Vol qualifié', 'Fraude']
        },
        'Crime organisé': {      # Changed from 'Organized Crime'
            'color': '#0000cc',
            'crimes': ['Participation à un groupe criminel organisé', "Blanchiment d'argent",
                      'Corruption', 'Actes illicites impliquant des drogues ou des précurseurs contrôlés']
        },
        'Cyber et autres': {     # Changed from 'Cyber & Other'
            'color': '#cc6600',
            'crimes': ['Actes contre les systèmes informatiques', 'Pédopornographie', 'Enlèvement', 'pots-de-vin']
        }
    }

def create_crime_category_mapping(categories):
    """Create mapping of individual crimes to their categories"""
    mapping = {}
    for cat_name, cat_info in categories.items():
        if cat_info is not None:
            for crime in cat_info['crimes']:
                mapping[crime] = cat_name
    return mapping

def process_year_data(df, year):
    """Process and clean data for a specific year"""
    year_data = df[df['Year'] == year].copy()
    numeric_columns = ['Value', 'lat', 'lon']
    for col in numeric_columns:
        year_data[col] = pd.to_numeric(year_data[col], errors='coerce')
    return year_data

def create_base_map(year_data, categories):
    """Create and return base map with dynamic colormaps for each category"""
    # Create map without tiles
    m = folium.Map(location=[48, 2], zoom_start=4, tiles=None)
    
    # Add GeoJSON layer with blue styling as the base layer
    geojson_style = {
        'fillColor': '#e6f3ff',  # Light blue fill
        'color': '#3182bd',      # Medium blue border
        'weight': 1,
        'fillOpacity': 0.3
    }
    
    # Create GeoJSON layer with custom style function
    geojson = folium.GeoJson(
        'europe.geojson',
        name='Europe',
        style_function=lambda x: geojson_style,
        tooltip=None,
        popup=None,
        overlay=False  # This makes it a base layer
    )
    
    # Add custom JavaScript to ensure GeoJSON stays visible
    custom_geojson_style = """
    <style>
    .leaflet-pane.leaflet-overlay-pane {
        z-index: 400 !important;
    }
    .leaflet-pane.leaflet-marker-pane {
        z-index: 600 !important;
    }
    .leaflet-pane.leaflet-popup-pane {
        z-index: 700 !important;
    }
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Ensure GeoJSON layer is always visible
        setTimeout(function() {
            var geojsonLayer = document.querySelector('.leaflet-layer:first-child');
            if (geojsonLayer) {
                geojsonLayer.style.display = 'block';
                geojsonLayer.style.zIndex = '1';
            }
        }, 100);
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(custom_geojson_style))
    geojson.add_to(m)
    
    return m

def calculate_category_totals(country_data, categories):
    """Calculate totals for each crime category"""
    totals = {}
    for cat_name, cat_info in categories.items():
        if cat_info is not None:
            cat_data = country_data[country_data['Crime Type'].isin(cat_info['crimes'])]
            total = cat_data['Value'].sum()
            totals[cat_name] = 'NA' if pd.isna(total) else total
    return totals

def create_category_popup_content(country, year, crimes, total, graph_file, category):
    """Generate HTML content for popup with table/graph toggle and sorted data"""
    total_display = "NA" if total == 'NA' or pd.isna(total) else f"{total:.2f}"
    
    # Prépare les données pour le graphique avec gestion des erreurs
    data_rows = []
    for crime in crimes:
        if pd.notna(crime['Value']):
            try:
                value = float(crime['Value'])
                if value >= 0:  # Vérifie que la valeur est valide
                    data_rows.append({
                        'type': crime['Crime Type'],
                        'value': value
                    })
            except (ValueError, TypeError):
                continue
    
    # Trie les données par valeur croissante
    data_rows.sort(key=lambda x: x['value'])
    
    # Création du HTML pour le graphique
    graph_html = """
        <div class="chart-container">
    """
    
    # Trouve la valeur maximum pour l'échelle avec gestion des erreurs
    try:
        if data_rows:  # Vérifie si nous avons des données valides
            max_value = max(crime['value'] for crime in data_rows)
            
            # Si max_value est 0, on évite la division par zéro
            if max_value == 0:
                max_value = 1
                
            for row in data_rows:
                percentage = (row['value'] / max_value) * 100
                graph_html += f"""
                    <div class="chart-row">
                        <div class="chart-label" title="{row['type']}">{row['type']}</div>
                        <div class="chart-bar-container">
                            <div class="chart-bar" style="width: {percentage}%">
                                <span class="chart-value">{row['value']:.2f}</span>
                            </div>
                        </div>
                    </div>
                """
        else:
            graph_html += """
                <div class="no-data-message">
                    Aucune donnée disponible pour ce graphique
                </div>
            """
    except Exception as e:
        graph_html += f"""
            <div class="error-message">
                Erreur lors de la génération du graphique: {str(e)}
            </div>
        """
    
    graph_html += "</div>"
    
    popup_content = f"""
    <style>
        .popup-container {{
            min-width: 600px;
            max-width: 90vw;
            max-height: 80vh;
            overflow-y: auto;
            background: white;
            position: relative;
            padding: 16px;
            box-sizing: border-box;
        }}
        
        .view-toggle {{
            background-color: #6495ED;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            cursor: pointer;
            margin: 10px 0;
            width: 100%;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .view-toggle:hover {{
            background-color: #2F4F4F;
        }}
        
        .no-data-message, .error-message {{
            text-align: center;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 4px;
            margin: 10px 0;
            color: #666;
        }}
        
        .error-message {{
            background-color: #fff3f3;
            color: #d32f2f;
        }}
        
        .chart-container {{
            margin-top: 20px;
            transition: all 0.3s ease;
        }}
        
        .chart-row {{
            display: flex;
            margin-bottom: 16px;  /* Increased from 12px */
            align-items: center;
            animation: fadeIn 0.5s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .chart-label {{
            width: 150px;
            padding-right: 10px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
        }}
        
        .chart-bar-container {{
            flex-grow: 1;
            background-color: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .chart-bar {{
            background-color: #2196F3;
            height: 24px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            color: white;
            font-size: 12px;
            transition: width 0.6s ease;
            min-width: 40px;
            position: relative;
        }}
        
        .chart-value {{
            margin-left: auto;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }}
        
        #graphView, #tableView {{
            display: none;
        }}
        
        #graphView.active, #tableView.active {{
            display: block;
        }}
        
        .button-container {{
            display: flex;
            gap: 12px;
            margin: 15px 0;
            flex-wrap: wrap;
        }}
        
        .popup-button {{
            padding: 8px 16px;
            border: none;
            cursor: pointer;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 140px;
        }}
        
        .trends-button {{
            background-color: #4CAF50;
            color: white;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .data-table th {{
            background-color: #f0f0f0;
        }}
        
        @media screen and (max-width: 480px) {{
            .button-container {{
                flex-direction: column;
            }}
            
            .popup-button {{
                width: 100%;
            }}
            
            .chart-label {{
                width: 100px;
            }}
            
            .chart-value {{
                font-size: 11px;
            }}
        }}
    </style>
    
    <div class="popup-container">
        <div class="popup-header">
            <h4 style="margin: 0 0 5px 0;">{country} - {year}</h4>
            <h5 style="margin: 0;">{category}</h5>
            <p style="margin: 5px 0;"><strong>Taux total:</strong> {total_display}</p>
        </div>
        
        <div class="button-container">
            <button onclick="window.open('{graph_file}', '_blank')"
                    class="popup-button trends-button">
                Voir les tendances
            </button>
            <button id="rankingsButton" 
                    onclick="window.open('rankings.html', '_blank')"
                    class="popup-button">
                Voir les classements européens
            </button>
        </div>
        
        <button onclick="document.getElementById('graphView').classList.toggle('active');
                        document.getElementById('tableView').classList.toggle('active');
                        this.textContent = this.textContent.includes('graphique') ? 
                            'Voir le tableau' : 'Voir le graphique';"
                class="view-toggle">
            Voir le graphique
        </button>
        
        <div id="tableView" class="active">
            <table class="data-table">
                <tr>
                    <th>Type de crime</th>
                    <th>Taux</th>
                </tr>
    """
    
    # Affichage du tableau
    has_data = False
    for crime in crimes:
        try:
            value_display = "NA" if pd.isna(crime['Value']) else f"{float(crime['Value']):.2f}"
            popup_content += f"""
                <tr>
                    <td>{crime['Crime Type']}</td>
                    <td>{value_display}</td>
                </tr>
            """
            if value_display != "NA":
                has_data = True
        except (ValueError, TypeError):
            popup_content += f"""
                <tr>
                    <td>{crime['Crime Type']}</td>
                    <td>NA</td>
                </tr>
            """
    
    if not has_data:
        popup_content += """
                <tr>
                    <td colspan="2" style="text-align: center;">Aucune donnée disponible</td>
                </tr>
        """
    
    popup_content += f"""
            </table>
        </div>
        <div id="graphView">
            {graph_html}
        </div>
    </div>
    """
    
    return popup_content

def create_crime_distribution_html(country, year, data):
    """Create an HTML page for crime distribution visualization"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Crime Distribution - {country} {year}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 15px;
            font-family: system-ui, -apple-system, sans-serif;
            background: white;
        }}
        .chart-container {{
            width: 100%;
            margin-bottom: 20px;
        }}
        select {{
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        h2 {{
            margin: 0 0 15px 0;
            font-size: 16px;
            color: #333;
        }}
    </style>
</head>
<body>
    <h2>{country} Crime Distribution ({year})</h2>
    <select id="chartTypeSelect" onchange="updateChartType()">
        <option value="all">Tous les crimes</option>
        <option value="violent">Crimes violents</option>
        <option value="property">Crimes contre la propriété</option>
        <option value="organized">Crime organisé</option>
        <option value="cyber">Cyber et autres</option>
    </select>
    <div id="chartContainer"></div>

    <script>
        const crimeData = {json.dumps(data)};
        
        function getCrimeCategory(crimeType) {{
            const categories = {{
                violent: ['Homicide intentionnel', "Tentative d'homicide volontaire", 'Attaque grave',
                         'Violence sexuelle', 'Agression sexuelle', 'Viol', 'Exploitation sexuelle'],
                property: ['Vol', 'Vol par effraction', 'Vol par effraction de résidences privées',
                         "Vol d'un véhicule motorisé ou de pièces de celui-ci", 'Vol qualifié', 'Fraude'],
                organized: ['Participation à un groupe criminel organisé', "Blanchiment d'argent",
                          'Corruption', 'Actes illicites impliquant des drogues ou des précurseurs contrôlés'],
                cyber: ['Actes contre les systèmes informatiques', 'Pédopornographie', 'Enlèvement', 'pots-de-vin']
            }};
            
            for (const [category, crimes] of Object.entries(categories)) {{
                if (crimes.includes(crimeType)) {{
                    return category;
                }}
            }}
            return 'other';
        }}
        
        function createBarChart(data) {{
            data = [...data].sort((a, b) => b.value - a.value);
            
            const layout = {{
                height: Math.max(300, data.length * 30),
                margin: {{ t: 20, b: 50, l: 200, r: 40 }},
                xaxis: {{
                    title: 'Taux pour 100,000 habitants',
                    tickformat: '.1f'
                }},
                yaxis: {{
                    ticktext: data.map(d => d.type),
                    tickvals: data.map((_, i) => i),
                    tickmode: 'array',
                    type: 'category'
                }},
                showlegend: false,
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};

            const plotData = [{{
                type: 'bar',
                x: data.map(d => d.value),
                y: data.map(d => d.type),
                orientation: 'h',
                marker: {{
                    color: '#2196F3',
                    opacity: 0.8
                }},
                text: data.map(d => d.value.toFixed(1)),
                textposition: 'outside',
                hoverinfo: 'x+text'
            }}];

            return {{ data: plotData, layout: layout }};
        }}
        
        function updateChartType() {{
            const selectedType = document.getElementById('chartTypeSelect').value;
            let chartData;
            
            if (selectedType === 'all') {{
                chartData = crimeData;
            }} else {{
                chartData = crimeData.filter(d => getCrimeCategory(d.type) === selectedType);
            }}
            
            if (chartData.length === 0) {{
                document.getElementById('chartContainer').innerHTML = 
                    '<div style="text-align: center; padding: 20px;">Aucune donnée disponible pour la catégorie sélectionnée</div>';
                return;
            }}
            
            const {{ data, layout }} = createBarChart(chartData);
            
            Plotly.newPlot('chartContainer', data, layout, {{
                responsive: true,
                displayModeBar: false
            }});
        }}
        
        // Initial chart creation
        updateChartType();
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            updateChartType();
        }});
    </script>
</body>
</html>"""

def create_category_control(categories):
    """Create enhanced HTML for category control panel"""
    control = """
    <div id='category-control' style='
        position: absolute;
        top: 10px;
        right: 10px;
        background: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        z-index: 1000;
    '>
        <h4 style='margin: 0 0 10px 0;'>Crime Categories</h4>
        <div id='category-buttons' style='display: flex; flex-direction: column; gap: 5px;'>
    """
    
    for cat_name, cat_info in categories.items():
        color = cat_info['color'] if cat_info else '#333333'
        control += f"""
            <label style='display: flex; align-items: center; gap: 5px;'>
                <input type='radio' name='category' value='{cat_name}' 
                       {'checked' if cat_name == 'Tous les crimes' else ''}>
                <span style='color: {color};'>{cat_name}</span>
            </label>
        """
    
    control += """
        </div>

    </div>
    """
    
    return control

def get_enhanced_interactive_js():
    """Return enhanced JavaScript code for map interactivity with dynamic sizing and legend"""
    return """
    document.addEventListener('DOMContentLoaded', function() {
        const openedPopups = new Set();
        let currentCategory = 'Tous les crimes';
        
        // Initialize legend visibility
        function updateLegendVisibility(category) {
            const legends = document.querySelectorAll('.leaflet-control.legend');
            legends.forEach(legend => {
                const legendText = legend.querySelector('div').textContent;
                const isMatch = legendText.startsWith(category);
                legend.style.display = isMatch ? 'block' : 'none';
            });
        }
        
        function updateMarkerSize(marker, value) {
            const minRadius = 5;
            const maxRadius = 20;
            let radius = minRadius;
            
            if (value !== 'NA' && !isNaN(value)) {
                radius = Math.min(maxRadius, Math.max(minRadius, value/100));
            }
            
            const circleElement = marker.querySelector('path');
            if (circleElement) {
                const d = circleElement.getAttribute('d');
                if (d) {
                    const newD = d.replace(/\d+(\.\d+)?(?=\s*Z$)/, radius);
                    circleElement.setAttribute('d', newD);
                }
            }
        }
        
        function updateMarkers(category) {
            document.querySelectorAll('.crime-marker').forEach(marker => {
                try {
                    const markerData = marker.querySelector('.marker-data');
                    if (!markerData) return;
                    
                    const categoriesStr = markerData.dataset.categories;
                    const colorsStr = markerData.dataset.colors;
                    if (!categoriesStr || !colorsStr) return;
                    
                    const categories = {};
                    categoriesStr.split(';').forEach(item => {
                        const [key, value] = item.split(':');
                        if (key) {
                            categories[key] = value;
                        }
                    });
                    
                    const colors = {};
                    colorsStr.split(';').forEach(item => {
                        const [key, value] = item.split(':');
                        if (key) {
                            colors[key] = value;
                        }
                    });
                    
                    if (category === 'Tous les crimes') {
                        const totalValue = markerData.dataset.total;
                        updateMarkerSize(marker, totalValue);
                        marker.style.opacity = '1';
                    } else {
                        const categoryValue = categories[category];
                        updateMarkerSize(marker, categoryValue);
                        marker.style.opacity = (categoryValue && categoryValue !== 'NA') ? '1' : '0.2';
                        
                        const categoryColor = colors[category];
                        if (categoryColor) {
                            const circleElement = marker.querySelector('path');
                            if (circleElement) {
                                circleElement.style.fill = categoryColor;
                            }
                        }
                    }
                    
                } catch (error) {
                    console.error('Error updating marker:', error);
                    marker.style.opacity = '1';
                }
            });
            
            // Update legend visibility
            updateLegendVisibility(category);
        }
        
        // Add event listeners for category selection
        document.querySelectorAll('input[name="category"]').forEach(radio => {
            radio.addEventListener('change', function() {
                currentCategory = this.value;
                updateMarkers(currentCategory);
            });
        });
        
        // Initialize with default category
        const initialCategory = document.querySelector('input[name="category"]:checked').value;
        updateMarkers(initialCategory);
        
        // Call initial legend update
        updateLegendVisibility('Tous les crimes');
    });
    """

def calculate_marker_radius(value, min_radius=5, max_radius=20):
    """Calculate marker radius with bounds"""
    if pd.isna(value) or value <= 0:
        return min_radius
    return min(max_radius, max(min_radius, value/100))

def get_marker_color(value):
    """Determine marker color based on value"""
    if pd.isna(value) or value == 'NA':
        return '#9e9e9e'  # Gray for NA
    elif value > 8000:
        return '#d32f2f'  # High
    elif value > 4000:
        return '#f57c00'  # Medium
    elif value > 1000:
        return '#fdd835'  # Low
    else:
        return '#c5e1a5'  # Minimal

def create_year_map(df, year, output_dir):
    """Main function to create map for a specific year with dynamic category popups"""
    # Initialize and process data
    categories = get_crime_categories()
    crime_mapping = create_crime_category_mapping(categories)
    year_data = process_year_data(df, year)
    year_data['Category'] = year_data['Crime Type'].map(lambda x: crime_mapping.get(x, 'Cyber & Other'))
    
    # Create base map without tiles
    m = folium.Map(location=[48, 2], zoom_start=4, tiles=None)

    # Add GeoJSON layer with blue styling as a base layer
    geojson_style = {
        'fillColor': '#e6f3ff',  # Light blue fill
        'color': '#3182bd',      # Medium blue border
        'weight': 1,
        'fillOpacity': 0.3
    }
    
    # Create GeoJSON layer with custom style function
    geojson = folium.GeoJson(
        'europe.geojson',
        name='Europe',
        style_function=lambda x: geojson_style,
        tooltip=None,
        popup=None,
        overlay=False  # This makes it a base layer instead of an overlay
    )
    
    # Add custom JavaScript to ensure GeoJSON stays visible and behind points
    custom_geojson_style = """
    <style>
    /* Base Control Styles */
    .leaflet-control-layers {
      position: relative !important;
      border: none !important;
      border-radius: 16px !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
      background: white !important;
      padding: 0 !important;
      margin: 16px !important;
      width: 240px !important;
      backdrop-filter: blur(8px) !important;
      transition: all 0.2s ease-in-out !important;
      overflow: hidden !important;
      z-index: 1000 !important;
      transform: translateX(calc(100% + 16px)) !important;
      opacity: 0 !important;
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .leaflet-control-layers.active {
      transform: translateX(0) !important;
      opacity: 1 !important;
    }

    .leaflet-control-layers.collapsed {
      display: none !important;
    }

    .leaflet-control-layers:hover {
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12) !important;
    }

    /* Close Button Styles */
    .leaflet-control-layers .close-button {
      position: absolute !important;
      top: 12px !important;
      right: 12px !important;
      width: 24px !important;
      height: 24px !important;
      background-color: transparent !important;
      border: none !important;
      cursor: pointer !important;
    }

    .leaflet-control-layers .close-button::before,
    .leaflet-control-layers .close-button::after {
      content: '' !important;
      position: absolute !important;
      top: 11px !important;
      left: 4px !important;
      width: 16px !important;
      height: 2px !important;
      background-color: #cbd5e1 !important;
    }

    .leaflet-control-layers .close-button::before {
      transform: rotate(45deg) !important;
    }

    .leaflet-control-layers .close-button::after {
      transform: rotate(-45deg) !important;
    }

    /* Header Styles */
    .leaflet-control-layers-expanded::before {
      content: 'Contrôle des couches';
      display: block;
      font-weight: 600;
      font-size: 15px;
      color: #0f172a;
      padding: 16px 20px;
      border-bottom: 1px solid #e2e8f0;
      margin-bottom: 8px;
      letter-spacing: -0.01em;

    }

    /* List Container */
    .leaflet-control-layers-list {
      padding: 12px 8px !important;
      margin: 0 !important;
      max-height: calc(100vh - 240px) !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      scrollbar-width: thin !important;
      box-sizing: border-box !important;
      width: 100% !important;
    }

    /* Layer Items */
    .leaflet-control-layers-overlays label {
      display: flex !important;
      align-items: center !important;
      padding: 10px 12px !important;
      margin: 4px 0 !important;
      border-radius: 12px !important;
      transition: all 0.2s ease-out !important;
      cursor: pointer !important;
      user-select: none !important;
      width: calc(100% - 8px) !important;
      box-sizing: border-box !important;
    }

    .leaflet-control-layers-overlays label:hover {
      background-color: #f8fafc !important;
      transform: translateX(2px) !important;
    }

    /* Checkbox Styles */
    .leaflet-control-layers-selector {
      appearance: none !important;
      -webkit-appearance: none !important;
      width: 20px !important;
      height: 20px !important;
      border: 2px solid #cbd5e1 !important;
      border-radius: 6px !important;
      margin-right: 12px !important;
      position: relative !important;
      cursor: pointer !important;
      transition: all 0.2s ease !important;
      flex-shrink: 0 !important;
    }

    .leaflet-control-layers-selector:checked {
      border-color: #3b82f6 !important;
      background-color: #3b82f6 !important;
    }

    .leaflet-control-layers-selector:checked::after {
      content: '✓' !important;
      position: absolute !important;
      color: white !important;
      font-size: 12px !important;
      left: 50% !important;
      top: 50% !important;
      transform: translate(-50%, -50%) !important;
    }

    /* Toggle Button Styles */
    .layer-toggle-btn {
      position: absolute !important;
      top: 100px !important;
      right: 16px !important;
      z-index: 1000 !important;
      background-color: white !important;
      border: none !important;
      border-radius: 12px !important;
      padding: 8px 16px !important;
      cursor: pointer !important;
      font-size: 14px !important;
      font-weight: 500 !important;
      color: #1e293b !important;
      display: flex !important;
      align-items: center !important;
      gap: 8px !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
      transition: all 0.2s ease-out !important;
      transform: translateX(0) !important;
    }

    .layer-toggle-btn:hover {
      transform: translateX(-4px) !important;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
    }

    .layer-toggle-btn.hidden {
      transform: translateX(calc(100% + 16px)) !important;
      opacity: 0 !important;
    }

    .layer-toggle-btn .icon {
      display: inline-block !important;
      transition: transform 0.3s ease !important;
    }

    .layer-toggle-btn:hover .icon {
      transform: rotate(-15deg) !important;
    }

    /* Label Text */
    .leaflet-control-layers-overlays span {
     white-space: normal !important;  /* Changed from nowrap to normal */
      overflow: visible !important;    /* Changed from hidden to visible */
      text-overflow: clip !important;  /* Changed from ellipsis to clip */
      line-height: 1.4 !important;     /* Added line height */
      max-width: 100% !important;      /* Added max width */
      word-wrap: break-word !important; /* Added word wrap */
    }

    /* Scrollbar Styling */
    .leaflet-control-layers-list::-webkit-scrollbar {
      width: 4px !important;
    }

    .leaflet-control-layers-list::-webkit-scrollbar-track {
      background: transparent !important;
    }

    .leaflet-control-layers-list::-webkit-scrollbar-thumb {
      background: #e2e8f0 !important;
      border-radius: 2px !important;
    }

    .leaflet-control-layers-list::-webkit-scrollbar-thumb:hover {
      background: #cbd5e1 !important;
    }

    /* Toggle Button */
    .leaflet-control-layers-toggle {
      width: 40px !important;
      height: 40px !important;
      background-size: 18px !important;
      border-radius: 12px !important;
      background-color: white !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
      transition: all 0.2s ease !important;
    }

    .leaflet-control-layers-toggle:hover {
      background-color: #f8fafc !important;
      transform: translateY(-1px) !important;
    }

    /* Z-index Fixes */
    .leaflet-pane.leaflet-overlay-pane {
      z-index: 400 !important;
    }

    .leaflet-pane.leaflet-marker-pane {
      z-index: 600 !important;
    }

    .leaflet-pane.leaflet-popup-pane {
      z-index: 700 !important;
    }

    /* Responsive Adjustments */
    @media (max-width: 768px) {
      .leaflet-control-layers {
        width: 200px !important;
        margin: 12px !important;
      }
      
      .leaflet-control-layers-list {
        max-height: calc(100vh - 280px) !important;
      }
      
      .leaflet-control-layers-overlays label {
        padding: 8px 12px !important;
      }
      
      .leaflet-control-layers-expanded::before {
        padding: 14px 16px;
        font-size: 14px;
      }
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(custom_geojson_style))
    geojson.add_to(m)

    # Create mutually exclusive layer groups
    layer_groups = {}
    
    # Create "Tous les crimes" layer
    all_crimes_group = folium.FeatureGroup(name="Tous les crimes")
    layer_groups['Tous les crimes'] = all_crimes_group
    
    # Create category-specific layer groups
    for cat_name, cat_info in categories.items():
        if cat_info is not None:
            layer_groups[cat_name] = folium.FeatureGroup(name=cat_name)
    
    # Process each country
    for country in year_data['NAME'].unique():
        try:
            country_data = year_data[year_data['NAME'] == country]
            if country_data['lat'].isna().all() or country_data['lon'].isna().all():
                continue
            
            # Use country-specific graph file instead of year-specific
            graph_file = f'graph_{country.replace(" ", "_")}.html'
            graph_path = os.path.join(output_dir, graph_file)
            
            # Only create graph file if it doesn't exist
            if not os.path.exists(graph_path):
                graph_html = create_crime_trend_graph(df, country)
                with open(graph_path, 'w', encoding='utf-8') as f:
                    f.write(graph_html)
            
            # Calculate totals and prepare data for each category
            category_data = {}
            for cat_name, cat_info in categories.items():
                if cat_info is not None:
                    cat_crimes = cat_info['crimes']
                    cat_data = country_data[country_data['Crime Type'].isin(cat_crimes)]
                    total = cat_data['Value'].sum()
                    category_data[cat_name] = {
                        'total': 'NA' if pd.isna(total) else total,
                        'crimes': cat_data.to_dict('records')
                    }
            
            total_crime = country_data['Value'].sum()
            
            # Create HTML content for each category
            popup_contents = {
                'Tous les crimes': create_category_popup_content(country, year, country_data.to_dict('records'), 
                                                            total_crime, graph_file, 'Tous les crimes')
            }
            for cat_name, cat_info in category_data.items():
                popup_contents[cat_name] = create_category_popup_content(country, year, cat_info['crimes'], 
                                                                        cat_info['total'], graph_file, cat_name)
            
            # Create markers for each category with hidden popup data
            marker_data = {
                'country': country,
                'popups': popup_contents,
                'graph_file': graph_file
            }
            
            # Tous les crimes marker
            if pd.notna(total_crime):
                marker = folium.CircleMarker(
                    location=[country_data['lat'].iloc[0], country_data['lon'].iloc[0]],
                    radius=calculate_marker_radius(total_crime),
                    popup=folium.Popup(popup_contents['Tous les crimes'], max_width=300),
                    color='black',
                    weight=1,
                    fill=True,
                    fillColor=get_marker_color(total_crime),
                    fillOpacity=0.7,
                    html=f'<div class="marker-data" style="display:none;" data-info=\'{json.dumps(marker_data)}\'></div>'
                )
                all_crimes_group.add_child(marker)
            
            # Category-specific markers
            for cat_name, cat_info in category_data.items():
                cat_total = cat_info['total']
                if cat_total != 'NA' and pd.notna(cat_total):
                    cat_marker = folium.CircleMarker(
location=[country_data['lat'].iloc[0], country_data['lon'].iloc[0]],
                        radius=calculate_marker_radius(cat_total),
                        popup=folium.Popup(popup_contents[cat_name], max_width=300),
                        color='black',
                        weight=1,
                        fill=True,
                        fillColor=get_marker_color(cat_total),
                        fillOpacity=0.7,
                        html=f'<div class="marker-data" style="display:none;" data-info=\'{json.dumps(marker_data)}\'></div>'
                    )
                    layer_groups[cat_name].add_child(cat_marker)
            
        except Exception as e:
            print(f"Error processing {country}: {str(e)}")
            continue
    
    # Add all crime layer groups to map
    for group in layer_groups.values():
        group.add_to(m)
    
    # Add custom JavaScript for mutually exclusive layer control and popup updates
    custom_js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var currentCategory = 'Tous les crimes';
        var openPopups = new Set();
        var isPlaying = false;  // Add flag to track playback state
        
        function updatePopupContent(popup, category) {
            try {
                const container = popup._container;
                if (!container) return;
                
                const markerData = container.querySelector('.marker-data');
                if (!markerData) return;
                
                const data = JSON.parse(markerData.dataset.info);
                const popupContent = data.popups[category];
                
                const popupContentDiv = container.querySelector('.leaflet-popup-content');
                if (popupContentDiv) {
                    popupContentDiv.innerHTML = popupContent;
                }
            } catch (error) {
                console.error('Error updating popup:', error);
            }
        }
        
        function updateAllPopups(category) {
            document.querySelectorAll('.leaflet-popup').forEach(popup => {
                const popupObj = popup.__popup;
                if (popupObj) {
                    updatePopupContent(popupObj, category);
                }
            });
        }
        
        // Get all layer control inputs
        var inputs = document.querySelectorAll('.leaflet-control-layers-selector');
        
        // Modify the change event listener
        inputs.forEach(function(input) {
            input.addEventListener('change', function(e) {
                if (isPlaying) {
                    // Prevent layer changes during playback
                    e.preventDefault();
                    return false;
                }
                
                if (this.checked) {
                    // Uncheck all other inputs
                    inputs.forEach(function(otherInput) {
                        if (otherInput !== input && otherInput.checked) {
                            otherInput.click();
                        }
                    });
                    
                    currentCategory = input.labels[0].innerText.trim();
                    updateAllPopups(currentCategory);
                }
            });
        });

        // Listen for play/pause messages from the parent window
        window.addEventListener('message', function(event) {
            if (event.data.type === 'playbackState') {
                isPlaying = event.data.isPlaying;
                
                // If starting playback, ensure only Tous les crimes is visible
                if (isPlaying) {
                    inputs.forEach(function(input) {
                        const label = input.labels[0].innerText.trim();
                        if (label === 'Tous les crimes' && !input.checked) {
                            input.click();
                        }
                    });
                    
                    // Hide layer control during playback
                    document.querySelector('.leaflet-control-layers').classList.remove('active');
                    document.querySelector('.layer-toggle-btn').classList.add('hidden');
                } else {
                    // Show layer control after playback
                    document.querySelector('.layer-toggle-btn').classList.remove('hidden');
                }
            }
        });
        
        // Enhanced layer control functionality
        var layerControl = document.querySelector('.leaflet-control-layers');
        
        // Create and style toggle button
        var toggleButton = document.createElement('button');
        toggleButton.className = 'layer-toggle-btn hidden';
        toggleButton.innerHTML = '<span class="icon">🗺️</span>';
        document.body.appendChild(toggleButton);

        // Show toggle button after a short delay
        setTimeout(() => {
            toggleButton.classList.remove('hidden');
        }, 300);

        // Add close button to layer control
        if (layerControl) {
            var closeButton = document.createElement('button');
            closeButton.className = 'close-button';
            layerControl.appendChild(closeButton);

            // Handle layer control visibility
            closeButton.addEventListener('click', function() {
                layerControl.classList.remove('active');
                setTimeout(() => {
                    toggleButton.classList.remove('hidden');
                }, 300);
            });

            toggleButton.addEventListener('click', function() {
                layerControl.classList.add('active');
                toggleButton.classList.add('hidden');
            });

            // Initialize layer control state
            setTimeout(() => {
                layerControl.classList.remove('active');
                toggleButton.classList.remove('hidden');
            }, 100);
        }
        
        // Ensure only "Tous les crimes" is initially visible
        setTimeout(function() {
            inputs.forEach(function(input) {
                const label = input.labels[0].innerText.trim();
                if (input.checked && label !== 'Tous les crimes') {
                    input.click();
                } else if (!input.checked && label === 'Tous les crimes') {
                    input.click();
                }
            });
        }, 100);
        
        // Add observer for new popups
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('leaflet-popup')) {
                        const popupObj = node.__popup;
                        if (popupObj) {
                            updatePopupContent(popupObj, currentCategory);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.querySelector('.leaflet-map-pane'), {
            childList: true,
            subtree: true
        });
    });
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(custom_js))
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Save map file
    output_file = os.path.join(output_dir, f'map_{year}.html')
    m.save(output_file, 'UTF-8') #adding utf
    return output_file



def create_main_page(years, output_dir):
    """
    Create the main HTML page with year selection and improved play controls
    
    Args:
        years: List of years to display
        output_dir: Directory to save the output HTML file
    """
    # Convert years to a proper JavaScript array string
    years_js_array = "[" + ",".join(str(year) for year in years) + "]"
    
    # Read the main page template adding utf
    with open('templates/main_page_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Insert the years array into the template
    main_html = template.replace('const years = [];', f'const years = {years_js_array};')
    
    # Save the main page
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(main_html)

def create_rankings_page(df, output_dir):
    """Create the rankings page with embedded data"""
    # Read the rankings page template
    with open('templates/rankings_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Convert DataFrame to JSON
    df_json = df.to_json(orient='records')
    
    # Insert the data into the template
    rankings_html = template.replace(
        'let crimeData = [];',
        f'let crimeData = {df_json};'
    )
    
    # Save the rankings page
    with open(os.path.join(output_dir, 'rankings.html'), 'w', encoding='utf-8') as f:
        f.write(rankings_html)

def create_temporal_crime_map(csv_file):
    """Main function to create the temporal crime map"""
    df = pd.read_csv(csv_file, encoding='utf-8') #adding utf-8
    df['Year'] = df['Year'].astype(int)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])
    
    output_dir = 'crime_maps'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the rankings page first
    create_rankings_page(df, output_dir)
    
    # Create graph files for all countries first
    countries = df['NAME'].unique()
    print(f"Creating trend graphs for {len(countries)} countries")
    for country in countries:
        graph_file = f'graph_{country.replace(" ", "_")}.html'
        graph_path = os.path.join(output_dir, graph_file)
        if not os.path.exists(graph_path):
            graph_html = create_crime_trend_graph(df, country)
            with open(graph_path, 'w', encoding='utf-8') as f:
                f.write(graph_html)
    
    # Create maps for each year
    years = sorted(df['Year'].unique())
    print(f"Processing maps for years: {years}")
    for year in years:
        print(f"Creating map for year {year}")
        create_year_map(df, year, output_dir)
    
    create_main_page(years, output_dir)
    print(f"Maps created in directory: {output_dir}")

if __name__ == "__main__":
    csv_file = "merged_crimes_per_hundred_thousand_french.csv"
    
    try:
        create_temporal_crime_map(csv_file)
        print("Maps created successfully")
    except Exception as e:
        print(f"Error: {str(e)}")