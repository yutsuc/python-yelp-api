import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

def searchByLocation(location):
    return ""

def main():
    while True:
        # Gets user input of location
        location = input('Enter a city, state (e.g. San Francisco, CA or Ann Arbor, MI) or "exit" \n: ')

        if location.lower() == "exit":
            exit()
        else:
            # try catch如果API request有http error的話會直接結束
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