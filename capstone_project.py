import collections
from datetime import datetime
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from folium import plugins

# Armenian map borders for longitude and latitude values
armenian_map_borders = {
    "lonMin": 43.45,  
    "lonMax": 47.17,  
    "latMin": 38.84,  
    "latMax": 41.3 
}

lightning_data_source_url = list([(2018, 'https://lightning.nsstc.nasa.gov/isslisib/tmp/lisflashes-46.70.69.250.txt'),
                                  (2019, 'https://lightning.nsstc.nasa.gov/isslisib/tmp/lisflashes-62.3.16.1.txt'),
                                  (2020, 'https://lightning.nsstc.nasa.gov/isslisib/tmp/lisflashes-46.71.128.123.txt'),
                                  (2021, 'https://lightning.nsstc.nasa.gov/isslisib/tmp/lisflashes-217.76.14.49.txt'),
                                  (
                                      2022,
                                      'https://lightning.nsstc.nasa.gov/isslisib/tmp/lisflashes-141.136.79.228.txt')])

armenian_lightning_data = {}


def fetch_data_from_server(url, map_borders):
    df = pd.read_csv(url, delimiter='\s+', usecols=[0, 1, 4, 5], names=['Time', 'Months', 'Latitude', 'Longitude'],
                     skiprows=1)
    df['Latitude'] = df['Latitude'].str.replace(',', '').astype(float)
    df['Longitude'] = df['Longitude'].str.replace(r'\)', '', regex=True).astype(float)
    df["Time"] = tuple(datetime.strptime(date_str, '%Y-%jT%H:%M:%S.%fZ').hour for date_str in df['Time'])
    df['Months'] = df['Months'].str.replace(r'\[', '', regex=True)
    filtered_df = df[
        (df['Latitude'] >= map_borders["latMin"]) & (df['Latitude'] <= map_borders["latMax"]) & (
                df['Longitude'] >= map_borders["lonMin"]) & (
                df['Longitude'] <= map_borders["lonMax"])]
    return filtered_df

##################################################
def create_time_histogram(data):
    time_array = list([])
    for year, value in data.items():
        if year != 2018:
            for time in value['Time']:
                time_array.append(time)

    unique_times = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
                    (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12),
                    (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18),
                    (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24)]

    time_counts = collections.Counter(time_array)
    freq_time = [collections.Counter(time_array)[l_time[0]] for l_time in unique_times]

    fig, ax = plt.subplots()
    x_pos = range(len(unique_times))
    bar_width = 0.8
    ax.bar(x_pos, freq_time, label='Time', color='purple', width=bar_width, align='edge')


    ax.set_xticks([i + bar_width / 2 for i in x_pos])  # Shift the ticks by half the bar width
    ax.set_xticklabels([l_time[0] for l_time in unique_times])
    ax.set_xlabel('Time')
    ax.set_ylabel('N')
    ax.set_title('Time Frequencies over Armenia during 2019-2022 (UTC)')
    ax.legend(loc='upper left')

    # Display the histogram
    plt.show()
############################################

def show_histogram(data, l_year):
    # Histogram as a map
    plt.hist2d(data['Longitude'], data['Latitude'], bins=100, cmap='viridis', vmin=0, vmax=9)
    plt.colorbar()
    # Set axis labels and title
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Spread of Lightnings in Armenia in ' + str(l_year))
    # Show the plot
    plt.show()


def get_styles(feature):
    return {
        'fillColor': 'transparent',
        'color': 'Black',
        'weight': 2
    }


# Armenian shp file
armenia = gpd.read_file('C:/Users/aleks/Downloads/arm_adm_2029_shp')


def create_map_with_dots(lightning_data, l_color_list):
    # Create a map centered on Armenia
    map_with_dots = folium.Map(location=[40, 45], zoom_start=7.5)
    color_index = 0

    for l_year, l_data in lightning_data.items():
        if l_year != 2018:
            # Add a dot for each set of longitude and latitude values
            for longitude, latitude in zip(l_data['Longitude'], l_data['Latitude']):
                folium.CircleMarker(location=(latitude, longitude), radius=1, color=l_color_list[color_index],
                                    fill=True,
                                    fill_color=l_color_list[color_index]).add_to(
                    map_with_dots)
            color_index += 1

    # Save the map
    folium.GeoJson(armenia, style_function=get_styles).add_to(map_with_dots)
    map_with_dots.save('MapWithDots.html')


def create_heat_map(locations, lightning_year):
    map_of_frequency = folium.Map(location=[40, 45], zoom_start=7.5)
    folium.GeoJson(armenia, style_function=get_styles).add_to(map_of_frequency)
    folium.plugins.HeatMap(locations, min_opacity=0.2, max_opacity=0.8, radius=15, blur=10, max_zoom=1).add_to(
        map_of_frequency)
    map_of_frequency.save('HeatMap_' + str(lightning_year) + '.html')

#####################################################################
def create_monthly_histogram_for_all_years(all_years_freq: list):
    monthly_count = list([])
    for i in range(0, 12):
        count = 0
        for freq in all_years_freq:
            count += freq[i]
        monthly_count.append(count)

    fig, ax = plt.subplots()
    x_pos = range(len(unique_months))
    bar_width = 0.8
    ax.bar(x_pos, monthly_count, label='Monthly', color='hotpink', width=bar_width, align='edge')
    ax.set_xticks([i + bar_width / 2 for i in x_pos])  # Shift the ticks by half the bar width
    ax.set_xticklabels([month[0] for month in unique_months])
    ax.set_xlabel('Months')
    ax.set_ylabel('N')
    ax.set_title('Number of Monthly Lightning Activity over Armenia for the years 2019-2022')
    ax.legend(loc='upper left')
    plt.show()

#################################################

for data_source in lightning_data_source_url:
    armenian_lightning_data[data_source[0]] = fetch_data_from_server(data_source[1], armenian_map_borders)

for year, data in armenian_lightning_data.items():
    if year != 2018:
        show_histogram(data, year)

color_list = ['red', 'blue', 'orange', 'green']
create_map_with_dots(dict(sorted(armenian_lightning_data.items(), reverse=True)), color_list)

for year, data in armenian_lightning_data.items():
    if year != 2018:
        create_heat_map(data[['Latitude', 'Longitude']].values.tolist(), year)

########## Comparative histogram of 4 years
# create a list of tuples for unique months, sorted by numerical value
unique_months = [('Jan', 1), ('Feb', 2), ('Mar', 3), ('Apr', 4), ('May', 5), ('Jun', 6),
                 ('Jul', 7), ('Aug', 8), ('Sep', 9), ('Oct', 10), ('Nov', 11), ('Dec', 12)]

# count the frequencies of each month for each year
freq_2019 = [collections.Counter(armenian_lightning_data[2019]['Months'])[month[0]] for month in unique_months]
freq_2020 = [collections.Counter(armenian_lightning_data[2020]['Months'])[month[0]] for month in unique_months]
freq_2021 = [collections.Counter(armenian_lightning_data[2021]['Months'])[month[0]] for month in unique_months]
freq_2022 = [collections.Counter(armenian_lightning_data[2022]['Months'])[month[0]] for month in unique_months]

# create the bar plot
fig, ax = plt.subplots()
x_pos = range(len(unique_months))
bar_width = 0.2
ax.bar(x_pos, freq_2019, width=bar_width, label='2019', color='green')
ax.bar([i + bar_width for i in x_pos], freq_2020, width=bar_width, label='2020', color='orange')
ax.bar([i + 2 * bar_width for i in x_pos], freq_2021, width=bar_width, label='2021')
ax.bar([i + 3 * bar_width for i in x_pos], freq_2022, width=bar_width, label='2022', color='red')

# add labels and titles
ax.set_xticks([i + 1.5 * bar_width for i in x_pos])
ax.set_xticklabels([month[0] for month in unique_months])
ax.set_xlabel('Month')
ax.set_ylabel('N')
ax.set_title('Comparative Histogram of Monthly Frequencies in Armenia')
ax.legend(loc='upper left')

plt.show()

##########Count of lightnings in every year


print("Number of lightning activity over Armenia in 2019: ",
      len(armenian_lightning_data[2019][['Latitude', 'Longitude']].values.tolist()))
print("Number of lightning activity over Armenia in 2020: ",
      len(armenian_lightning_data[2020][['Latitude', 'Longitude']].values.tolist()))
print("Number of lightning activity over Armenia in 2020: ",
      len(armenian_lightning_data[2021][['Latitude', 'Longitude']].values.tolist()))
print("Number of lightning activity over Armenia in 2021: ",
      len(armenian_lightning_data[2022][['Latitude', 'Longitude']].values.tolist()))


####################### Armavir ##################


# Define a function to filter data by latitude and longitude ranges
def filter_data_by_location(data, lat_range, lon_range):
    return data[(data['Latitude'] >= lat_range[0]) & (data['Latitude'] <= lat_range[1]) &
                (data['Longitude'] >= lon_range[0]) & (data['Longitude'] <= lon_range[1])]


# Define the latitude and longitude ranges for Armavir
armavir_lat_range = (40, 40.3)
armavir_lon_range = (43.6, 44.6)

# Filter the data by location for each year
armavir_2018 = filter_data_by_location(armenian_lightning_data[2018], armavir_lat_range, armavir_lon_range)
armavir_2019 = filter_data_by_location(armenian_lightning_data[2019], armavir_lat_range, armavir_lon_range)
armavir_2020 = filter_data_by_location(armenian_lightning_data[2020], armavir_lat_range, armavir_lon_range)
armavir_2021 = filter_data_by_location(armenian_lightning_data[2021], armavir_lat_range, armavir_lon_range)
armavir_2022 = filter_data_by_location(armenian_lightning_data[2022], armavir_lat_range, armavir_lon_range)

# Create a map centered on Armenia
def heat_map_allYears():
    all_locations = []
    for year, data in armenian_lightning_data.items():
        all_locations += data[['Latitude', 'Longitude']].values.tolist()
    heatmap = folium.Map(location=[40, 45], zoom_start=7.5)
    folium.GeoJson(armenia, style_function=get_styles).add_to(heatmap)
    folium.plugins.HeatMap(all_locations, min_opacity=0.2, max_opacity=0.8, radius=15, blur=10, max_zoom=1).add_to(
        heatmap)
    heatmap.save('HeatMap_AllYears.html')

heat_map_allYears()

# Define a function to add markers to the map for a given year and color
def add_markers_to_map(data, color):
    for lon, lat in zip(data['Longitude'], data['Latitude']):
        folium.CircleMarker(location=(lat, lon), radius=4, color=color, fill=True, fill_color=color).add_to(armavir_map)

armavir_map = folium.Map(location=[40.15446, 44.03815], zoom_start=10)
# Add markers to the map for each year and color
add_markers_to_map(armavir_2022, 'red')
add_markers_to_map(armavir_2021, 'blue')
add_markers_to_map(armavir_2020, 'orange')
add_markers_to_map(armavir_2019, 'green')
add_markers_to_map(armavir_2018, 'purple')

armenia_geojson = folium.GeoJson(armenia, style_function=get_styles)
armenia_geojson.add_to(armavir_map)

# Save the map as an HTML file
armavir_map.save('ArmavirMap.html')


# Print the number of lightning activity for each year
print("Number of lightning activity over Armavir in 2018:", len(armavir_2018))
print("Number of lightning activity over Armavir in 2019:", len(armavir_2019))
print("Number of lightning activity over Armavir in 2020:", len(armavir_2020))
print("Number of lightning activity over Armavir in 2021:", len(armavir_2021))
print("Number of lightning activity over Armavir in 2022:", len(armavir_2022))

create_time_histogram(armenian_lightning_data)
create_monthly_histogram_for_all_years(list([freq_2019,freq_2020, freq_2021, freq_2022]))

