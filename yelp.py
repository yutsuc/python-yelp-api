import sys
import requests
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

# API variables
API_KEY= "EKJ9TZaYDzW-wnqgcQxNVVQQwz-K624lEH_Cwj1DI7NvHZm16P6P0YMsfvE2Jm4a1h2GWGwZlSikgo45BzGJXfxLdPtWBrlq6cJYMfLsjZrUq8XZZOJogZ65kaaYXnYx" 
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

# Sends request to Yelp Fusion API, Business Endpoint
def request(url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(API_HOST, quote(SEARCH_PATH.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % API_KEY,
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

# Searches for coffee shops at given location
# Process results and store each item in the database
def searchByLocation(location):
    # Request parameters
    url_params = {
        'categories': 'coffee',
        'location': location.replace(' ', '+'),
        # 'limit': 50,
        'sort_by': 'rating'
    }
    results = request(url_params)
    businesses = results.get('businesses')
    total_results = results.get('total')

    return businesses

def main():
    while True:
        # Gets user input of location
        location = input('Enter a city, state (e.g. San Francisco, CA or Ann Arbor, MI) or "exit" \n: ')

        if location.lower() == "exit":
            exit()
        else:
            # Exit if encounters HTTP error during API request
            try:
                searchByLocation(location)
            except HTTPError as error:
                exit(
                    'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                        error.code,
                        error.url,
                        error.read(),
                    )
                )

                
if __name__ == '__main__':
    main()