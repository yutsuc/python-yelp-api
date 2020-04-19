import json
import requests
import sqlite3
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

# Cache variables
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

# Database variables
CONN = sqlite3.connect('YelpCafe.sqlite')
CUR = CONN.cursor()

# API variables
API_KEY= 'EKJ9TZaYDzW-wnqgcQxNVVQQwz-K624lEH_Cwj1DI7NvHZm16P6P0YMsfvE2Jm4a1h2GWGwZlSikgo45BzGJXfxLdPtWBrlq6cJYMfLsjZrUq8XZZOJogZ65kaaYXnYx'
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

# Load the cache, save in global variable
CACHE_DICT = load_cache()

# Cafe Instance
class Cafe:
    ''' Instance Attributes
    --------------------------------------
    id: int
        database auto generated ID (e.g. 145)
    yelpid: string
        distinct ID from Yelp (e.g. 'SGwK1mC95VFWtIvUZLdXEg')
    name: string
        name of the cafe (e.g. 'Bearclaw Coffee')
    rating: float
        Yelp rating of the cafe (e.g. 3.5)
    numberofreviews: int
        number of Yelp reviews (e.g. 39)
    state: string
        state of the cafe (e.g. 'MI')
    city: string
        city of the cafe (e.g. 'Ann Arbor')
    fulladdress: string
        full address of the cafe (e.g. '2460 Washtenaw Ave, Ann Arbor, MI 48104')
    zipcode: int
        zip code of the cafe (e.g. 48104)
    phonenumber: string
        phone number of the cafe (e.g. '(734) 332-7850')
    yelpurl: string
        URL of the cafe on yelp (e.g. 'https://www.yelp.com/biz/bearclaw-coffee-ann-arbor-3?adjust_creative=VF_368K_nLLvE2b2T7zR_g&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=VF_368K_nLLvE2b2T7zR_g')
    '''
    def __init__(self, id, yelpid, name, rating, numberofreviews, state, city, fulladdress, zipcode, phonenumber, yelpurl):
        self.id = id
        self.yelpid = yelpid
        self.name = name
        self.rating = rating
        self.numberofreviews = numberofreviews
        self.state = state
        self.city = city
        self.fulladdress = fulladdress
        self.zipcode = zipcode
        self.phonenumber = phonenumber
        self.yelpurl = yelpurl

# Category Instance
class Category:
    ''' Instance Attributes
    --------------------------------------
    id: int
        database auto generated ID (e.g. 3)
    title: string
        title of the category (e.g. 'Coffee & Tea')
    alias: string
        alias of the category (e.g. 'coffee')
    '''
    def __init__(self, id, title, alias):
        self.id = id
        self.title = title,
        self.alias = alias

# Insert data to given table
def insertDataToDB(table, data):
    if table == 'cafe':
        insert = 'INSERT INTO Cafe VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    elif table == 'category':
        insert = 'INSERT INTO Category VALUES (NULL, ?, ?)'
    elif table == 'cafe_category':
        insert = 'INSERT INTO Cafe_Category VALUES (?, ?)'
  
    CUR.execute(insert, data)
    CONN.commit()
    lastInsertedId= CUR.lastrowid
    return lastInsertedId

# Gets Category with given Alias
def getCategory(alias):
    sql = 'SELECT Id, Title, Alias FROM Category WHERE Alias = "{0}"'.format(alias)
    result = CUR.execute(sql).fetchone()
    return result

# Gets Cafe with given Yelp ID
def getCafeById(yelpid):
    query = f''' 
        SELECT Id, YelpId, Name, Rating, NumberOfReviews, State, City, FullAddress, ZipCode, PhoneNumber, YelpURL   
        FROM Cafe 
        WHERE YelpId = "{yelpid}"
        '''
    result = CUR.execute(query).fetchone()
    return result

# Adds {Cafe, Category} relationship to database by looping through each category
def insertCafeCategories(cafeId, categories):
    for c in categories:
        values = [cafeId, c]
        insertDataToDB('cafe_category', values)

# Gets a list of IDs associated with given categories
def getCategoryIds(categories):
    ids = []
    for c in categories:
        category = getCategory(c['alias'])
        if category == None:
            category_values = [c['title'], c['alias']]
            id = insertDataToDB('category', category_values)
        else:
            id = category[0]
        ids.append(id)
    return ids

# Adds data to database tables
def insertCafes(cafes):
    # TODO: check if cafe exist before insert
    for c in cafes:
        cafe_values = [c['id'], c['name'], c['rating'], c['review_count'], c['location']['state'],
            c['location']['city'], ', '.join(c['location']['display_address']), c['location']['zip_code'], c['display_phone'], c['url']]
        categories = getCategoryIds(c['categories'])
        cafeId = insertDataToDB('cafe', cafe_values)
        insertCafeCategories(cafeId, categories)
    # TODO: test data. delete before submit
    cafes = CUR.execute('SELECT * FROM Cafe').fetchall()
    categories = CUR.execute('SELECT * FROM Category').fetchall()
    relationship = CUR.execute('SELECT * FROM Cafe_Category').fetchall()
    return cafes

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
        'limit': 50,
        # 'offset: 50,
        'sort_by': 'rating'
    }
    results = request(url_params)
    # TODO: continue to request and process more results if # of cafes added != total result count
    businesses = results.get('businesses')
    total_results = results.get('total')
    insertCafes(businesses)
    
    return total_results

# Checks cache to see if give location has been processed before
def make_request_using_cache(location):
    if location in CACHE_DICT.keys():
        # TODO: Change to return top 10 cafe wth given location from database 
        return CACHE_DICT[location]
    else:
        # Saves number of cafes at given location to the cache to indicate that the location has been requested before
        data = searchByLocation(location)
        CACHE_DICT[location] = data
        save_cache(CACHE_DICT)
        # TODO: Change to return top 10 cafe wth given location from database 
        return data

def main():
    while True:
        # Gets user input of location
        location = input('Enter a city, state (e.g. San Francisco, CA or Ann Arbor, MI) or "exit" \n: ')

        if location.lower() == "exit":
            exit()
        else:
            # Exit if encounters HTTP error during API request
            try:
                make_request_using_cache(location)
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