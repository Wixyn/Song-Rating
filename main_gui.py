'''
============================================================
Arq Song Rater — Pure Native C Matrix Core Engine
============================================================
File-handling operations: 100% C Execution Layer
UI Framework: CustomTkinter Layout Engine
'''

import os
import sys
import ctypes
import customtkinter as ctk

# ----------------------------------------------------------------
# 1. PYINSTALLER COMPATIBILITY & DYNAMIC BINARY ENGINE LINKING
# ----------------------------------------------------------------

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(sys._MEIPASS)
else:
    base_path = os.path.abspath(".")

binary_name = "song_engine.dll" if os.name == 'nt' else "song_engine.so"
engine_absolute_path = os.path.join(base_path, binary_name)

try:
    c_engine = ctypes.CDLL(engine_absolute_path)

    # Engine Deallocation
    c_engine.free_matrix.argtypes = [ctypes.c_void_p]
    c_engine.free_matrix.restype = None

    # Core Engine Bindings
    c_engine.create_album.argtypes = [ctypes.c_char_p]
    c_engine.create_album.restype = ctypes.c_bool

    c_engine.remove_album.argtypes = [ctypes.c_char_p]
    c_engine.remove_album.restype = ctypes.c_bool

    c_engine.add_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    c_engine.add_song.restype = ctypes.c_bool

    c_engine.change_song_rating.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    c_engine.change_song_rating.restype = ctypes.c_bool

    c_engine.change_album_rating.argtypes = [ctypes.c_char_p, ctypes.c_double]
    c_engine.change_album_rating.restype = ctypes.c_bool

    c_engine.remove_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    c_engine.remove_song.restype = ctypes.c_bool

    C_2D_Matrix_Schema = (ctypes.c_char * 100) * 100
    c_engine.get_all.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    c_engine.get_all.restype = ctypes.POINTER(C_2D_Matrix_Schema)

except Exception as e:
    print(f"Critical Linking Error: {e}")
    sys.exit(1)

def to_c_str(py_string):
    if py_string is None:
        return None
    return py_string.encode('utf-8')


# ----------------------------------------------------------------
# 2. APPLICATION CONTROLLER LAYER
# ----------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CoreEngineGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arq Song Rater")
        self.geometry("1200x700") 
        self.current_album = None
        self.tracked_albums = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_top_dashboard()
        self.setup_main_view()
        self.refresh_album_dropdown()

    def setup_top_dashboard(self):
        self.dashboard = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="#1e1e24")
        self.dashboard.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(self.dashboard, text="Arq Song Rater", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=30, pady=20)

        self.album_dropdown = ctk.CTkComboBox(self.dashboard, values=["Select Album..."], command=self.on_dropdown_select, width=180, state="readonly")
        self.album_dropdown.pack(side="left", padx=10, pady=20)

        self.album_rating_input = ctk.CTkEntry(self.dashboard, placeholder_text="Album Rating...", width=110)
        self.album_rating_input.pack(side="left", padx=5, pady=20)

        ctk.CTkButton(self.dashboard, text="Rate Album", width=90, fg_color="#24a0ed", command=self.ui_rate_album).pack(side="left", padx=5, pady=20)

        self.new_album_input = ctk.CTkEntry(self.dashboard, placeholder_text="Quick Album Create...", width=180)
        self.new_album_input.pack(side="right", padx=(5, 10), pady=20)
        
        ctk.CTkButton(self.dashboard, text="+ New", width=70, fg_color="#3a3a4a", command=self.ui_create_album).pack(side="right", padx=5, pady=20)
        
        ctk.CTkButton(self.dashboard, text="🗑️ Delete Album", width=110, fg_color="#d9534f", command=self.ui_delete_album).pack(side="right", padx=5, pady=20)

    def setup_main_view(self):
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(self.main_view, text="Select an Album", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        self.table_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Tracklist Index")
        self.table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        self.action_deck = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a", corner_radius=8)
        self.action_deck.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.action_deck.grid_columnconfigure((0, 1), weight=1)

        self.song_name_input = ctk.CTkEntry(self.action_deck, placeholder_text="Track Title...")
        self.song_name_input.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        self.rating_input = ctk.CTkEntry(self.action_deck, placeholder_text="Score (0.0 - 10.0)...")
        self.rating_input.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        btn_subgrid = ctk.CTkFrame(self.action_deck, fg_color="transparent")
        btn_subgrid.grid(row=0, column=2, padx=15, pady=15, sticky="ew")

        ctk.CTkButton(btn_subgrid, text="Save/Add", fg_color="#2ecc71", width=100, command=self.ui_add_song).pack(side="left", padx=4)
        ctk.CTkButton(btn_subgrid, text="Update", fg_color="#24a0ed", width=100, command=self.ui_update_rating).pack(side="left", padx=4)
        ctk.CTkButton(btn_subgrid, text="Delete", fg_color="#d9534f", width=100, command=self.ui_delete_song).pack(side="left", padx=4)

    def bind_mouse_scroll(self, scroll_frame):
        canvas = scroll_frame._parent_canvas
        def manual_scroll(event):
            if event.num == 4: canvas.yview_scroll(-1, "units")
            elif event.num == 5: canvas.yview_scroll(1, "units")
            else: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", manual_scroll)
        canvas.bind_all("<Button-4>", manual_scroll)
        canvas.bind_all("<Button-5>", manual_scroll)

    def refresh_album_dropdown(self):
        matrix_ptr = c_engine.get_all(to_c_str("albums.txt"), 0)
        self.tracked_albums = []
        if matrix_ptr:
            array_data = matrix_ptr.contents
            for i in range(100):
                line = array_data[i].value.decode('utf-8', errors='ignore').strip()
                if not line: break
                self.tracked_albums.append(line.split(" : ")[0])
            c_engine.free_matrix(matrix_ptr)
        self.album_dropdown.configure(values=self.tracked_albums if self.tracked_albums else ["No Albums Found"])

    def refresh_songs_display(self):
        for w in self.table_frame.winfo_children(): w.destroy()
        if not self.current_album: return
        matrix_ptr = c_engine.get_all(to_c_str(self.current_album), 0)
        if not matrix_ptr: return
        array_data = matrix_ptr.contents
        for i in range(100):
            raw = array_data[i].value.decode('utf-8', errors='ignore').strip()
            if not raw: break
            row = ctk.CTkFrame(self.table_frame, fg_color="#212121", corner_radius=6)
            row.pack(fill="x", pady=3, padx=5)
            ctk.CTkLabel(row, text=raw.split(" : ")[0]).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(row, text=f"⭐ {raw.split(' : ')[1]}").pack(side="right", padx=10, pady=10)
        c_engine.free_matrix(matrix_ptr)

    def select_album(self, album):
        self.current_album = album
        c_engine.create_album(to_c_str(album))
        self.header_label.configure(text=f"Album: {album}")
        self.refresh_songs_display()

    def on_dropdown_select(self, choice): self.select_album(choice)

    # Mutation Signals
    def ui_rate_album(self):
        try: 
            val = float(self.album_rating_input.get())
            c_engine.change_album_rating(to_c_str(self.current_album), ctypes.c_double(val))
            self.select_album(self.current_album)
        except: pass

    def ui_create_album(self):
        name = self.new_album_input.get().strip()
        if name:
            c_engine.create_album(to_c_str(name))
            self.refresh_album_dropdown()
            self.select_album(name)

    def ui_delete_album(self):
        if self.current_album:
            c_engine.remove_album(to_c_str(self.current_album))
            self.current_album = None
            self.refresh_album_dropdown()

    def ui_add_song(self):
        try:
            c_engine.add_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), ctypes.c_double(float(self.rating_input.get())))
            self.select_album(self.current_album)
        except: pass

    def ui_update_rating(self):
        try:
            c_engine.change_song_rating(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), ctypes.c_double(float(self.rating_input.get())))
            self.select_album(self.current_album)
        except: pass

    def ui_delete_song(self):
        c_engine.remove_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album))
        self.select_album(self.current_album)

if __name__ == "__main__":
    app = CoreEngineGui()
    app.mainloop()
