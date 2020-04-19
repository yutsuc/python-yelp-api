
import sqlite3

conn = sqlite3.connect("YelpCafe.sqlite")
cur = conn.cursor()

drop_cafe = 'DROP TABLE IF EXISTS "Cafe"'
drop_category = 'DROP TABLE IF EXISTS "Category"'
drop_cafe_category = 'DROP TABLE IF EXISTS "Cafe_Category"'

create_cafe = '''
    CREATE TABLE IF NOT EXISTS "Cafe" (
        "Id"                TEXT PRIMARY KEY UNIQUE,
        "Name"              TEXT NOT NULL,
        "Rating"            REAL,
        "NumberOfReviews"   INTEGER,
        "State"             TEXT,
        "City"             TEXT,
        "FullAddress"       TEXT,
        "ZipCode"           INTEGER,
        "PhoneNumber"       TEXT,
        "YelpURL"           TEXT
    );
'''
create_category = '''
    CREATE TABLE IF NOT EXISTS "Category" (
        "Id"                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"             TEXT NOT NULL,
        "Alias"             TEXT NOT NULL
    );
'''
create_cafe_category = '''
    CREATE TABLE IF NOT EXISTS "Cafe_Category" (
        "CafeId"            TEXT NOT NULL,
        "CategoryId"        INTEGER NOT NULL,
        FOREIGN KEY(CafeId) REFERENCES Cafe(Id)
        FOREIGN KEY(CategoryId) REFERENCES Category(Id)
    );
'''

cur.execute(drop_cafe)
cur.execute(drop_category)
cur.execute(drop_cafe_category)

cur.execute(create_cafe)
cur.execute(create_category)
cur.execute(create_cafe_category)

conn.commit()
