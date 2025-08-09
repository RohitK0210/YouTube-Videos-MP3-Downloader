import os
import string
from pytube import YouTube, Playlist
from pytube.exceptions import PytubeError, VideoUnavailable
from typing import Optional, Callable
from urllib.error import URLError

def get_video_info(video_link: str) -> dict:
    """
    Get video information without downloading it.
    """
    try:
        yt = YouTube(video_link)
        return {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "thumbnail_url": yt.thumbnail_url,
        }
    except VideoUnavailable:
        raise ValueError("Video is unavailable. It may be private, deleted, or age-restricted.")
    except URLError:
        raise ConnectionError("No internet connection or YouTube is down.")
    except PytubeError as e:
        raise ValueError(f"Invalid YouTube URL or video not available: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

def get_playlist_info(playlist_link: str) -> dict:
    """
    Get playlist information without downloading it.
    """
    try:
        pl = Playlist(playlist_link)
        return {
            "title": pl.title,
            "owner": pl.owner,
            "length": pl.length,
            "views": pl.views,
            "thumbnail_url": pl.videos[0].thumbnail_url if pl.videos else None,
        }
    except VideoUnavailable:
        raise ValueError("The playlist contains unavailable videos.")
    except URLError:
        raise ConnectionError("No internet connection or YouTube is down.")
    except PytubeError as e:
        raise ValueError(f"Invalid YouTube Playlist URL or playlist not available: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

def download_video(
    video_link: str,
    resolution: str = 'highest',
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None
) -> None:
    try:
        yt = YouTube(video_link, on_progress_callback=progress_callback)
        stream = get_video_stream(yt, resolution)

        if not stream:
            if error_callback:
                error_callback(f"No suitable stream found for {resolution} resolution.")
            return

        output_path = output_dir or os.path.join(os.getcwd(), sanitize_filename(yt.author))
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        stream.download(output_path=output_path)

        if completion_callback:
            completion_callback(yt.title)

    except (PytubeError, URLError) as e:
        if error_callback:
            error_callback(f"Pytube/Network error: {e}")
    except OSError as e:
        if error_callback:
            error_callback(f"File system error: {e}. Check permissions or disk space.")
    except Exception as e:
        if error_callback:
            error_callback(f"An unexpected error occurred: {e}")

def download_mp3_stream(
    mp3_stream_link: str,
    output_dir: Optional[str] = 'Songs',
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None
) -> None:
    try:
        yt_mp3 = YouTube(mp3_stream_link, on_progress_callback=progress_callback)
        stream_song = yt_mp3.streams.filter(only_audio=True).first()

        if not stream_song:
            if error_callback:
                error_callback("No audio stream found for this video.")
            return

        output_path = output_dir or 'Songs'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        downloaded_file = stream_song.download(output_path=output_path)
        base, ext = os.path.splitext(downloaded_file)
        new_file = base + '.mp3'
        os.rename(downloaded_file, new_file)

        if completion_callback:
            completion_callback(yt_mp3.title)

    except (PytubeError, URLError) as e:
        if error_callback:
            error_callback(f"Pytube/Network error: {e}")
    except OSError as e:
        if error_callback:
            error_callback(f"File system error: {e}. Check permissions or disk space.")
    except Exception as e:
        if error_callback:
            error_callback(f"An unexpected error occurred: {e}")

def download_playlist(
    playlist_link: str,
    resolution: str = 'highest',
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
    start_index: int = 1,
    end_index: Optional[int] = None
) -> None:
    try:
        yt_pl = Playlist(playlist_link)

        # If no end index, download all videos
        if end_index is None:
            end_index = len(yt_pl.videos)

        # Adjust indices for 0-based list slicing
        start_index = max(1, start_index)
        end_index = min(len(yt_pl.videos), end_index)

        videos_to_download = yt_pl.videos[start_index - 1:end_index]

        for i, video in enumerate(videos_to_download):
            try:
                # Update progress with playlist info
                playlist_progress_callback = lambda stream, chunk, bytes_remaining: progress_callback(stream, chunk, bytes_remaining, i + start_index, len(yt_pl.videos))

                download_video(
                    video.watch_url,
                    resolution,
                    output_dir,
                    playlist_progress_callback,
                    completion_callback,
                    error_callback
                )
            except Exception as e:
                if error_callback:
                    error_callback(f"Error downloading video {video.title}: {e}")

    except (PytubeError, URLError) as e:
        if error_callback:
            error_callback(f"Pytube/Network error with playlist: {e}")
    except Exception as e:
        if error_callback:
            error_callback(f"An unexpected error occurred with the playlist: {e}")

def get_video_stream(video: YouTube, resolution: str):
    if resolution == 'highest':
        return video.streams.get_highest_resolution()
    else:
        return video.streams.filter(res=f"{resolution}p", progressive=True).first()

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be used as a valid filename.
    """
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    sanitized = filename.translate(translator)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length to avoid issues with file systems
    return sanitized[:100]
