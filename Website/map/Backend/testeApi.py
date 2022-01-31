import openrouteservice
import json
""" - setup openrouteservice client with api key, you can signup https://openrouteservice.org 
      if you don't have API key. Its totaly free😊
    - After signup, you can see your API key available under the dashboard tab.
"""
client = openrouteservice.Client(key='5b3ce3597851110001cf6248bf5bdcd04df248c3b65cda7a92bb1561')

#set location coordinates in longitude,latitude order
coords = ((-8.8373567,41.70154),(-8.8324579,41.6900904))

#call API
res = client.directions(coords)
#test our response
with(open('test.json','+w')) as f:
 f.write(json.dumps(res,indent=4, sort_keys=True))