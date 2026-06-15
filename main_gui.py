
"""
Music Library Manager (DLL Frontend)
Requires:
    pip install customtkinter

Place your compiled DLL/SO beside this script and update DLL_PATH.
"""

import ctypes
import customtkinter as ctk
from tkinter import messagebox


DLL_PATH = "./song_engine.dll"   # change if needed


class Backend:
    def __init__(self, path):
        self.lib = ctypes.CDLL(path)

        self.lib.create_album.argtypes = [ctypes.c_char_p]
        self.lib.create_album.restype = ctypes.c_bool

        self.lib.remove_album.argtypes = [ctypes.c_char_p]
        self.lib.remove_album.restype = ctypes.c_bool

        self.lib.change_album_rating.argtypes = [ctypes.c_char_p, ctypes.c_double]
        self.lib.change_album_rating.restype = ctypes.c_bool

        self.lib.add_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
        self.lib.add_song.restype = ctypes.c_bool

        self.lib.remove_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.remove_song.restype = ctypes.c_bool

        self.lib.change_song_rating.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
        self.lib.change_song_rating.restype = ctypes.c_bool

        self.lib.get_all.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.get_all.restype = ctypes.POINTER(ctypes.c_char * 100)

        self.lib.free_matrix.argtypes = [ctypes.c_void_p]

    def get_lines(self, item):
        ptr = self.lib.get_all(item.encode(), b"")
        rows = []
        try:
            for i in range(100):
                text = ptr[i].value.decode(errors="ignore").strip()
                if not text:
                    break
                rows.append(text)
        finally:
            self.lib.free_matrix(ptr)
        return rows


def parse_line(line):
    if " : " not in line:
        return line, 0.0
    name, rating = line.rsplit(" : ", 1)
    try:
        rating = float(rating)
    except Exception:
        rating = 0.0
    return name.strip(), rating


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.backend = Backend(DLL_PATH)

        ctk.set_appearance_mode("dark")
        self.geometry("1200x700")
        self.title("Music Library Manager")

        self.current_album = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.search = ctk.CTkEntry(self.sidebar, placeholder_text="Search albums")
        self.search.pack(fill="x", padx=10, pady=10)
        self.search.bind("<KeyRelease>", lambda e: self.refresh_albums())

        self.album_frame = ctk.CTkScrollableFrame(self.sidebar, width=250)
        self.album_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(self.sidebar, text="New Album", command=self.create_album).pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(self.sidebar, text="Delete Album", command=self.delete_album).pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(self.sidebar, text="Rate Album", command=self.rate_album).pack(fill="x", padx=10, pady=4)

        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.header = ctk.CTkLabel(self.main, text="Select an album", font=("Segoe UI", 24, "bold"))
        self.header.pack(pady=10)

        self.song_frame = ctk.CTkScrollableFrame(self.main)
        self.song_frame.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = ctk.CTkFrame(self.main)
        bottom.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(bottom, text="Add Song", command=self.add_song).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="Delete Song", command=self.delete_song).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="Rate Song", command=self.rate_song).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="Refresh", command=self.refresh_all).pack(side="right", padx=5)

        self.refresh_all()

    def refresh_all(self):
        self.refresh_albums()
        if self.current_album:
            self.show_album(self.current_album)

    def refresh_albums(self):
        for w in self.album_frame.winfo_children():
            w.destroy()

        albums = self.backend.get_lines("albums.txt")
        query = self.search.get().lower()

        for line in albums:
            name, rating = parse_line(line)

            if query and query not in name.lower():
                continue

            txt = f"{name}   ★ {rating:.1f}"
            ctk.CTkButton(
                self.album_frame,
                text=txt,
                anchor="w",
                command=lambda a=name: self.show_album(a)
            ).pack(fill="x", pady=3)

    def show_album(self, album):
        self.current_album = album
        self.header.configure(text=album)

        for w in self.song_frame.winfo_children():
            w.destroy()

        for line in self.backend.get_lines(album):
            name, rating = parse_line(line)

            card = ctk.CTkFrame(self.song_frame)
            card.pack(fill="x", pady=4)

            ctk.CTkLabel(card, text=name, font=("Segoe UI", 15)).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(card, text=f"★ {rating:.1f}").pack(side="right", padx=10)

    def create_album(self):
        dlg = ctk.CTkInputDialog(text="Album name", title="Create Album")
        name = dlg.get_input()
        if name:
            self.backend.lib.create_album(name.encode())
            self.refresh_albums()

    def delete_album(self):
        if not self.current_album:
            return
        if messagebox.askyesno("Delete", f"Delete {self.current_album}?"):
            self.backend.lib.remove_album(self.current_album.encode())
            self.current_album = None
            self.refresh_all()

    def rate_album(self):
        if not self.current_album:
            return
        dlg = ctk.CTkInputDialog(text="Album rating", title="Album Rating")
        value = dlg.get_input()
        try:
            self.backend.lib.change_album_rating(self.current_album.encode(), float(value))
            self.refresh_all()
        except Exception:
            pass

    def add_song(self):
        if not self.current_album:
            return

        win = ctk.CTkToplevel(self)
        win.geometry("300x180")

        song = ctk.CTkEntry(win, placeholder_text="Song name")
        song.pack(fill="x", padx=10, pady=10)

        rating = ctk.CTkEntry(win, placeholder_text="Rating")
        rating.pack(fill="x", padx=10, pady=10)

        def save():
            self.backend.lib.add_song(
                song.get().encode(),
                self.current_album.encode(),
                float(rating.get() or 0)
            )
            win.destroy()
            self.show_album(self.current_album)

        ctk.CTkButton(win, text="Save", command=save).pack(pady=10)

    def delete_song(self):
        if not self.current_album:
            return

        dlg = ctk.CTkInputDialog(text="Song name", title="Delete Song")
        song = dlg.get_input()

        if song:
            self.backend.lib.remove_song(song.encode(), self.current_album.encode())
            self.show_album(self.current_album)

    def rate_song(self):
        if not self.current_album:
            return

        songdlg = ctk.CTkInputDialog(text="Song name", title="Rate Song")
        song = songdlg.get_input()

        if not song:
            return

        ratedlg = ctk.CTkInputDialog(text="Rating", title="Rate Song")
        rating = ratedlg.get_input()

        try:
            self.backend.lib.change_song_rating(
                song.encode(),
                self.current_album.encode(),
                float(rating)
            )
            self.show_album(self.current_album)
        except Exception:
            pass


if __name__ == "__main__":
    App().mainloop()
