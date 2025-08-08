import customtkinter
from downloader import download_video, download_mp3_stream
from tkinter import filedialog
import sys

class Logger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.insert("end", text)
        self.textbox.see("end")

    def flush(self):
        pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("720x480")

        # Create a grid layout with 2 columns and 1 row
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a frame for the controls on the left
        self.frame_left = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nsw")

        # Create a frame for the output on the right
        self.frame_right = customtkinter.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure the grid layout for the left frame
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row with weight as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        # Add a title to the left frame
        self.title_label = customtkinter.CTkLabel(self.frame_left, text="Downloader Options", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(20, 10))

        # Add a URL entry field
        self.url_label = customtkinter.CTkLabel(self.frame_left, text="YouTube URL:")
        self.url_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.url_entry = customtkinter.CTkEntry(self.frame_left, placeholder_text="Enter YouTube URL")
        self.url_entry.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Add a download type radio button
        self.download_type_label = customtkinter.CTkLabel(self.frame_left, text="Download Type:")
        self.download_type_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.download_type = customtkinter.StringVar(value="video")
        self.video_radio = customtkinter.CTkRadioButton(self.frame_left, text="Video", variable=self.download_type, value="video")
        self.video_radio.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="w")
        self.mp3_radio = customtkinter.CTkRadioButton(self.frame_left, text="MP3", variable=self.download_type, value="mp3")
        self.mp3_radio.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="w")

        # Add a resolution dropdown
        self.resolution_label = customtkinter.CTkLabel(self.frame_left, text="Resolution:")
        self.resolution_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.resolution_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["1080p", "720p", "480p", "360p", "240p", "144p", "highest"])
        self.resolution_menu.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Add an output directory button
        self.output_dir_label = customtkinter.CTkLabel(self.frame_left, text="Output Directory:")
        self.output_dir_label.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.output_dir_button = customtkinter.CTkButton(self.frame_left, text="Select Directory", command=self.select_output_dir)
        self.output_dir_button.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.output_dir = ""

        # Add a download button
        self.download_button = customtkinter.CTkButton(self.frame_left, text="Download", command=self.download)
        self.download_button.grid(row=12, column=0, padx=20, pady=10, sticky="ew")

        # Configure the grid layout for the right frame
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)

        # Add a textbox for the output
        self.output_textbox = customtkinter.CTkTextbox(self.frame_right)
        self.output_textbox.grid(row=0, column=0, sticky="nsew")

        # Redirect stdout to the textbox
        sys.stdout = Logger(self.output_textbox)

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.output_dir_button.configure(text=self.output_dir)

    def download(self):
        self.output_textbox.delete("1.0", "end")
        url = self.url_entry.get()
        download_type = self.download_type.get()
        resolution = self.resolution_menu.get()

        if download_type == "video":
            download_video(url, resolution, self.output_dir)
        else:
            download_mp3_stream(url, self.output_dir)

if __name__ == "__main__":
    app = App()
    app.mainloop()
