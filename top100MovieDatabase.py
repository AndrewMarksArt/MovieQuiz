"""
Use the movie databse api to pull information based on the
AFI top 100 movies and save the data for the Movie Quiz App

Process:
1. load top 100 csv
2. grab title and year, dont need rank for now
3. make api call using title and year
4. get movie id
5. get image URL's
    1. poster
    2. backdrop
6. use movie id to get movie details
    1. budget
    2. genres -> name and id?
    3. production companies
        1. name
        2. logo path
        3. id
    4. tag line
    5. vote avg -> this is a rating out of 10
7. use movie id to get credits
    1. cast -> everyone is listed, way to many, will need to figure out how to limit
        1. name
        2. gender
        3. department -> Acting / director / etc.
        4. character name
        5. character image from movie
        6. id -> can be used to search later for what other movies they have been in


From above we will have:
1. rank in AFI Top 100
2. Title
3. Year released
4. Poster Image
5. Background Image
6. Budget
7. Genres
8. Production Company name
9. Production Company Logo Image
10. Movie Tag Line
11. Movie rating out of 10
12. Cast Members
    1. Name
    2. gender
    3. department
    4. character name
    5. character image from movie
    6. actor id

"""

import CONFIG
import json
import requests
import pandas as pd


def search_movies(api_key, query, year, include_adult="false", language='en-US', page=1):
    """
    make an api call to the movie database movie search. need to return movie ID and image URLs.

    :param api_key: string, required.
    :param language: string, optional, default is "en-US" for English.
    :param query: string, required. The movie title.
    :param page: int, optional, default is 1 Max is 100, which page to query.
    :param include_adult: boolean, optional, default is false. Set to True to include
                          pornographic movies in results.
    :param year: int, optional, should be used to help limit results and return better matches.

    :return: tuple, (afi_rank, movie_title, year, movie_id, poster_url, background_url)
    """

    api_url = f"{CONFIG.API_MOVIE_SEARCH_BASE}api_key={api_key}&language={language}&" \
              f"query={query}&page={page}&include_adult={include_adult}&year={year}"

    response = requests.get(api_url)

    return json.loads(response.content.decode('utf-8'))


def get_movie_details(api_key, movie_id, language="en-US"):
    """

    :param api_key:
    :param movie_id:
    :param language:
    :return:
    """
    api_url = f"{CONFIG.API_MOVIE_GET_DETAILS}{movie_id}?api_key={api_key}&language={language}"

    response = requests.get(api_url)
    return json.loads(response.content.decode('utf-8'))


def get_movie_cast(api_key, movie_id):
    """

    :param api_key:
    :param movie_id:
    :return:
    """
    api_url = f"{CONFIG.API_MOVIE_GET_DETAILS}{movie_id}/credits?api_key={api_key}"
    response = requests.get(api_url)
    return json.loads(response.content.decode('utf-8'))


# set api_key
key = CONFIG.API_KEY

# load AFI top 100 csv as a Pandas DataFrame
df = pd.read_csv(CONFIG.path+"top100.csv")

# initialize list to hold results
results = []

for i in range(len(df)):
    # get movie rank, title, and year in row
    row = df.loc[i].tolist()

    # initialize movie dictionary
    movie = {}

    # set movie rank from row[0]
    movie["AFI_top_100_rank"] = int(row[0])

    # use title (row[1]) and year made (row[2]) to search movies
    temp = search_movies(key, row[1], row[2])

    # returns list of objects --> we only need the first 1
    temp = temp["results"][0]

    # set movie search keys and values
    movie["id"] = temp["id"]
    movie["title"] = temp["title"]
    movie["year"] = int(row[2])
    movie["background_path"] = temp["backdrop_path"]
    movie["poster_path"] = temp["poster_path"]
    movie["user_rating"] = temp["vote_average"]

    # use "movie ID" to get details
    temp = get_movie_details(key, movie["id"])

    # set movie details keys and values
    movie["genres"] = temp["genres"]
    movie["budget"] = temp["budget"]
    movie["overview"] = temp["overview"]
    movie["production_companies"] = temp["production_companies"]
    movie["revenue"] = temp["revenue"]
    movie["tagline"] = temp["tagline"]

    # search for the movies cast using the "movie ID"
    temp = get_movie_cast(key, movie["id"])

    # there maybe a significant number of cast members, get first 10
    temp = temp["cast"][:10]

    # initialize list to hold cast members
    cast = []

    # loop through cast members and set key and values for each
    for cast_member in temp:
        # initialize individual actor dictionary
        actor = {}

        # set actor keys and values
        actor["id"] = cast_member["id"]
        actor["name"] = cast_member["name"]
        actor["gender"] = cast_member["gender"]
        actor["character"] = cast_member["character"]
        actor["profile_image"] = cast_member["profile_path"]

        # append actor dictionary to cast list
        cast.append(actor)

    # add cast list to movie dictionary
    movie["cast"] = cast

    # add movie to top 100 list
    results.append(movie)

# print out all results
print(json.dumps(results, indent=4))

# save results
with open(CONFIG.path+"AFI_top_100_details.json", "w") as file:
    json.dump(results, file)


