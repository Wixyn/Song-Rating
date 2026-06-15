'''
============================================================
Arq Song Rater — Pure Native C Execution Layer
============================================================
- ZERO File I/O in Python
- 100% C-Backend Routing via ctypes
'''

import os
import sys
import ctypes
import customtkinter as ctk

# ----------------------------------------------------------------
# 1. ENGINE LINKING
# ----------------------------------------------------------------
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
    base_path = sys._MEIPASS
    if hasattr(os, 'add_dll_directory'): os.add_dll_directory(sys._MEIPASS)
else:
    base_path = os.path.abspath(".")

binary_name = "song_engine.dll" if os.name == 'nt' else "song_engine.so"
engine_absolute_path = os.path.join(base_path, binary_name)

try:
    c_engine = ctypes.CDLL(engine_absolute_path)
    # Bindings
    c_engine.free_matrix.argtypes = [ctypes.c_void_p]
    c_engine.create_album.argtypes = [ctypes.c_char_p]
    c_engine.create_album.restype = ctypes.c_bool
    c_engine.remove_album.argtypes = [ctypes.c_char_p]
    c_engine.remove_album.restype = ctypes.c_bool
    c_engine.change_album_rating.argtypes = [ctypes.c_char_p, ctypes.c_double]
    c_engine.change_album_rating.restype = ctypes.c_bool
    c_engine.add_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    c_engine.add_song.restype = ctypes.c_bool
    c_engine.change_song_rating.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    c_engine.change_song_rating.restype = ctypes.c_bool
    c_engine.remove_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    c_engine.remove_song.restype = ctypes.c_bool
    
    C_2D_Matrix_Schema = (ctypes.c_char * 100) * 100
    c_engine.get_all.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    c_engine.get_all.restype = ctypes.POINTER(C_2D_Matrix_Schema)
except Exception as e:
    sys.exit(1)

def to_c_str(s): return s.encode('utf-8') if s else None

# ----------------------------------------------------------------
# 2. REVAMPED UI CLASS
# ----------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CoreEngineGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arq Song Rater Pro")
        self.geometry("950x650")
        self.current_album = None
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_main_content()
        self.refresh_ui()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="Library", font=("Arial", 20, "bold")).pack(pady=25)
        
        # Album Select
        self.album_dropdown = ctk.CTkComboBox(self.sidebar, values=["No Albums"], command=self.on_dropdown_select)
        self.album_dropdown.pack(pady=10, padx=20, fill="x")
        
        # Album Controls
        self.album_rating_input = ctk.CTkEntry(self.sidebar, placeholder_text="New Album Rating...")
        self.album_rating_input.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Update Album Rating", fg_color="#24a0ed", command=self.ui_rate_album).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🗑️ Delete Album", fg_color="#d9534f", command=self.ui_delete_album).pack(pady=20, padx=20, fill="x")
        
        self.new_album_input = ctk.CTkEntry(self.sidebar, placeholder_text="New Album Name...")
        self.new_album_input.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Create Album", fg_color="#2ecc71", command=self.ui_create_album).pack(padx=20, fill="x")

    def setup_main_content(self):
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.header = ctk.CTkLabel(self.main_view, text="Select an Album", font=("Arial", 28, "bold"))
        self.header.pack(pady=20)

        self.table_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Tracklist")
        self.table_frame.pack(fill="both", expand=True, pady=10)

        # Track Controls
        input_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        input_frame.pack(fill="x", pady=10)
        self.song_name_input = ctk.CTkEntry(input_frame, placeholder_text="Song Title")
        self.song_name_input.pack(side="left", fill="x", expand=True, padx=5)
        self.rating_input = ctk.CTkEntry(input_frame, placeholder_text="Rating", width=80)
        self.rating_input.pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Add", width=80, fg_color="#24a0ed", command=self.ui_add_song).pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Update", width=80, fg_color="#24a0ed", command=self.ui_update_song_rating).pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Delete", width=80, fg_color="#555", command=self.ui_delete_song).pack(side="left", padx=5)

    # ----------------------------------------------------------------
    # 3. PURE C-BACKEND CONTROLLER
    # ----------------------------------------------------------------
    def refresh_ui(self):
        # Refresh Dropdown
        matrix_ptr = c_engine.get_all(to_c_str("albums.txt"), None)
        albums = []
        if matrix_ptr:
            for i in range(100):
                line = matrix_ptr.contents[i].value.decode('utf-8', 'ignore').strip()
                if not line: break
                albums.append(line.split(" : ")[0])
            c_engine.free_matrix(matrix_ptr)
        self.album_dropdown.configure(values=albums if albums else ["No Albums Found"])

        # Refresh Song List
        for w in self.table_frame.winfo_children(): w.destroy()
        if self.current_album:
            matrix_ptr = c_engine.get_all(to_c_str(self.current_album), None)
            if matrix_ptr:
                for i in range(100):
                    line = matrix_ptr.contents[i].value.decode('utf-8', 'ignore').strip()
                    if not line: break
                    row = ctk.CTkFrame(self.table_frame)
                    row.pack(fill="x", pady=2, padx=5)
                    ctk.CTkLabel(row, text=line.split(" : ")[0]).pack(side="left", padx=10)
                    ctk.CTkLabel(row, text=f"⭐ {line.split(' : ')[1]}").pack(side="right", padx=10)
                c_engine.free_matrix(matrix_ptr)

    def on_dropdown_select(self, choice):
        self.current_album = choice
        self.header.configure(text=f"Album: {choice}")
        self.refresh_ui()

    def ui_create_album(self):
        c_engine.create_album(to_c_str(self.new_album_input.get().strip()))
        self.refresh_ui()

    def ui_delete_album(self):
        if self.current_album:
            c_engine.remove_album(to_c_str(self.current_album))
            self.current_album = None
            self.refresh_ui()

    def ui_rate_album(self):
        try:
            c_engine.change_album_rating(to_c_str(self.current_album), float(self.album_rating_input.get()))
            self.refresh_ui()
        except: pass

    def ui_add_song(self):
        try:
            c_engine.add_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), float(self.rating_input.get()))
            self.refresh_ui()
        except: pass

    def ui_update_song_rating(self):
        try:
            c_engine.change_song_rating(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), float(self.rating_input.get()))
            self.refresh_ui()
        except: pass

    def ui_delete_song(self):
        c_engine.remove_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album))
        self.refresh_ui()

if __name__ == "__main__":
    CoreEngineGui().mainloop()
