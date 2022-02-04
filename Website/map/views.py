import os
from django.shortcuts import render
import folium
import sys
import openrouteservice
from openrouteservice import convert
import json

#sys.path.insert(0, r"D:\Escola\orTools\Website\map\Backend")
sys.path.insert(0, r"C:\Users\user\Documents\GitHub\projeto3\Website\map\Backend")

from DefineRoutes import create_data
from DefineRoutes import print_solution
from DefineRoutes import main

client = openrouteservice.Client(key='5b3ce3597851110001cf6248bf5bdcd04df248c3b65cda7a92bb1561')

# Create your views here.
def index(request):
    # Create Map Object
    m = folium.Map(
        location=[41.697210, -8.832654],
        zoom_start=15
    )

    # HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)

teste = main()

def GetRoute(request):
    # Create Map Object
    m = folium.Map(
        location=[41.697210, -8.832654],
        zoom_start=15
    )

    #Pontos
    dados = create_data()
    print_solution(dados, teste[0], teste[1], teste[2])
    pontos = dados['addresses']

    for i in range(len(pontos)):
        #fragmentar coordenada
        index = pontos[i].find(',')
        lat = pontos[i][0:index]

        temp = index+1
        long = pontos[i][temp:]

        lat = float(lat)
        long = float(long)

        if i == 0:
            folium.Marker(
                [lat, long], 
                tooltip='Mais Informação', 
                popup="<h4> Armazém <h4>"  + str([lat,long]) ,
                icon=folium.Icon(color="red")
            ).add_to(m)
        
        else:      
            folium.Marker(
                [lat, long], 
                tooltip='Mais Informação', 
                popup='<h4> Ponto de Distribuição <h4>' + str([lat,long]), 
                icon=folium.Icon(color="blue")
            ).add_to(m)

    # read json file from backend
    data = open('C:/Users/user/Documents/GitHub/projeto3/Website/route.json').read() #opens the json file and saves the raw contents
    jsonData = json.loads(data) #converts to a json structure

    # implementação da rota
    coords1 = []
    coords2 = []

    style1 = {'fillColor': '#228B22', 'color': '#228B22'}
    style2 = {'fillColor': '#00FFFFFF', 'color': '#00FFFFFF'}
    
    # Vehicle 1
    for coordenada in jsonData[0]:
        index = coordenada.find(',')
        lat = coordenada[0:index]

        temp = index + 1
        long = coordenada[temp:]

        lat = float(lat)
        long = float(long)

        formatted_lat = "{:.14f}".format(lat)
        formatted_long = "{:.14f}".format(long)

        temp_coords = (formatted_long, formatted_lat)

        coords1.append(temp_coords)

    geometry = client.directions(coords1)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    folium.GeoJson(decoded, style_function=lambda x:style1).add_child(folium.Popup('<h4> Time of route: {0} min <h4>'.format(jsonData[1]),max_width=300)).add_to(m)

    # Vehicle 2
    for coordenada in jsonData[2]:
        index = coordenada.find(',')
        lat = coordenada[0:index]

        temp = index + 1
        long = coordenada[temp:]

        lat = float(lat)
        long = float(long)

        formatted_lat = "{:.14f}".format(lat)
        formatted_long = "{:.14f}".format(long)

        temp_coords = (formatted_long, formatted_lat)

        coords2.append(temp_coords)

    geometry = client.directions(coords2)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    folium.GeoJson(decoded, style_function=lambda x:style2).add_child(folium.Popup('<h4> Time of route: {0} min <h4>'.format(jsonData[3]),max_width=300)).add_to(m)

    m.save('map.html')

    # HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)
