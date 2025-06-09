from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    # Pobierz parametr cut z URL
    selected_cut = request.args.get('cut', 'All')

    # Wczytaj dane
    df = pd.read_csv("diamonds.csv")

    # Przekształcenie kolumn kategorii
    df['cut'] = pd.Categorical(df['cut'], categories=['Fair', 'Good', 'Very Good', 'Premium', 'Ideal'], ordered=True)
    df['color'] = pd.Categorical(df['color'], categories=['J', 'I', 'H', 'G', 'F', 'E', 'D'], ordered=True)
    df['clarity'] = pd.Categorical(df['clarity'], categories=['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF'], ordered=True)

    # Filtrowanie
    if selected_cut != 'All':
        df = df[df['cut'] == selected_cut]

    # Statystyki
    total_diamonds = len(df)
    avg_price = int(df['price'].mean())
    avg_carat = round(df['carat'].mean(), 2)

   

 # Wykres 1: Cena vs Masa wg Czystości
    fig1 = px.scatter(df.sample(2000), x='carat', y='price', color='clarity',
                      title='Cena vs Masa (carat) wg czystości', opacity=0.6)
    graph1 = pio.to_html(fig1, full_html=False)

    # Wykres 2: Średnia cena wg koloru i jakości cięcia
    avg_price_data = df.groupby(['color', 'cut'])['price'].mean().reset_index()
    fig2 = px.bar(avg_price_data, x='color', y='price', color='cut', barmode='group',
                  title='Średnia cena wg koloru i cięcia', width=900)
    graph2 = pio.to_html(fig2, full_html=False)

    # Wykres 3: 3D scatter (x, y, z, cena)
    fig3 = px.scatter_3d(df.sample(1000), x='x', y='y', z='z', color='price',
                         title='Rozkład wymiarów (x, y, z) i cena', width=900)
    graph3 = pio.to_html(fig3, full_html=False)

    # Wykres 4: Heatmapa korelacji
    corr = df[['carat', 'depth', 'table', 'price', 'x', 'y', 'z']].corr()
    fig4 = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Korelacja")
    ))
    fig4.update_layout(title="Macierz korelacji cech liczbowych", width=900)
    graph4 = pio.to_html(fig4, full_html=False)

    # Wykres 5: Mapa losowych lokalizacji (scatter_geo)
    # Przykładowe dane lokalizacyjne
    countries = ['Poland', 'Germany', 'USA', 'India', 'Brazil', 'France', 'China', 'Canada']
    samples = np.random.choice(countries, size=len(df), replace=True)
    df_map = df.copy()
    df_map['country'] = samples
    location_avg = df_map.groupby('country')['price'].mean().reset_index()
    fig_map = px.choropleth(location_avg, locations='country', locationmode='country names',
                            color='price', title='Średnia cena diamentów wg kraju (losowo)',
                            color_continuous_scale='Viridis', width = 900)
    map_graph = pio.to_html(fig_map, full_html=False)

    return render_template("index.html",
                           graph1=graph1,
                           graph2=graph2,
                           graph3=graph3,
                           graph4=graph4,
                           map_graph=map_graph,
                           total_diamonds=total_diamonds,
                           avg_price=avg_price,
                           avg_carat=avg_carat,
                           selected_cut=selected_cut)

if __name__ == '__main__':
    app.run(debug=True)
