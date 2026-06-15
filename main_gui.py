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
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
# ----------------------------------------------------------------
# 1. PYINSTALLER COMPATIBILITY & DYNAMIC BINARY ENGINE LINKING
# ----------------------------------------------------------------
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

binary_name = "song_engine.dll" if os.name == 'nt' else "song_engine.so"
engine_absolute_path = os.path.join(base_path, binary_name)

try:
    c_engine = ctypes.CDLL(engine_absolute_path)

    c_engine.create_album.argtypes = [ctypes.c_char_p]
    c_engine.create_album.restype = ctypes.c_bool

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
    print(f"Critical Linking Error: Could not load target {binary_name} dynamic engine.")
    sys.exit(1)

def to_c_str(py_string):
    if py_string is None:
        return None
    return py_string.encode('utf-8')


# ----------------------------------------------------------------
# 2. APPLICATION CONTROLLER LAYER (Diversified UX Layout)
# ----------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CoreEngineGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Arq Song Rater")
        self.geometry("1200x700") # Slightly widened window to elegantly sit the new dashboard inputs
        self.current_album = None
        self.tracked_albums = []

        # Single top dashboard panel layout with wide data viewport below
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_top_dashboard()
        self.setup_main_view()
        self.refresh_album_dropdown()

    def setup_top_dashboard(self):
        """Top panel managing rapid switching via dropdowns and creation hooks"""
        self.dashboard = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="#1e1e24")
        self.dashboard.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        brand_label = ctk.CTkLabel(self.dashboard, text="Arq Song Rater", font=ctk.CTkFont(size=20, weight="bold"))
        brand_label.pack(side="left", padx=(30, 15), pady=20)

        # Dropdown selector
        self.album_dropdown = ctk.CTkComboBox(
            self.dashboard, 
            values=["Select Album..."], 
            command=self.on_dropdown_select,
            width=180,
            state="readonly"
        )
        self.album_dropdown.pack(side="left", padx=10, pady=20)

        # ADDED FEATURE: Dedicated Input Control deck to run change_album_rating directly
        self.album_rating_input = ctk.CTkEntry(self.dashboard, placeholder_text="Album Rating...", width=110)
        self.album_rating_input.pack(side="left", padx=5, pady=20)

        rate_album_btn = ctk.CTkButton(self.dashboard, text="Rate Album", width=90, fg_color="#24a0ed", hover_color="#007acc", command=self.ui_rate_album)
        rate_album_btn.pack(side="left", padx=5, pady=20)

        # Fast Inline Album Creator
        self.new_album_input = ctk.CTkEntry(self.dashboard, placeholder_text="Quick Album Create...", width=180)
        self.new_album_input.pack(side="right", padx=(5, 30), pady=20)
        
        add_album_btn = ctk.CTkButton(self.dashboard, text="+ New", width=70, fg_color="#3a3a4a", command=self.ui_create_album)
        add_album_btn.pack(side="right", padx=5, pady=20)

    def setup_main_view(self):
        """Assembles data-tables display and item mutation controls"""
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(self.main_view, text="Select an Album from the dropdown to start", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Main Table Index Viewport
        self.table_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Tracklist Index")
        self.table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        # Bind mouse scroll wheel execution directly to this workspace viewport
        self.bind_mouse_scroll(self.table_frame)

        # Streamlined Input Deck for Songs
        self.action_deck = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a", corner_radius=8)
        self.action_deck.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.action_deck.grid_columnconfigure((0, 1), weight=1)

        self.song_name_input = ctk.CTkEntry(self.action_deck, placeholder_text="Track Title Name...")
        self.song_name_input.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        self.rating_input = ctk.CTkEntry(self.action_deck, placeholder_text="Score Metric (0.0 - 10.0)...")
        self.rating_input.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        btn_subgrid = ctk.CTkFrame(self.action_deck, fg_color="transparent")
        btn_subgrid.grid(row=0, column=2, padx=15, pady=15, sticky="ew")

        add_btn = ctk.CTkButton(btn_subgrid, text="Save/Add", fg_color="#2ecc71", hover_color="#27ae60", width=100, command=self.ui_add_song)
        add_btn.pack(side="left", padx=4)

        rate_btn = ctk.CTkButton(btn_subgrid, text="Update", fg_color="#24a0ed", hover_color="#007acc", width=100, command=self.ui_update_rating)
        rate_btn.pack(side="left", padx=4)

        delete_btn = ctk.CTkButton(btn_subgrid, text="Delete", fg_color="#d9534f", hover_color="#c9302c", width=100, command=self.ui_delete_song)
        delete_btn.pack(side="left", padx=4)

    # ----------------------------------------------------------------
    # 3. UNIVERSAL MOUSE SCROLL BINDING LAYER
    # ----------------------------------------------------------------
    def bind_mouse_scroll(self, scroll_frame):
        """Recursively hooks mouse wheel changes to fire scrolling events safely across platforms"""
        canvas = scroll_frame._parent_canvas
        
        def manual_scroll(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", manual_scroll)
        canvas.bind_all("<Button-4>", manual_scroll)
        canvas.bind_all("<Button-5>", manual_scroll)

    # ----------------------------------------------------------------
    # 4. DIRECT C MEMORY MATRIX READ INTERCHANGES
    # ----------------------------------------------------------------
    def refresh_album_dropdown(self):
        """Asks C for albums.txt block data and maps strings to populate dropdown values"""
        matrix_ptr = c_engine.get_all(to_c_str("albums.txt"), None)
        self.tracked_albums = []

        if matrix_ptr:
            array_data = matrix_ptr.contents
            for i in range(100):
                album_line = array_data[i].value.decode('utf-8', errors='ignore').strip()
                if not album_line:
                    break
                album_name = album_line.split(" : ")[0] if " : " in album_line else album_line
                self.tracked_albums.append(album_name)

            try:
                ctypes.CDLL(None).free(matrix_ptr)
            except AttributeError:
                pass

        if self.tracked_albums:
            self.album_dropdown.configure(values=self.tracked_albums)
            if not self.current_album:
                self.album_dropdown.set(self.tracked_albums[0])
                self.select_album(self.tracked_albums[0])
        else:
            self.album_dropdown.configure(values=["No Albums Found"])
            self.album_dropdown.set("No Albums Found")

    def refresh_songs_display(self):
        """Asks your C function to pull song names and ratings out of the active album file"""
        for w in self.table_frame.winfo_children(): 
            w.destroy()
            
        if not self.current_album: 
            return

        matrix_ptr = c_engine.get_all(to_c_str(self.current_album), None)
        if not matrix_ptr: 
            return
            
        array_data = matrix_ptr.contents
        valid_index = 0

        for i in range(100):
            raw_line = array_data[i].value.decode('utf-8', errors='ignore').strip()
            if not raw_line: 
                break

            if " : " in raw_line:
                song_title, rating = raw_line.split(" : ", 1)
            else:
                song_title = raw_line
                rating = "N/A"

            row = ctk.CTkFrame(self.table_frame, fg_color="#212121" if valid_index % 2 == 0 else "#1a1a1a", corner_radius=6)
            row.pack(fill="x", pady=3, padx=5)

            ctk.CTkLabel(row, text=f"   🎵  {song_title}", font=ctk.CTkFont(size=14)).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(row, text=f"⭐ {rating}   ", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffd700").pack(side="right", padx=10, pady=10)
            
            valid_index += 1

        if valid_index == 0:
            ctk.CTkLabel(self.table_frame, text="Album is empty.", font=ctk.CTkFont(slant="italic"), text_color="gray").pack(pady=30)

        try:
            ctypes.CDLL(None).free(matrix_ptr)
        except AttributeError:
            pass

    def select_album(self, album_name):
        """Applies active variables, reads native total scoring matrix metrics, and re-draws headers"""
        if album_name == "No Albums Found" or album_name == "Select Album...":
            return

        self.current_album = album_name
        c_engine.create_album(to_c_str(album_name))
        
        album_rating = "N/A"
        matrix_ptr = c_engine.get_all(to_c_str("albums.txt"), None)
        if matrix_ptr:
            array_data = matrix_ptr.contents
            for i in range(100):
                line = array_data[i].value.decode('utf-8', errors='ignore').strip()
                if not line:
                    break
                if " : " in line:
                    name, rating = line.split(" : ", 1)
                    if name == album_name:
                        album_rating = rating
                        break
            try:
                ctypes.CDLL(None).free(matrix_ptr)
            except AttributeError:
                pass

        self.header_label.configure(text=f"Album: {album_name}  [⭐ {album_rating}]")
        self.refresh_songs_display()

    def on_dropdown_select(self, choice):
        self.select_album(choice)

    # ----------------------------------------------------------------
    # 5. NATIVE MUTATION SIGNALS
    # ----------------------------------------------------------------
    def ui_rate_album(self):
        """Direct execution layer connecting your C engine's standalone album ranking updater"""
        if not self.current_album:
            return
        
        rating_str = self.album_rating_input.get().strip()
        try:
            val = float(rating_str)
        except ValueError:
            return

        # Explicitly triggers your native custom engine mutation logic!
        c_engine.change_album_rating(to_c_str(self.current_album), ctypes.c_double(val))
        self.album_rating_input.delete(0, 'end')
        
        # Redraw the application layout parameters to instantly display the updated overall score
        self.select_album(self.current_album)

    def ui_create_album(self):
        name = self.new_album_input.get().strip()
        if not name: 
            return
            
        c_engine.create_album(to_c_str(name))
        self.new_album_input.delete(0, 'end')
        self.current_album = name
        self.refresh_album_dropdown()
        self.album_dropdown.set(name)
        self.select_album(name)

    def ui_add_song(self):
        if not self.current_album: 
            return
            
        song = self.song_name_input.get().strip()
        rating_str = self.rating_input.get().strip()
        
        try: 
            val = float(rating_str)
        except ValueError: 
            return

        c_engine.add_song(to_c_str(song), to_c_str(self.current_album), ctypes.c_double(val))
        
        self.song_name_input.delete(0, 'end')
        self.rating_input.delete(0, 'end')
        self.select_album(self.current_album)

    def ui_update_rating(self):
        if not self.current_album: 
            return
            
        song = self.song_name_input.get().strip()
        rating_str = self.rating_input.get().strip()
        
        try: 
            val = float(rating_str)
        except ValueError: 
            return

        c_engine.change_song_rating(to_c_str(song), to_c_str(self.current_album), ctypes.c_double(val))
        
        self.song_name_input.delete(0, 'end')
        self.rating_input.delete(0, 'end')
        self.select_album(self.current_album)

    def ui_delete_song(self):
        if not self.current_album: 
            return
            
        song = self.song_name_input.get().strip()
        if not song: 
            return

        c_engine.remove_song(to_c_str(song), to_c_str(self.current_album))
        self.song_name_input.delete(0, 'end')
        self.select_album(self.current_album)


if __name__ == "__main__":
    app = CoreEngineGui()
    app.mainloop()
