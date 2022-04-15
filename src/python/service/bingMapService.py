import urllib
import requests
from src.python.config import appConfig

'''
"https://dev.virtualearth.net/REST/v1/Locations/US/{adminDistrict}/{postalCode}/{locality}/{" \
                "addressLine}?includeNeighborhood={includeNeighborhood}&include={includeValue}&maxResults={" \
                "maxResults}&key={BingMapsAPIKey}"
'''


def getLatLong(
        addressLine="University%20of%20California,%20Irvine",
        city="Irvine",
        adminDistrict="CA",
        postalCode="92697",
        country="US"):
    returnFormat = "json"
    url = f'https://dev.virtualearth.net/REST/v1/Locations/' \
          f'{urllib.parse.quote_plus(country)}' \
          f'/{urllib.parse.quote_plus(adminDistrict)}' \
          f'/{urllib.parse.quote_plus(postalCode)}' \
          f'/{urllib.parse.quote_plus(city)}' \
          f'/{urllib.parse.quote_plus(addressLine)}?' \
          f'o={returnFormat}&key={appConfig.bingMapApiKey}'
    response = requests.get(url).json()

    return response["resourceSets"][0]["resources"][0]["point"]["coordinates"], response
