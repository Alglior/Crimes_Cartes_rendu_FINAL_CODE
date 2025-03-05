import pandas as pd
import plotly.express as px
import plotly.io as pio

# Load the data
data = pd.read_csv("merged_crimes_per_hundred_thousand_french.csv")

# Calculate mean for each crime type per country
numeric_cols = data.select_dtypes(include='number').columns
mean_per_crime_type = data.groupby(['Country', 'Crime Type'])[numeric_cols].agg({
    col: 'mean' for col in numeric_cols
}).reset_index()

# Include the non-numeric columns for merging
final_mean_per_crime_type = pd.merge(
    mean_per_crime_type,
    data[['Country', 'FIPS', 'ISO2', 'ISO3', 'UN', 'NAME', 'lat', 'lon']].drop_duplicates(),
    on='Country',
    how='left'
)

# Create interactive bar plot
fig = px.bar(final_mean_per_crime_type, 
             x='Country',
             y='Value',
             color='Crime Type',
             title='Average Crime Rates by Country and Crime Type',
             labels={'Value': 'Crimes per 100,000 inhabitants'},
             height=600)

# Update layout
fig.update_layout(
    xaxis_tickangle=-45,
    barmode='group',
    showlegend=True,
    legend_title_text='Crime Type'
)

# Save as interactive HTML
fig.write_html("interactive_crime_rates.html")

# Save as static image
fig.write_image("crime_rates_by_country.png", width=1200, height=800)

# Show the plot
fig.show()
