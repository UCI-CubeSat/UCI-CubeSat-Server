import urllib
import requests

# consider using this library instead
# https://geocoder.readthedocs.io/
# https://github.com/DenisCarriere/geocoder

BING_API_KEY = "AlG8wXq_mQ7kAhYeZzRQPsRPaFxei31_kBCmTW9P_RFOkhFBr1HCl9eT0NTkwEen"  # Insert API key here
BING_BASE_URL = "http://dev.virtualearth.net/REST/v1/Locations/US/{adminDistrict}/{postalCode}/{locality}/{" \
                "addressLine}?includeNeighborhood={includeNeighborhood}&include={includeValue}&maxResults={" \
                "maxResults}&key={BingMapsAPIKey}"


def getLatLong(addressLine="University%20of%20California,%20Irvine", city="Irvine", adminDistrict="CA",
               postalCode="92697", country="US"):
    returnFormat = "json"
    url = f'https://dev.virtualearth.net/REST/v1/Locations/' \
          f'{urllib.parse.quote_plus(country)}' \
          f'/{urllib.parse.quote_plus(adminDistrict)}' \
          f'/{urllib.parse.quote_plus(postalCode)}' \
          f'/{urllib.parse.quote_plus(city)}' \
          f'/{urllib.parse.quote_plus(addressLine)}?' \
          f'o={returnFormat}&key={BING_API_KEY}'
    response = requests.get(url).json()

    return response["resourceSets"][0]["resources"][0]["point"]["coordinates"], response
