from django.shortcuts import render
from django.template import context
import folium
import sys

sys.path.insert(0, 'D:\Escola\orTools\Website\map\Backend')

from DefineRoutes import create_data

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

        temp = index+2
        long =coordenada[temp:]

        lat=float(lat)
        long=float(long)

        folium.Marker([lat, long], tooltip='Click for more', popup='Armazém').add_to(m)

    #HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)