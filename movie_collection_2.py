from tkinter.messagebox import askokcancel, showerror
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter as tk
import json
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, messagebox, filedialog
from genres import genre_id_list
import webbrowser
API_KEY = "20f3d33b09ca122983eff57b3a146602"
db_file = "movies_db.json"
print_file = "movies_print.txt"

class MovieApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.all_movies = []
        self.display_list = []
        self.genre_list = []
        self.filter_id = 0
        self.selected_movie_id = ""
        self.movie_count = 0
        self.GENRES = []
        self.title("Movie Collection")
        self.geometry("1300x700")
        self.selected_genre = ""
        self.poster_image = None
        self.watched_var = tb.BooleanVar(value=False)
        self.db_watched_var = tb.BooleanVar(value=False)

        self.my_style = ttk.Style()
        self.my_style.configure("Dynamic.TLabel", foreground="green")  # Initial color
        self.my_style.configure("TCheckbutton", indicatorbackground="black", indicatorforeground="white",
                        background="black", foreground="blue")
        self.get_genres()

        # create list of genre names
        for item in genre_id_list:
            name = item["name"]
            self.GENRES.append(name)
        self.main = tb.Frame(self, padding=10, )
        self.main.pack(fill=BOTH, expand=YES)

        # ---- Movie List ----
        self.list_frame = tb.Frame(self.main, style="warning")
        self.list_frame.pack(side=LEFT, fill=Y)
        self.style.configure("Custom.TLabel", foreground="#000000")
        self.main_title = tb.Label(self.list_frame, text="Movies",
                              font=("Helvetica", 14, "bold"), background="#fc7e0f", style="Custom.TLabel")
        self.main_title.pack(pady=5)
        print(self.GENRES)

        self.add_btn = tk.Button(self.list_frame, text="Add Movie by ID", command=self.add_movie_by_id)
        self.add_btn.pack(pady=5)

        self.print_btn = tk.Button(self.list_frame, text="Print Movie List", command=lambda: self.print_movie_list(self.filtered_movies))
        self.print_btn.pack(pady=5)

        self.genre_cbo = tb.Combobox(self.list_frame, values=self.GENRES, state="readonly")
        self.genre_cbo.current(self.GENRES.index("All Genres"))
        self.genre_cbo.pack(pady=5)
        self.genre_cbo.bind("<<ComboboxSelected>>", self.filter_by_genre)

        self.watched_chk = tb.Checkbutton(self.list_frame, text="Exclude Watched",
                                          command=self.load_movie_list,
                                          variable=self.watched_var,
                                          )

        self.watched_chk.pack(pady=5, padx=5)

        self.scrollbar = tk.Scrollbar(self.list_frame, orient="vertical")
        self.movie_listbox = tk.Listbox(self.list_frame, height=20, width=50,
                                        font=("Helvetica", 14), background="blue", yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.movie_listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill="y")
        self.movie_listbox.pack(fill=Y, expand=YES)
        self.movie_listbox.bind("<<ListboxSelect>>", self.show_movie)

        # get collection from file
        data = []
        with open(db_file, "r") as f:
            data = json.loads(f.read())
        # create MOVIES DB

        added_titles = []
        for movie in data:
           # movie = json.load(item)
            # create full poster path
            poster_path = movie["poster_path"]
            path = f"https://image.tmdb.org/t/p/w185{poster_path}"
            movie["full_poster_path"] = path

            # prevent dups
            if movie["id"] not in added_titles:
                self.all_movies.append(movie)
            added_titles.append(movie["id"])

        # sort movies by title
        self.all_movies = sorted(self.all_movies, key=lambda movie: movie["title"])

        # copy all movies
        self.filtered_movies = self.all_movies[:]
        self.movie_count = len(self.filtered_movies)
        self.main_title.configure(text=f"Movies ({self.movie_count})")

        # display titles
        # for movie in self.filtered_movies:
        #     self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
        #     # if self.filter_id == 0:
            #     self.movie_listbox.insert(END, movie["title"])
            # else:
            #     if self.filter_id in movie["genre_ids"]:
            #         self.movie_listbox.insert(END, movie["title"])

        # ---- Details Frame ----
        self.details = tb.Frame(self.main, padding=10)
        self.details.configure(style="My.TFrame")
        self.details.pack(side=LEFT, fill=BOTH, expand=YES)

        self.poster_label = tb.Label(self.details)
        self.poster_label.pack(pady=5)

        self.title_label = tb.Label(self.details, font=("Noto Serif", 16))
        self.title_label.pack()

        self.info_label = tb.Label(self.details, font=("Helvetica", 10))
        self.info_label.pack(pady=5)

        self.genre_label = tb.Label(self.details, font=("Noto Serif", 16))
        self.genre_label.pack(pady=5)


        self.details_watched_chk = tb.Checkbutton(self.details, text="Watched", variable=self.db_watched_var, command=self.mark_as_watched)


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

        # display list of movies
        self.load_movie_list()

    def print_movie_list(self, movie_data):
        with open(print_file, "w") as f:
            for item in genre_id_list:
                if item["name"] != "All Genres":
                    text = "\n-------------------\n>>>> " + item["name"] + " <<<<\n-------------------\n"
                    f.write(text)
                    for movie in movie_data:
                        if item["id"] in movie["genre_ids"]:
                            title = f"{movie['title']} ({movie['year']})\n"
                            f.write(title)

        messagebox.showinfo("Printed", "List Saved to File")

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
            "watched": False        }

        # load all movies from file
        with open(db_file, "r") as f:
            self.all_movies = json.loads(f.read())

        # append new movie to list of movies
        self.all_movies.append(movie)

        # write movie list to file
        with open(db_file, "w") as f:
            f.write(json.dumps(self.all_movies))

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
            popup.destroy()

            ok = askokcancel("Add Movie?", movie_data)
            if ok:
                print("Adding this title...")
                self.add_movie_to_file(data)

        else:
            showerror("Search Failed", "Movie Not Found!")


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
        # create list of genre names
        for item in genre_id_list:
            name = item["name"]
            self.GENRES.append(name)

    def load_movie_list(self):
        hide_watched = self.watched_var.get()
        # clear out list box
        self.movie_listbox.delete(0, END)

        self.display_list = []
        for movie in self.filtered_movies:
            if hide_watched:
                if not movie["watched"]:
                    # put movie in list box and save it in list of displayed movies
                    self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
                    self.display_list.append(movie)
                else:
                    print("excluding watched - ", movie["title"])
            else:
                # put movie in list box and save it in list of displayed movies
                self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
                self.display_list.append(movie)

        movie_count = len(self.display_list)
        self.main_title.configure(text=f"{self.selected_genre} Movies ({movie_count})")

        # load up movie list box
        # for movie in self.filtered_movies:
        #     self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
        #     self.display_list.append(movie)

    # def load_movie_list(self):
    #     print("Loading Movies List...")
    #     hide_watched = self.watched_var.get()
    #     temp = self.filtered_movies.copy()
    #
    #     self.movie_listbox.delete(0, END)
    #    # self.movie_count = len(self.filtered_movies)
    #    # self.main_title.configure(text=f"{self.selected_genre} Movies ({self.movie_count})")
    #
    #     # load listbox with movies
    #     movie_count = 0
    #     filtered_movies = []
    #     for movie in temp:
    #         print(movie["watched"])
    #         if not movie["watched"]:
    #           # print("movie not watched")
    #             # movie not watched so add it
    #             filtered_movies.append(movie)
    #             #self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
    #             #movie_count += 1
    #         else:
    #             print(f"movie watched {movie['title']}")
    #             if not hide_watched:
    #                 # movie watched but not hiding movies so add it
    #                 filtered_movies.append(movie)
    #                 #self.movie_listbox.insert(END, f"{movie["title"]} ({movie['year']})")
    #                 #movie_count += 1
    #     movie_count = len(filtered_movies)
    #     self.main_title.configure(text=f"{self.selected_genre} Movies ({movie_count})")

    def filter_by_genre(self, event):
        genre_id = 0
        self.selected_genre = self.genre_cbo.get()
        # find the id of the selected genre
        for item in genre_id_list:
            if item["name"] == self.selected_genre:
                genre_id = int(item["id"])
                break

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
        self.load_movie_list()

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

    def mark_as_watched(self):
        print(f"marking watched {self.selected_movie_id}")
        for movie in self.all_movies:
            if movie["id"] == self.selected_movie_id:
                if self.db_watched_var.get():
                    movie["watched"] = True
                else:
                    movie["watched"] = False

    def delete_movie(self, popup):
        def close_popups():
            top.destroy()
            popup.destroy()

        for movie in self.all_movies:
            if movie["id"] == self.selected_movie_id:
                print(f"removing {self.selected_movie_id}")
                self.all_movies.remove(movie)
                top = tb.Toplevel()
                top.title("Movie Deleted")
                top.geometry("300x300")
                tb.Label(top, text="Movie Deleted", font=('helvetica', 20)).pack(pady=10)
                tb.Button(top, text="Close", command=close_popups).pack(pady=10)



    def on_poster_click(self, event):
        print(f"on_poster_click {self.selected_movie_id}")
        top = tb.Toplevel()
        top.title("Options")
        top.geometry("300x200")
        tb.Button(top, text="Delete Movie", command=lambda: self.delete_movie(top)).pack(pady=10)
        tb.Button(top, text="Close", command=top.destroy).pack(pady=10)

    def show_movie(self, event):
        # show movie poster and details
        index = self.movie_listbox.curselection()
        if not index:
            return

        # index into the displayed list of movies
        movie = self.display_list[index[0]]
        self.selected_movie_id = movie["id"]
        overview_details = self.get_overview(movie["id"])

        # get movie genres for details frame
        genre_str = ""
        for genre_id in movie["genre_ids"]:
            for genre in genre_id_list:
                if genre["id"] == genre_id:
                    genre_str += genre["name"] + ", "

        genre_str = genre_str[:-2]

        # Load poster image
        response = requests.get(movie["full_poster_path"])
        img = Image.open(BytesIO(response.content))
        img = img.resize((200, 290))
        self.poster_image = ImageTk.PhotoImage(img)
        self.poster_label.config(image=self.poster_image)
        self.poster_label.bind("<Button-1>", self.on_poster_click)

        self.title_label.config(text=movie["title"])

        vote_avg = round(float(overview_details["vote_average"]), 1) * 10
        vote_avg = int(vote_avg)

        if vote_avg <= 50:
            style = "danger"
        elif (vote_avg > 50) and (vote_avg <= 65):
            style = "warning"
        else:
            style = "success"

        self.details_watched_chk.pack(pady=5)
        if movie["watched"]:
            self.db_watched_var.set(True)
        else:
            self.db_watched_var.set(False)

        self.avg_vote.configure(amountused=vote_avg, bootstyle=style)
        self.avg_vote.pack()


        # self.vote_avg_label.config(text=f"Vote Avg. {vote_avg}%", font=("Helvetica", 14, "bold"))
        #
        self.info_label.config(text=movie["year"], font=("Helvetica", 14))
        self.genre_label.config(text=genre_str, font=("Helvetica", 14))

        self.imdb_btn.config(text="Open in TMDB", bootstyle="primary", command=lambda: self.open_tmdb(movie["id"]))
        self.imdb_btn.pack(pady=5)

        self.desc_box.config(state="normal", font=("Helvetica", 14))
        self.desc_box.delete("1.0", END)
        self.desc_box.insert(1.0, f"{overview_details['overview']}")
        self.desc_box.pack(pady=5)
        self.desc_box.config(state="disabled")

    def save_and_exit(self):
        print(f"saving db file")
        with open(db_file, "w") as outfile:
            json.dump(self.all_movies, outfile)
        messagebox.showinfo("Data Saved", "Movie DB Saved")
        self.destroy()


if __name__ == "__main__":
    app = MovieApp()
    app.protocol("WM_DELETE_WINDOW", app.save_and_exit)
    app.mainloop()