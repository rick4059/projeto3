from django.shortcuts import render
from django.template import context
import folium

# Create your views here.
def index(request):

    #Create Map Object
    m = folium.Map(
        location = [41.697210, -8.832654], 
        zoom_start = 15
    )

    #HTML representation of the object
    m = m._repr_html_()

    context = {
        'm': m,
    }

    return render(request, 'index.html', context)