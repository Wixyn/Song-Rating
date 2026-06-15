import os
import sys
import ctypes
import customtkinter as ctk

# ----------------------------------------------------------------
# 1. ENGINE LINKING & BINDINGS
# ----------------------------------------------------------------
def get_engine():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    binary_name = "song_engine.dll" if os.name == 'nt' else "song_engine.so"
    path = os.path.join(base_path, binary_name)
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Engine binary not found at {path}")
    
    engine = ctypes.CDLL(path)
    
    # Define C-Function Signatures
    engine.create_album.argtypes = [ctypes.c_char_p]
    engine.add_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    engine.change_song_rating.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
    engine.change_album_rating.argtypes = [ctypes.c_char_p, ctypes.c_double]
    engine.remove_song.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    engine.remove_album.argtypes = [ctypes.c_char_p]
    engine.free_matrix.argtypes = [ctypes.c_void_p]
    
    # Define structure for the 2D matrix
    C_2D_Matrix_Schema = (ctypes.c_char * 100) * 100
    engine.get_all.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    engine.get_all.restype = ctypes.POINTER(C_2D_Matrix_Schema)
    
    return engine

try:
    c_engine = get_engine()
except Exception as e:
    print(f"Engine initialization error: {e}")
    sys.exit(1)

def to_c_str(s): return str(s).encode('utf-8')

# ----------------------------------------------------------------
# 2. APPLICATION CLASS
# ----------------------------------------------------------------
class CoreEngineGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arq Song Rater")
        self.geometry("1100x700")
        self.current_album = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_top_dashboard()
        self.setup_main_view()
        self.refresh_album_dropdown()

    def setup_top_dashboard(self):
        self.dashboard = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="#1e1e24")
        self.dashboard.grid(row=0, column=0, sticky="ew")
        
        self.album_dropdown = ctk.CTkComboBox(self.dashboard, values=["Select Album..."], command=self.on_dropdown_select, width=180)
        self.album_dropdown.pack(side="left", padx=15, pady=20)

        self.album_rate_in = ctk.CTkEntry(self.dashboard, placeholder_text="Album Rating...", width=100)
        self.album_rate_in.pack(side="left", padx=5, pady=20)
        
        ctk.CTkButton(self.dashboard, text="Rate Album", width=90, fg_color="#24a0ed", command=self.ui_rate_album).pack(side="left", padx=5, pady=20)
        
        ctk.CTkButton(self.dashboard, text="🗑️ Delete", width=80, fg_color="#d9534f", command=self.ui_delete_album).pack(side="right", padx=(5, 30), pady=20)
        ctk.CTkButton(self.dashboard, text="+ New", width=80, fg_color="#3a3a4a", command=self.ui_create_album).pack(side="right", padx=5, pady=20)
        self.new_album_input = ctk.CTkEntry(self.dashboard, placeholder_text="New Album Name...", width=150)
        self.new_album_input.pack(side="right", padx=5, pady=20)

    def setup_main_view(self):
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.header_label = ctk.CTkLabel(self.main_view, text="Select an Album", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w")

        self.table_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Tracks")
        self.table_frame.grid(row=1, column=0, sticky="nsew", pady=10)

        self.action_deck = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        self.action_deck.grid(row=2, column=0, sticky="ew")
        self.song_name_input = ctk.CTkEntry(self.action_deck, placeholder_text="Track Title")
        self.song_name_input.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.rating_input = ctk.CTkEntry(self.action_deck, placeholder_text="Rating")
        self.rating_input.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(self.action_deck, text="Save/Add", fg_color="#2ecc71", command=self.ui_add_song).pack(side="left", padx=5)
        ctk.CTkButton(self.action_deck, text="Update", fg_color="#24a0ed", command=self.ui_update_rating).pack(side="left", padx=5)
        ctk.CTkButton(self.action_deck, text="Delete", fg_color="#d9534f", command=self.ui_delete_song).pack(side="left", padx=5)

    def refresh_album_dropdown(self):
        matrix_ptr = c_engine.get_all(to_c_str("albums.txt"), None)
        albums = []
        if matrix_ptr:
            for i in range(100):
                line = matrix_ptr.contents[i].value.decode('utf-8', 'ignore').strip()
                if not line: break
                albums.append(line.split(" : ")[0])
            c_engine.free_matrix(matrix_ptr)
        self.album_dropdown.configure(values=albums if albums else ["No Albums Found"])

    def on_dropdown_select(self, choice):
        self.current_album = choice
        self.header_label.configure(text=f"Album: {choice}")
        self.refresh_songs_display()

    def refresh_songs_display(self):
        for w in self.table_frame.winfo_children(): w.destroy()
        if not self.current_album or self.current_album == "No Albums Found": return
        
        matrix_ptr = c_engine.get_all(to_c_str(self.current_album), None)
        if matrix_ptr:
            for i in range(100):
                line = matrix_ptr.contents[i].value.decode('utf-8', 'ignore').strip()
                if not line: break
                row = ctk.CTkFrame(self.table_frame)
                row.pack(fill="x", pady=2, padx=5)
                parts = line.split(" : ")
                ctk.CTkLabel(row, text=parts[0]).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=f"⭐ {parts[1] if len(parts) > 1 else 'N/A'}").pack(side="right", padx=10)
            c_engine.free_matrix(matrix_ptr)

    def ui_rate_album(self):
        if self.current_album:
            try:
                c_engine.change_album_rating(to_c_str(self.current_album), float(self.album_rate_in.get()))
                self.on_dropdown_select(self.current_album)
            except ValueError: pass

    def ui_delete_album(self):
        if self.current_album:
            c_engine.remove_album(to_c_str(self.current_album))
            self.current_album = None
            self.refresh_album_dropdown()

    def ui_create_album(self):
        if self.new_album_input.get():
            c_engine.create_album(to_c_str(self.new_album_input.get()))
            self.refresh_album_dropdown()

    def ui_add_song(self):
        try:
            c_engine.add_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), float(self.rating_input.get()))
            self.refresh_songs_display()
        except ValueError: pass

    def ui_update_rating(self):
        try:
            c_engine.change_song_rating(to_c_str(self.song_name_input.get()), to_c_str(self.current_album), float(self.rating_input.get()))
            self.refresh_songs_display()
        except ValueError: pass

    def ui_delete_song(self):
        c_engine.remove_song(to_c_str(self.song_name_input.get()), to_c_str(self.current_album))
        self.refresh_songs_display()

if __name__ == "__main__":
    CoreEngineGui().mainloop()
