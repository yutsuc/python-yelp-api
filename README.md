# Yelp API Project

This app allows you to get top 10 cafes by input location and displays various plots.

## TL;DR

To get started:

* Create database tables with `Yelp_SQL_Table.py`
* Start the program with `yelp.py`

## What You're Getting
```bash
├── README.md # This file.
├── Yelp_SQL_Table.py # Dataase CREATE statements
└── yelp.py # The program
```

## TODO
finish following methods
- getCafeById(id)
- insertCafeCategories(cafeId, categories)

makes improvements to following methods
- insertCafes - check if cafe exist before insert
- searchByLocation - continue to request and process more results
- make_request_using_cache(location) - return top 10 resesults

## Important
The program makes API requests to Yelp Fusion API. For a list of request parameters and response attributes, you can find it [here](https://www.yelp.com/developers/documentation/v3/business_search)