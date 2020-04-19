import requests
import sqlite3
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

# Database variables
CONN = sqlite3.connect('./YelpCafe.sqlite')
CUR = CONN.cursor()

# API variables
API_KEY= 'EKJ9TZaYDzW-wnqgcQxNVVQQwz-K624lEH_Cwj1DI7NvHZm16P6P0YMsfvE2Jm4a1h2GWGwZlSikgo45BzGJXfxLdPtWBrlq6cJYMfLsjZrUq8XZZOJogZ65kaaYXnYx'
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

def insertDataToDB(table, data):
    if table == 'cafe':
        insert = 'INSERT INTO Cafe VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    elif table == 'category':
        insert = 'INSERT INTO Category VALUES (NULL, ?, ?)'
    elif table == 'cafe_category':
        insert = 'INSERT INTO Cafe_Category VALUES (?, ?)'
  
    CUR.execute(insert, data)
    CONN.commit()
    insertedId= CUR.lastrowid
    return insertedId

def getCategory(alias):
    sql = 'SELECT Id, Title, Alias FROM Category WHERE Alias = "{0}"'.format(alias)
    CUR.execute(sql)
    return CUR.fetchall()
    
def getCategoryIds(categories):
    ids = []
    for c in categories:
        category = getCategory(c['alias'])
        if len(category) == 0:
            category_values = [c['title'], c['alias']]
            id = insertDataToDB('category', category_values)
        else:
            id = category[0][0]
        ids.append(id)
    return ids

def insertCafes(cafes):
    # TODO: check if exist before insert
    for c in cafes:
        cafe_values = [c['id'], c['name'], c['rating'], c['review_count'], c['location']['state'],
            c['location']['city'], ', '.join(c['location']['display_address']), c['location']['zip_code'], c['display_phone'], c['url']]
        categories = getCategoryIds(c['categories'])
        insertDataToDB('cafe', cafe_values)
    test = CUR.execute('SELECT * FROM Cafe')
    rows = CUR.fetchall()
    return rows
    

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
    insertCafes(businesses)
    
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