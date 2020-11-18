"""
Go to "AFI's 100 Years... 100 Movies -- 10th Anniversary edition,
The 100 Greatest American Films Of All Time" site to get list of
movies which will be used to search the movie database api
"""

# imports
from selenium import webdriver
import time
import pandas as pd
import CONFIG

# set URL for the page to goto
URL = "https://www.afi.com/afis-100-years-100-movies-10th-anniversary-edition/"

# initialize the webdriver object
driver = webdriver.Chrome(CONFIG.WEBDRIVER_PATH)

# have the driver go to the provided URL
driver.get(URL)

# wait 2 seconds for elements on the site to load
time.sleep(2)

# look for cookies button and click it
accept_element = driver.find_element_by_class_name("mgbutton")
accept_element.click

# wait 2 seconds for cookies bar to close
time.sleep(2)

# find list of movies
movies_element = driver.find_element_by_class_name("list_tab_content")
movie_rows = movies_element.find_elements_by_class_name("single_list")

# initialize list to hold movie titles
movies = []

# loop through movies, if row is empty pass
# otherwise create a list with the rank, title, and year
# then append that list to the movies list
for row in movie_rows:
    movie_title = row.find_element_by_tag_name("h6").text
    if movie_title == "":
        pass
    else:
        label = movie_title.split(" ", 1)
        movie_label = label[-1]
        title_list = movie_label.split("(")
        movie = [label[0].replace(".", ""), title_list[0].rstrip(), title_list[-1][:-1]]
        movies.append(movie)

# close the webdriver
driver.close()

# convert the list to a pandas dataframe and save it as a csv
df = pd.DataFrame(movies, columns=['Rank', 'Title', 'Year'])
df.to_csv(CONFIG.path + "top100.csv", index=False)

