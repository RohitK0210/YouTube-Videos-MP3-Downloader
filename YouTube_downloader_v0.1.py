import os
import string
from pytube import YouTube, Channel, Playlist
from typing import Optional

UNDERLINE = '-' * 100

def download_video(video_link: str, resolution: str = 'highest', output_dir: Optional[str] = None) -> None:
    try:
        yt = YouTube(video_link)
        stream = get_video_stream(yt, resolution)
        if stream:
            print(f'\tChannel Name: {yt.author}')
            print(f'\tChannel URL: {yt.channel_url}')
            print(f'\tVideo Views: {yt.views} views')
            print(UNDERLINE)
            print(f'\tDownloading: {yt.title}...')
            output_path = output_dir or os.path.join(os.getcwd(), sanitize_filename(yt.author))
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            stream.download(output_path=output_path)
            print(f'\t{yt.title} downloaded successfully')
        else:
            print(f'No suitable stream found for {video_link}')
        print(UNDERLINE)
    except Exception as e:
        print(f'Error downloading video: {e}')

def download_playlist(playlist_link: str, resolution: str = 'highest', output_dir: Optional[str] = None) -> None:
    try:
        yt_pl = Playlist(playlist_link)
        for video in yt_pl.videos:
            print(UNDERLINE)
            print(f'\tDownloading: {video.title}...')
            stream = get_video_stream(video, resolution)
            if stream:
                path = output_dir or create_path(yt_pl.owner, yt_pl.title)
                if not os.path.exists(path):
                    os.makedirs(path)
                stream.download(output_path=path)
                print(f'\t{video.title} downloaded successfully')
            else:
                print(f'No suitable stream found for {video.title}')
            print(UNDERLINE)
    except Exception as e:
        print(f'Error downloading playlist: {e}')

def download_mp3_stream(mp3_stream_link: str, output_dir: Optional[str] = 'Songs') -> None:
    try:
        yt_mp3 = YouTube(mp3_stream_link)
        print(f'\tDownloading: {yt_mp3.title}...')
        stream_song = yt_mp3.streams.get_by_itag(140).download(output_path=output_dir)
        os.rename(stream_song, f'{stream_song[:-4]}.mp3')
        print(f'\t{yt_mp3.title} downloaded successfully')
        print(UNDERLINE)
    except Exception as e:
        print(f'Error downloading song: {e}')

def download_mp3_streams_custom(mp3_stream_links: str, output_dir: Optional[str] = 'Playlist Music') -> None:
    try:
        yt_pl_mp3 = Playlist(mp3_stream_links)
        display_playlist_info(yt_pl_mp3)
        start_index, end_index = get_custom_indices()
        for video in yt_pl_mp3.videos[start_index - 1:end_index]:
            print(UNDERLINE)
            print(f'\tDownloading: {video.title}...')
            songs = video.streams.get_by_itag(140).download(output_path=output_dir)
            os.rename(songs, f'{songs[:-4]}.mp3')
            print(f'\t{video.title} downloaded successfully')
            print(UNDERLINE)
    except Exception as e:
        print(f'Error downloading songs: {e}')

def download_playlist_custom(playlist_link_ct: str, resolution: str = 'highest', output_dir: Optional[str] = None) -> None:
    try:
        yt_pl_ct = Playlist(playlist_link_ct)
        display_playlist_info(yt_pl_ct)
        start_index, end_index = get_custom_indices()
        for video in yt_pl_ct.videos[start_index - 1:end_index]:
            print(UNDERLINE)
            print(f'\tDownloading: {video.title}...')
            stream = get_video_stream(video, resolution)
            if stream:
                path = output_dir or create_path(yt_pl_ct.owner, yt_pl_ct.title)
                if not os.path.exists(path):
                    os.makedirs(path)
                stream.download(output_path=path)
                print(f'\t{video.title} downloaded successfully')
            else:
                print(f'No suitable stream found for {video.title}')
            print(UNDERLINE)
    except Exception as e:
        print(f'Error downloading videos: {e}')

def get_video_stream(video, resolution: str):
    if resolution == 'highest':
        return video.streams.get_highest_resolution()
    else:
        itag_mapping = {
            '1080p': 137, '720p': 22, '480p': 135,
            '360p': 18, '240p': 133, '144p': 160
        }
        try:
            return video.streams.get_by_itag(itag_mapping[resolution])
        except KeyError:
            print(f'Resolution {resolution} not available. Falling back to highest resolution.')
            return video.streams.get_highest_resolution()

def create_path(owner: str, title: str) -> str:
    sanitized_title = sanitize_filename(title)
    return os.path.join(os.getcwd(), f'{sanitize_filename(owner)} Playlist', sanitized_title)

def sanitize_filename(filename: str) -> str:
    return filename.translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')

def display_playlist_info(playlist) -> None:
    print(UNDERLINE)
    print(f'\tTotal Videos in Playlist: {playlist.length}')
    print(f'\tChannel Name: {playlist.owner}')
    print(f'\tPlaylist Title: {playlist.title}')
    print(f'\tTotal Views: {playlist.views} views')
    print(f'\tLast Updated: {playlist.last_updated}')
    print(UNDERLINE)

def get_custom_indices() -> tuple:
    start_index = int(input('\tEnter Starting Index: '))
    end_index = int(input('\tEnter Ending Index: '))
    return start_index, end_index

def main() -> None:
    while True:
        menu = (
            "\t1): Download YouTube Video\n"
            "\t2): Download YouTube Playlist\n"
            "\t3): Download YouTube MP3 Song\n"
            "\t4): Download YouTube MP3 Playlist with Custom Settings\n"
            "\t5): Download YouTube Playlist with Custom Settings\n"
            "\t6): Exit"
        )
        print(menu)
        print(UNDERLINE)
        user_choice = int(input("\tChoose an option (1, 2, 3, 4, 5, 6): "))
        print(UNDERLINE)
        
        if user_choice in {1, 2, 5}:
            resolution = input("\tEnter desired resolution (1080p, 720p, 480p, 360p, 240p, 144p, or highest): ").strip().lower()
            output_dir = input("\tEnter output directory (leave blank for default): ").strip() or None

        actions = {
            1: lambda: download_video(input('\tEnter a YouTube Video URL: '), resolution, output_dir),
            2: lambda: download_playlist(input('\tEnter a Playlist URL: '), resolution, output_dir),
            3: lambda: download_mp3_stream(input('\tEnter a YouTube Video (Song) URL: ')),
            4: lambda: download_mp3_streams_custom(input('\tEnter a Playlist URL: ')),
            5: lambda: download_playlist_custom(input('\tEnter a Playlist URL: '), resolution, output_dir),
            6: exit
        }
        
        action = actions.get(user_choice)
        if action:
            action()
        else:
            print(f'\tInvalid choice: {user_choice}. Please try again!')

if __name__ == "__main__":
    main()
