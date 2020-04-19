
import sqlite3

conn = sqlite3.connect("YelpCafe.sqlite")
cur = conn.cursor()

drop_existing = '''
    DROP TABLE IF EXISTS "Cafe";
    DROP TABLE IF EXISTS "Category";
    DROP TABLE IF EXISTS "Cafe_Category";
'''

create_tables = '''
    CREATE TABLE IF NOT EXISTS "Cafe" (
        "Id"                TEXT PRIMARY KEY UNIQUE,
        "Name"              TEXT NOT NULL,
        "Rating"            REAL,
        "NumberOfReviews"   INTEGER,
        "State"             TEXT,
        "City"              TEXT,
        "FullAddress"       TEXT,
        "ZipCode"           INTEGER,
        "PhoneNumber"       TEXT,
        "YelpURL"           TEXT
    );
    CREATE TABLE IF NOT EXISTS "Category" (
        "Id"                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"             TEXT NOT NULL,
        "Alias"             TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS "Cafe_Category" (
        "CafeId"            TEXT NOT NULL,
        "CategoryId"        INTEGER NOT NULL,
        FOREIGN KEY(CafeId) REFERENCES Cafe(Id)
        FOREIGN KEY(CategoryId) REFERENCES Category(Id)
    );
'''

cur.execute(drop_existing)
cur.execute(create_tables)

conn.commit()
