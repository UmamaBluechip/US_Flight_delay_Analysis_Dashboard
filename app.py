from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import io
import plotly.express as px
from utils.data_processing import load_flight_data, preprocess_flight_data, geo_data


file_path = 'data/On_Time_Marketing_Carrier_On_Time_Performance_(Beginning_January_2018)_2023_1.csv'
data = load_flight_data(file_path)

final_data = preprocess_flight_data(data)

dep_delay_per_state, arr_delay_per_state = geo_data(data)

app = Flask(__name__)

@app.route("/")
def index():
    average_dep_delay = final_data['DepDelayMinutes'].mean()
    average_arr_delay = final_data['ArrDelayMinutes'].mean()
    total_air_time = final_data['AirTime'].sum()
    total_distance = final_data['Distance'].sum()

    return render_template('index.html',
                           avg_dep_del=average_dep_delay,
                           avg_arr_del=average_arr_delay,
                           totalAirTime=total_air_time,
                           totalDistance=total_distance)

@app.route("/line_plot")
def line_plot():
    line_fig = px.line(final_data, x='DayofMonth', y='DepartureDelayGroups', 
                       title='Departure Delays Over Days of the Month')
    
    line_plot_html = line_fig.to_html(full_html=False)
    return render_template('line_plot.html', line_plot=line_plot_html)

@app.route("/bar_chart")
def bar_chart():
    avg_arrival_delays = final_data.groupby('Marketing_Airline_Network')['ArrivalDelayGroups'].mean().reset_index()
    fig = px.bar(avg_arrival_delays, x='Marketing_Airline_Network', y='ArrivalDelayGroups', 
                 title='Average Arrival Delays by Marketing Airline Network')
    fig.update_layout(xaxis_title='Marketing Airline Networks', yaxis_title='Average Arrival Delay Groups')
    
    return render_template('bar_chart.html', bar_chart=fig.to_html(full_html=False))

@app.route("/scatter_plot")
def scatter_plot():
    scatter_fig = px.scatter(final_data, x='DepartureDelayGroups', y='ArrivalDelayGroups', 
                             title='Departure Delays vs Arrival Delays', opacity=0.5)
    
    scatter_plot_html = scatter_fig.to_html(full_html=False)
    return render_template('scatter_plot.html', scatter_plot=scatter_plot_html)

@app.route("/boxplot")
def boxplot():
    data = [final_data[final_data['Marketing_Airline_Network'] == airline]['DepartureDelayGroups'] 
            for airline in final_data['Marketing_Airline_Network'].unique()]

    fig = px.box(data, labels={'value': 'Departure Delay Groups', 'x': 'Airlines'},
                 title='Departure Delays by Airlines')

    return render_template('boxplot.html', plot=fig.to_html())

@app.route('/choropleth_map')
def render_choropleth_map():
    fig = px.choropleth(
        dep_delay_per_state,
        locations='OriginState',
        color='DepDelayMinutes',
        locationmode='USA-states',
        scope='usa',
        color_continuous_scale='Viridis',
        title='Total Depature Delay Minutes by State'
    )

    fig.update_layout(
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            projection_type='albers usa'
        )
    )

    return render_template('choropleth_map.html', plot=fig.to_html())    


if __name__ == '__main__':
    app.run(debug=True)
