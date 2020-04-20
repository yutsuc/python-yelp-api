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
        self.title = title
        self.alias = alias

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
        for city in cache.keys():
            for index, item in enumerate(cache[city]):
                # Convert dict to Cafe object
                instance = object.__new__(Cafe)
                for key, value in item.items():
                    setattr(instance, key, value)
                cache[city][index] = instance
        return cache
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    # Convert object to dict
    contents_to_write = json.dumps(cache, default=lambda x: x.__dict__)
    cache_file.write(contents_to_write)
    cache_file.close()

# Load the cache, save in global variable
CACHE_DICT = load_cache()

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
def getCategoryByAlias(alias):
    sql = 'SELECT Id, Title, Alias FROM Category WHERE Alias = "{0}"'.format(alias)
    result = CUR.execute(sql).fetchone()
    if result != None:
        return Category(result[0], result[1], result[2])
    return result

# Gets Cafe with given Yelp ID
def getCafeByYelpId(yelpid):
    query = f''' 
        SELECT Id, YelpId, Name, Rating, NumberOfReviews, State, City, FullAddress, ZipCode, PhoneNumber, YelpURL   
        FROM Cafe 
        WHERE YelpId = "{yelpid}"
        '''
    result = CUR.execute(query).fetchone()
    if result != None:
        return Cafe(result[0], result[1], result[2], result[3], result[4], result[5],
            result[6], result[7], result[8], result[9], result[10])
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
        category = getCategoryByAlias(c['alias'])
        if category == None:
            category_values = [c['title'], c['alias']]
            id = insertDataToDB('category', category_values)
        else:
            id = category.id
        ids.append(id)
    return ids

# Adds data to database tables
def insertCafes(cafes):
    cafeList = []
    for c in cafes:
        cafe = getCafeByYelpId(c['id'])
        if cafe == None:
            # Only need to do inserts if Cafe hasn't been added to database before
            yelpid = c['id']
            name = c['name']
            rating = c['rating']
            reviewcount = c['review_count']
            state = c['location']['state']
            city = c['location']['city']
            address = ', '.join(c['location']['display_address'])
            zipcode = c['location']['zip_code']
            phone = c['display_phone']
            url = c['url']
            cafe_values = [yelpid, name, rating, reviewcount, state, city, address, zipcode, phone, url]
            categories = getCategoryIds(c['categories'])
            cafeId = insertDataToDB('cafe', cafe_values)
            insertCafeCategories(cafeId, categories)
            cafe = Cafe(cafeId, yelpid, name, rating, reviewcount, state, city, address, zipcode, phone, url)
        cafeList.append(cafe)
    return cafeList

# Sends request to Yelp Fusion API, Business Endpoint
def request(url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(API_HOST, SEARCH_PATH)
    headers = {
        'Authorization': 'Bearer %s' % API_KEY,
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

# Searches for coffee shops at given location
# Process results and store each item in the database
# Returns top 10 result to be stored in the cache
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
    cafes = insertCafes(results.get('businesses'))
    # return first 10
    return cafes[:10]

# Checks cache to see if give location has been processed before
def make_request_using_cache(location):
    if location in CACHE_DICT.keys():
        return CACHE_DICT[location]
    else:
        # Saves top 10 cafes at given location to the cache
        data = searchByLocation(location)
        CACHE_DICT[location] = data
        save_cache(CACHE_DICT)
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
                top10 = make_request_using_cache(location.lower())
                for item in top10:
                    print('{0} ({1})'.format(item.name, item.rating))
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