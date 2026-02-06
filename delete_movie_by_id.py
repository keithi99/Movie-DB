import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets.scrolled import ScrolledText
import requests
import json
import sys


def App(master):
    movies = []

    def load_movies():
        global movies

        with open("movies_db.json", "r") as f:
            movies = json.loads(f.read())

        print(len(movies))

    def delete_title(movie_data):
        movies = []
        year = movie_data["release_date"][:4]
        # get all genres
        genre_ids = []
        for genre in movie_data["genres"]:
            genre_ids.append(genre["id"])

        movie = {
            "title": movie_data["title"],
            "genre_ids": genre_ids,
            "id": movie_data["id"],
            "year": year,
            "poster_path": movie_data["poster_path"],
        }

        print(movie)

        with open("movies_db.json", "r") as f:
            movies = json.loads(f.read())

       # print(movies)

        movies.append(movie)

        with open("movies_db.json", "w") as f:
            f.write(json.dumps(movies))

        print("Movie Added")

        sys.exit()

    def search():
        global movies

        movie_id =  int(entry.get())
        print(type(movie_id))

        # find movie in movie DB
        for movie in movies:
            if movie["id"] == movie_id:
                movies.remove(movie)
                print("Movie Removed")

        with open("movies_db.json", "w") as f:
            f.write(json.dumps(movies))



    root = ttk.Frame(master, padding=50)
    label = ttk.Label(root, text="Movie Id")
    label.pack()
    entry = ttk.Entry(root, width=10)
    entry.pack()
    button = ttk.Button(root, text="Search", command=search)
    button.pack(pady=5)

    load_movies()

    return root

if __name__ == "__main__":
    app = ttk.Window("Add New Movie")
    bagel = App(app)

    bagel.pack(fill=BOTH, expand=YES)

    app.mainloop()