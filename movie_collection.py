from tkinter.messagebox import askokcancel, showerror

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter as tk
import json
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, messagebox
from genres import genre_id_list
import webbrowser

API_KEY = "20f3d33b09ca122983eff57b3a146602"


class MovieApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.all_movies = []
        self.filtered_movies = []
        self.filter_id = 0
        self.movie_count = 0

        self.title("Movie Collection")
        self.geometry("1300x700")

        self.poster_image = None

        self.get_genres()
        style = ttk.Style()
        style.configure("Dynamic.TLabel", foreground="green")  # Initial color

        # create list of genre names
        for item in genre_id_list:
            name = item["name"]
            self.GENRES.append(name)

    def add_movie_to_file(self, movie_data):
        movies = []
        # save this movie's genres
        genre_ids = []
        for genre in movie_data["genres"]:
            genre_ids.append(genre["id"])

        year = movie_data["release_date"][:4]
        movie = {
            "title": movie_data["title"],
            "genre_ids": genre_ids,
            "id": movie_data["id"],
            "year": year,
            "poster_path": movie_data["poster_path"],
        }

        # load all movies from file
        with open("movies_db.json", "r") as f:
            movies = json.loads(f.read())

        # append new movie to list of movies
        movies.append(movie)

        # write movie list to file
        with open("movies_db.json", "w") as f:
            f.write(json.dumps(movies))

        print("Movie Added")
        messagebox.showinfo("Movie Added", "Movie Added")

    def search_for_id(self, entry, popup):
        movie_id = entry.get()
        if movie_id == "":
            return

        if movie_id.isnumeric():
            movie_id = int(entry.get())
        print(movie_id)


        # see if movie already exists in DB
        for movie in self.all_movies:
            if movie["id"] == movie_id:
                messagebox.showerror("Movie Exists", "Movie Already Exists")
                return

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=20f3d33b09ca122983eff57b3a146602"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            print(data["title"], data["release_date"])

            movie_data = data["title"] + " " + data["release_date"]

            ok = askokcancel("Add Movie?", movie_data)
            if ok:
                print("Adding this title...")
                self.add_movie_to_file(data)
        else:
            showerror("Search Failed", "Movie Not Found!")

        popup.destroy()
        print("popup destroy")


    def add_movie_by_id(self):
        # open dialog window
        """Creates a custom popup window with specific widgets."""
        popup = tk.Toplevel(self)
        popup.title("Add New Movie")
        popup.geometry("250x150")

        # Optional: make the Toplevel window modal (user must close it first)
        popup.grab_set()

        label = tk.Label(popup, text="TMDB or IMDB Movie ID")
        label.pack(pady=3)

        entry = tk.Entry(popup, width=20)
        entry.pack(pady=3)
        entry.focus_set()

        close_button = tk.Button(popup, text="Search TMDB", command=lambda:self.search_for_id(entry, popup))
        close_button.pack(pady=10)


    def get_genres(self):
        self.GENRES = []
        # create list of genre names
        for item in genre_id_list:
            name = item["name"]
            self.GENRES.append(name)



        def filter_by_genre(event):
            genre_id = 0
            genre = self.genre_cbo.get()
            print(genre)
            for item in genre_id_list:
                if item["name"] == genre:
                    genre_id = int(item["id"])
                    break

            print(genre_id)
            self.filtered_movies = []

            if genre_id == 0:
                # no filter applied so use all movies
                self.filtered_movies = self.all_movies[:]
            else:
                # filter to selected genre
                for movie in self.all_movies:
                    if genre_id in movie["genre_ids"]:
                        self.filtered_movies.append(movie)

            #print(self.filtered_movies)

            self.movie_listbox.delete(0, END)
            self.movie_count = len(self.filtered_movies)
            main_title.configure(text=f"{genre} Movies ({self.movie_count})")

            # load listbox with movies
            for movie in self.filtered_movies:
                self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
            # for movie in self.MOVIES:
            #     if self.filter_id == 0:
            #         self.movie_listbox.insert(END, movie["title"])
            #     else:
            #         if self.filter_id in movie["genre_ids"]:
            #             self.movie_listbox.insert(END, movie["title"])

            #
            # # filter movie list to selected genre
            # filtered = []
            # for movie in self.MOVIES:
            #     if genre_id in movie["genre_ids"]:
            #         filtered.append(movie)
            #
            # print(filtered)
            #
            # # display titles
            # self.movie_listbox.delete(0, END)
            # for movie in filtered:
            #     self.movie_listbox.insert(END, movie["title"])



        main = tb.Frame(self, padding=10, )
        main.pack(fill=BOTH, expand=YES)

        # ---- Movie List ----
        list_frame = tb.Frame(main, style="warning")
        list_frame.pack(side=LEFT, fill=Y)
        self.style.configure("Custom.TLabel", foreground="#000000")
        main_title = tb.Label(list_frame, text="Movies",
                              font=("Helvetica", 14, "bold"), background="#fc7e0f", style="Custom.TLabel")
        main_title.pack(pady=5)
        print(self.GENRES)

        self.add_btn = tk.Button(list_frame, text="Add Movie by ID", command=self.add_movie_by_id)
        self.add_btn.pack(pady=5)

        self.genre_cbo = tb.Combobox(list_frame, values=self.GENRES, state="readonly")
        self.genre_cbo.current(self.GENRES.index("All Genres"))
        self.genre_cbo.bind("<<ComboboxSelected>>", filter_by_genre)
        self.genre_cbo.pack(pady=5)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.movie_listbox = tk.Listbox(list_frame, height=20, width=50,
                                        font=("Helvetica", 14), background="blue", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.movie_listbox.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.movie_listbox.pack(fill=Y, expand=YES)
        self.movie_listbox.bind("<<ListboxSelect>>", self.show_movie)

        # get collection from file
        data = []
        with open(f"movies_db.json", "r") as f:
            data = json.loads(f.read())
        # create MOVIES DB

        added_titles = []
        for movie in data:
           # movie = json.load(item)
            # create full poster path
            poster_path = movie["poster_path"]
            path = f"https://image.tmdb.org/t/p/w185{poster_path}?api_key=20f3d33b09ca122983eff57b3a146602"
            movie["poster_path"] = path
            # prevent dups
            if movie["id"] not in added_titles:
                self.all_movies.append(movie)
            added_titles.append(movie["id"])

        # sort movies by title
        self.all_movies = sorted(self.all_movies, key=lambda movie: movie["title"])

        # copy all movies
        self.filtered_movies = self.all_movies[:]
        self.movie_count = len(self.filtered_movies)
        main_title.configure(text=f"Movies ({self.movie_count})")

        # display titles
        for movie in self.filtered_movies:
            self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
            # if self.filter_id == 0:
            #     self.movie_listbox.insert(END, movie["title"])
            # else:
            #     if self.filter_id in movie["genre_ids"]:
            #         self.movie_listbox.insert(END, movie["title"])


        # ---- Details Frame ----
        self.details = tb.Frame(main, padding=10)
        self.details.configure(style="My.TFrame")
        self.details.pack(side=LEFT, fill=BOTH, expand=YES)

        self.poster_label = tb.Label(self.details)
        self.poster_label.pack(pady=10)

        self.title_label = tb.Label(self.details, font=("Helvetica", 16))
        self.title_label.pack()

        self.info_label = tb.Label(self.details, font=("Helvetica", 10))
        self.info_label.pack(pady=5)

        # self.vote_avg_label = tb.Label(self.details, font=("Helvetica", 16))
        # self.vote_avg_label.pack()

        self.avg_vote = tb.Meter(self.details,metersize=64,
                                 amounttotal=100,
                                 meterthickness=4,
                                 textfont='-size 12 -weight bold',
                                 textright='%',
                                 subtextfont='-size 8 -weight bold',
                                padding=15,
                                amountused=75,
                                metertype=FULL,
                                interactive=False,
                                 showtext=True)
       # self.avg_vote.pack(pady=5)

        self.imdb_btn = tb.Button(self.details)


        self.desc_box = ScrolledText(self.details, wrap=WORD)
        # self.desc_label = tb.Label(
        #     self.details,
        #     wraplength=400,
        #     justify=LEFT
        # )
        #self.desc_box.pack(pady=10)

    def get_overview(self, id):

        print(id)
        overview_details = {
            "overview" : "",
            "vote_average" : ""
        }

        url = f"https://api.themoviedb.org/3/movie/{id}?api_key=20f3d33b09ca122983eff57b3a146602"
        response = requests.get(url)
        if response.status_code == 200:
            movie = json.loads(response.content)
            overview_details["overview"] = movie["overview"]
            overview_details["vote_average"] = movie["vote_average"]

        return overview_details

    def open_tmdb(self, id):
        print(id)
        url = f"https://www.themoviedb.org/movie/{id}"
        print(url)
        webbrowser.open(url)

    def show_movie(self, event):
        # show movie poster and details
        index = self.movie_listbox.curselection()
        if not index:
            return

        movie = self.filtered_movies[index[0]]
        overview_details = self.get_overview(movie["id"])

        # Load poster image
        response = requests.get(movie["poster_path"])
        img = Image.open(BytesIO(response.content))
        img = img.resize((220, 310))
        self.poster_image = ImageTk.PhotoImage(img)
        self.poster_label.config(image=self.poster_image)

        self.title_label.config(text=movie["title"])

        vote_avg = round(float(overview_details["vote_average"]), 1) * 10
        vote_avg = int(vote_avg)

        if vote_avg <= 50:
            style = "danger"
        elif (vote_avg > 50) and (vote_avg <= 65):
            style = "warning"
        else:
            style = "success"

        self.avg_vote.configure(amountused=vote_avg, bootstyle=style)
        self.avg_vote.pack()


        # self.vote_avg_label.config(text=f"Vote Avg. {vote_avg}%", font=("Helvetica", 14, "bold"))
        #
        self.info_label.config(text=movie["year"], font=("Helvetica", 16))

        self.imdb_btn.config(text="Open in TMDB", bootstyle="primary", command=lambda: self.open_tmdb(movie["id"]))
        self.imdb_btn.pack(pady=5)

        self.desc_box.config(state="normal", font=("Helvetica", 14))
        self.desc_box.delete("1.0", END)
        self.desc_box.insert(1.0, f"{overview_details['overview']}")
        self.desc_box.pack(pady=10)
        self.desc_box.config(state="disabled")



if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()
