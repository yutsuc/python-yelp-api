import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

# API variables
API_KEY= "EKJ9TZaYDzW-wnqgcQxNVVQQwz-K624lEH_Cwj1DI7NvHZm16P6P0YMsfvE2Jm4a1h2GWGwZlSikgo45BzGJXfxLdPtWBrlq6cJYMfLsjZrUq8XZZOJogZ65kaaYXnYx" 
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

# Use Yelp Fusion API, Business Endpoint to get all Coffee shops at given location
def searchByLocation(location):
    return ""

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