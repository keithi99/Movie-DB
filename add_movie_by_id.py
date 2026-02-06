import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets.scrolled import ScrolledText
import requests
import json
import sys


def App(master):

    def add_title(movie_data):
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
        movie_id =  entry.get()
        print(movie_id)
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=20f3d33b09ca122983eff57b3a146602"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            print(data["title"], data["release_date"])

            movie_data = data["title"] + " " +  data["release_date"]

            mb = Messagebox.okcancel(movie_data, "Add this title?")
            if mb == 'OK':
                print("Adding this title...")
                add_title(data)

            sys.exit()
            # show_question(message, title=' ', parent=None, alert=False, **kwargs)

    root = ttk.Frame(master, padding=50)
    label = ttk.Label(root, text="Movie Id")
    label.pack()
    entry = ttk.Entry(root, width=10)
    entry.pack()
    button = ttk.Button(root, text="Search", command=search)
    button.pack(pady=5)





    return root

if __name__ == "__main__":
    app = ttk.Window("Add New Movie")
    bagel = App(app)
    bagel.pack(fill=BOTH, expand=YES)

    app.mainloop()