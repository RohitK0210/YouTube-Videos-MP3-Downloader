import customtkinter
from tkinter import filedialog, messagebox
import threading
import queue
import re
from downloader import get_video_info, get_playlist_info, download_video, download_mp3_stream, download_playlist
from PIL import Image, ImageTk
import requests
from io import BytesIO

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Frame for URL and Info ---
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.url_label = customtkinter.CTkLabel(self.top_frame, text="YouTube URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = customtkinter.CTkEntry(self.top_frame, placeholder_text="Enter YouTube URL")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.url_entry.bind("<FocusOut>", self.fetch_video_info)

        self.info_frame = customtkinter.CTkFrame(self.top_frame)
        self.info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.thumbnail_label = customtkinter.CTkLabel(self.info_frame, text="")
        self.thumbnail_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        self.title_label = customtkinter.CTkLabel(self.info_frame, text="Title: ", wraplength=400, justify="left")
        self.title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.author_label = customtkinter.CTkLabel(self.info_frame, text="Author: ")
        self.author_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.length_label = customtkinter.CTkLabel(self.info_frame, text="Length: ")
        self.length_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # --- Main Frame for Controls and Output ---
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # --- Controls Frame ---
        self.controls_frame = customtkinter.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.mode_label = customtkinter.CTkLabel(self.controls_frame, text="Download Mode:")
        self.mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.mode_type = customtkinter.StringVar(value="single")
        self.single_radio = customtkinter.CTkRadioButton(self.controls_frame, text="Single Video", variable=self.mode_type, value="single", command=self.toggle_mode)
        self.single_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.playlist_radio = customtkinter.CTkRadioButton(self.controls_frame, text="Playlist", variable=self.mode_type, value="playlist", command=self.toggle_mode)
        self.playlist_radio.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.download_type_label = customtkinter.CTkLabel(self.controls_frame, text="Download Type:")
        self.download_type_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.download_type = customtkinter.StringVar(value="video")
        self.video_radio = customtkinter.CTkRadioButton(self.controls_frame, text="Video", variable=self.download_type, value="video", command=self.toggle_resolution)
        self.video_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.mp3_radio = customtkinter.CTkRadioButton(self.controls_frame, text="MP3", variable=self.download_type, value="mp3", command=self.toggle_resolution)
        self.mp3_radio.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.resolution_label = customtkinter.CTkLabel(self.controls_frame, text="Resolution:")
        self.resolution_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.resolution_menu = customtkinter.CTkOptionMenu(self.controls_frame, values=["highest", "1080", "720", "480", "360"])
        self.resolution_menu.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        self.playlist_options_frame = customtkinter.CTkFrame(self.controls_frame)
        self.playlist_options_frame.grid(row=0, column=3, rowspan=3, padx=10, pady=5, sticky="nsew")

        self.playlist_range_label = customtkinter.CTkLabel(self.playlist_options_frame, text="Playlist Range (optional):")
        self.playlist_range_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.start_index_entry = customtkinter.CTkEntry(self.playlist_options_frame, placeholder_text="Start")
        self.start_index_entry.grid(row=1, column=0, padx=5, pady=5)
        self.end_index_entry = customtkinter.CTkEntry(self.playlist_options_frame, placeholder_text="End")
        self.end_index_entry.grid(row=1, column=1, padx=5, pady=5)

        self.output_dir_label = customtkinter.CTkLabel(self.controls_frame, text="Output Directory:")
        self.output_dir_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.output_dir_button = customtkinter.CTkButton(self.controls_frame, text="Select Directory", command=self.select_output_dir)
        self.output_dir_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.output_dir = ""

        self.download_button = customtkinter.CTkButton(self.controls_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=4, column=2, columnspan=2, padx=10, pady=10, sticky="ew")

        self.toggle_mode()

        # --- Output Frame ---
        self.output_frame = customtkinter.CTkFrame(self.main_frame)
        self.output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)

        self.output_textbox = customtkinter.CTkTextbox(self.output_frame)
        self.output_textbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.output_textbox.configure(state="disabled")

        # --- Status Bar ---
        self.status_bar = customtkinter.CTkFrame(self)
        self.status_bar.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        self.status_label = customtkinter.CTkLabel(self.status_bar, text="Ready")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.progress_bar = customtkinter.CTkProgressBar(self.status_bar)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.status_bar.grid_columnconfigure(1, weight=1)

        # --- Queue for thread communication ---
        self.queue = queue.Queue()
        self.after(100, self.process_queue)

    def fetch_video_info(self, event=None):
        url = self.url_entry.get()
        if not self.is_valid_youtube_url(url):
            return

        # Run in a separate thread to avoid blocking the GUI
        thread = threading.Thread(target=self.run_fetch_info, args=(url,), daemon=True)
        thread.start()

    def run_fetch_info(self, url):
        try:
            self.queue.put(("status", "Fetching info..."))
            if self.mode_type.get() == "single":
                info = get_video_info(url)
                self.queue.put(("video_info", info))
            else:
                info = get_playlist_info(url)
                self.queue.put(("playlist_info", info))
        except Exception as e:
            self.queue.put(("info_error", str(e)))

    def is_valid_youtube_url(self, url):
        video_pattern = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11}$'
        playlist_pattern = r'^(https?://)?(www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+$'

        if self.mode_type.get() == "single":
            return re.match(video_pattern, url)
        else:
            return re.match(playlist_pattern, url)

    def toggle_mode(self):
        if self.mode_type.get() == "single":
            self.start_index_entry.configure(state="disabled")
            self.end_index_entry.configure(state="disabled")
            self.resolution_menu.configure(state="normal")
            self.mp3_radio.configure(state="normal")
        else: # Playlist
            self.start_index_entry.configure(state="normal")
            self.end_index_entry.configure(state="normal")
            # For simplicity, playlist downloads will be video only for now
            self.mp3_radio.configure(state="disabled")
            self.download_type.set("video")
            self.toggle_resolution()

    def toggle_resolution(self):
        if self.download_type.get() == "mp3":
            self.resolution_menu.configure(state="disabled")
        else:
            self.resolution_menu.configure(state="normal")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.output_dir_button.configure(text=self.output_dir)

    def start_download(self):
        url = self.url_entry.get()
        if not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        self.progress_bar.set(0)
        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Starting download...")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

        thread = threading.Thread(target=self.run_download, daemon=True)
        thread.start()

    def progress_callback(self, stream, chunk, bytes_remaining, video_num=None, total_videos=None):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100

        progress_data = {
            "percentage": percentage,
            "video_num": video_num,
            "total_videos": total_videos
        }
        self.queue.put(("progress", progress_data))

    def completion_callback(self, title):
        self.queue.put(("complete", title))

    def error_callback(self, error_message):
        self.queue.put(("error", error_message))

    def process_queue(self):
        try:
            message = self.queue.get_nowait()
            message_type, data = message

            if message_type == "status":
                self.status_label.configure(text=data)
            elif message_type == "video_info":
                self.update_video_info(data)
            elif message_type == "playlist_info":
                self.update_playlist_info(data)
            elif message_type == "info_error":
                self.handle_info_error(data)
            elif message_type == "progress":
                self.update_progress(data)
            elif message_type == "complete":
                self.handle_completion(data)
            elif message_type == "error":
                self.handle_error(data)
            elif message_type == "playlist_complete":
                self.status_label.configure(text="Playlist download complete!")
                self.download_button.configure(state="normal")
                messagebox.showinfo("Success", "Playlist downloaded successfully.")

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def update_video_info(self, info):
        self.title_label.configure(text=f"Title: {info['title']}")
        self.author_label.configure(text=f"Author: {info['author']}")
        self.length_label.configure(text=f"Length: {info['length'] // 60}m {info['length'] % 60}s")

        if info.get("thumbnail_url"):
            # Load thumbnail in a separate thread
            thread = threading.Thread(target=self.load_thumbnail, args=(info['thumbnail_url'],), daemon=True)
            thread.start()

        self.status_label.configure(text="Ready")

    def update_playlist_info(self, info):
        self.title_label.configure(text=f"Playlist: {info['title']}")
        self.author_label.configure(text=f"Channel: {info['owner']}")
        self.length_label.configure(text=f"Total Videos: {info['length']}")

        if info.get("thumbnail_url"):
            # Load thumbnail in a separate thread
            thread = threading.Thread(target=self.load_thumbnail, args=(info['thumbnail_url'],), daemon=True)
            thread.start()

        self.status_label.configure(text="Ready")

    def load_thumbnail(self, url):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img.thumbnail((120, 90))
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_label.configure(image=photo)
            self.thumbnail_label.image = photo
        except Exception as e:
            # Could put a placeholder image here
            pass

    def handle_info_error(self, error_message):
        self.title_label.configure(text="Title: ")
        self.author_label.configure(text="Author: ")
        self.length_label.configure(text="Length: ")
        self.thumbnail_label.configure(image=None)
        self.status_label.configure(text="Error fetching video info.")
        messagebox.showerror("Error", error_message)

    def update_progress(self, progress_data):
        percentage = progress_data["percentage"]
        video_num = progress_data["video_num"]
        total_videos = progress_data["total_videos"]

        self.progress_bar.set(percentage / 100)

        if video_num and total_videos:
            status_text = f"Downloading video {video_num} of {total_videos}... {percentage:.2f}%"
        else:
            status_text = f"Downloading... {percentage:.2f}%"

        self.status_label.configure(text=status_text)

    def handle_completion(self, title):
        # If it was a playlist, the button is re-enabled at the end of the whole playlist
        if self.mode_type.get() == 'single':
            self.status_label.configure(text="Download complete!")
            self.download_button.configure(state="normal")
            messagebox.showinfo("Success", f"'{title}' downloaded successfully.")

        self.log_message(f"Successfully downloaded: {title}")

    def handle_error(self, error_message):
        self.status_label.configure(text="Download failed.")
        self.log_message(f"ERROR: {error_message}")
        self.download_button.configure(state="normal")
        messagebox.showerror("Error", error_message)

    def run_download(self):
        url = self.url_entry.get()
        download_type = self.download_type.get()
        mode = self.mode_type.get()
        resolution = self.resolution_menu.get()
        output_dir = self.output_dir

        try:
            if mode == "single":
                if download_type == "video":
                    download_video(url, resolution, output_dir, self.progress_callback, self.completion_callback, self.error_callback)
                else: # mp3
                    download_mp3_stream(url, output_dir, self.progress_callback, self.completion_callback, self.error_callback)
            else: # playlist
                start_index_str = self.start_index_entry.get()
                end_index_str = self.end_index_entry.get()

                start_index = int(start_index_str) if start_index_str.isdigit() else 1
                end_index = int(end_index_str) if end_index_str.isdigit() else None

                download_playlist(url, resolution, output_dir, self.progress_callback, self.completion_callback, self.error_callback, start_index, end_index)

                # After the loop finishes, re-enable the button
                self.queue.put(("playlist_complete", None))

        except Exception as e:
            self.error_callback(str(e))

    def log_message(self, message):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
