from django.shortcuts import render
import folium
import sys
import openrouteservice
from openrouteservice import convert

sys.path.insert(0, r"D:\Escola\orTools\Website\map\Backend")

from DefineRoutes import create_data

client = openrouteservice.Client(key='5b3ce3597851110001cf6248bf5bdcd04df248c3b65cda7a92bb1561')

# Create your views here.
def index(request):

    #Create Map Object
    m = folium.Map(
        location = [41.697210, -8.832654], 
        zoom_start = 15
    )
    dados = create_data()

    for coordenada in dados['addresses']:

        index = coordenada.find(',')
        lat = coordenada[0:index]

        temp = index+1
        long = coordenada[temp:]

        lat = float(lat)
        long = float(long)

        folium.Marker([lat, long], tooltip='Click for more', popup='Armazém').add_to(m)


    #HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)

def GetRoute(request):
    # Create Map Object
    m = folium.Map(
        location=[41.697210, -8.832654],
        zoom_start=15
    )
    dados = create_data()

    for coordenada in dados['addresses']:
        index = coordenada.find(',')
        lat = coordenada[0:index]

        temp = index + 1
        long = coordenada[temp:]

        lat = float(lat)
        long = float(long)

        folium.Marker([lat, long], tooltip='Click for more', popup='Armazém').add_to(m)

    dados = create_data()
    # implementação da rota
    coords = []

    for coordenada in dados['addresses']:
        index = coordenada.find(',')
        lat = coordenada[0:index]

        temp = index + 1
        long = coordenada[temp:]

        lat = float(lat)
        long = float(long)

        formatted_lat = "{:.14f}".format(lat)
        formatted_long = "{:.14f}".format(long)

        temp_coords = (formatted_long, formatted_lat)

        coords.append(temp_coords)

    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    folium.GeoJson(decoded).add_to(m)

    m.save('map.html')

    # HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)