import os
import string
from pytube import YouTube, Channel, Playlist

lines = '-'*100
def download_video(video_link):
    try:
        yt = YouTube(video_link)
        stream = yt.streams.get_highest_resolution()
        print(f'\tChannel Name Is: {yt.author}')
        print(f'\tChannel URL: {yt.channel_url}')
        print(f'\tThis Video Views Is: {yt.views} views')
        print(lines)
        print(f'\t{yt.title} Downloading...')
        yt_channel_name = yt.channel_url
        yt_channel_obj = Channel(yt_channel_name)
        stream.download(output_path=f'{yt_channel_obj.channel_name}')
        print(f'\t{yt.title} Download Successfully')
        print(lines)

    except Exception as e:
        print(f'Error downloading video: {e}')

def download_playlist(playlist_link):
    try:
        yt_pl = Playlist(playlist_link)
        for video in yt_pl.videos:
            print(lines)
            print(f'\t{video.title} Is Downloading...')
            filteringStreams = video.streams.filter(file_extension='mp4', progressive=True)
            resolutions = [stream.resolution for stream in filteringStreams]
            highest_resolution = max(resolutions, default=None, key=lambda res: int(res[:-1]))
            path = f'{yt_pl.owner} Playlist/{yt_pl.title}'.translate(str.maketrans('','',string.punctuation)) 
            if(int(highest_resolution[:-1]) == 1080):
                video.streams.get_by_itag(137).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 720):
                video.streams.get_by_itag(22).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 360):
                video.streams.get_by_itag(18).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 144):
                video.streams.get_by_itag(160).download(output_path=path)
            else:
                print("The available resolutions are lower than 1080p.")
                print("Please choose a different video.")    
            print(f'\t{video.title} Is Download Successfully')
            print(lines)
    except Exception as e:
        print(f'Error downloading playlist: {e}')

def download_MP3_Stream(mp3Stream_link):
    try:
        yt_mp3 = YouTube(mp3Stream_link)
        print(f'\t{yt_mp3.title} Downloading...')
        stream_song =yt_mp3.streams.get_by_itag(140).download(output_path=f'Songs')
        os.rename(stream_song, f'{stream_song[:-4]}.mp3')
        print(f'\t{yt_mp3.title} Downlaod Successfully')
        print(lines)
    except Exception as e:
        print(f'Error Downloading Song: {e}')

def download_MP3_Streams_Custom(mp3Stream_links):
    try:
        yt_pl_mp3 = Playlist(mp3Stream_links)
        print(lines)
        print(f'\t👉 Total Videos of the Playlist is: {yt_pl_mp3.length} Videos')
        print(f'\t👉 Channel Name Is: {yt_pl_mp3.owner}')
        print(f'\t👉 Playlist Title Is: {yt_pl_mp3.title}')
        print(f'\t👉 Playlist Total Views Is: {yt_pl_mp3.views} Views')
        print(f'\t👉 Playlist Last Update on: {yt_pl_mp3.last_updated}')
        print(lines)
        start_index = int(input('\tEnter Starting Index: '))
        end_index = int(input('\tEnter Ending Index: '))
        for video in yt_pl_mp3.videos[start_index - 1: end_index]:
            print(lines)
            print(f'\t{video.title} Is Downloading...')
            songs = video.streams.get_by_itag(
                140).download(output_path=f'Playlist Music')
            os.rename(songs, f'{songs[:-4]}.mp3')
            print(f'\t{video.title} Is Download Successfully')

    except Exception as e:
        print(f'Error Downloading Songs: {e}')
    
def download_Playlist_Custom(playlist_link_ct):
    try:
        yt_pl_ct = Playlist(playlist_link_ct)
        print(lines)
        print(f'\t👉 Total Videos of the Playlist is: {yt_pl_ct.length} Videos')
        print(f'\t👉 Channel Name Is: {yt_pl_ct.owner}')
        print(f'\t👉 Playlist Title Is: {yt_pl_ct.title}')
        print(f'\t👉 Playlist Total Views Is: {yt_pl_ct.views} Views')
        print(lines)
        start_index = int(input('\tEnter Starting Index: '))
        end_index = int(input('\tEnter Ending  Index: '))
        for video in yt_pl_ct.videos[start_index-1:end_index]:
            print(lines)
            print(f'\t{video.title} Is Downloading...')
            filteringStreams = video.streams.filter(file_extension='mp4', progressive=True)
            resolutions = [stream.resolution for stream in filteringStreams]
            highest_resolution = max(resolutions, default=None, key=lambda res: int(res[:-1]))
            path = f'{yt_pl_ct.owner} Playlist/{yt_pl_ct.title}'.translate(str.maketrans('','',string.punctuation)) 
            if(int(highest_resolution[:-1]) == 1080):
                video.streams.get_by_itag(137).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 720):
                video.streams.get_by_itag(22).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 360):
                video.streams.get_by_itag(18).download(output_path=path)
            elif(int(highest_resolution[:-1]) == 144):
                video.streams.get_by_itag(160).download(output_path=path)
            else:
                print("The available resolutions are lower than 1080p.")
                print("Please choose a different video.")
            print(f'\t{video.title} Is Download Successfully')
        print(lines)
    except Exception as e:
        print(f'Error Downloading Videos: {e}')



def main():
    while True:
        menus = '''\t1): Download YouTube Video\n\t2): Download YouTube Playlist\n\t3): Download YouTube MP3 Songs\n\t4): Download YouTube MP3 Playlist Custom Settings:\n\t5): Download YouTube Playlist Custom Settings:\n\t6): Exit'''
        print(menus)
        print(lines)

        user_choice = int(input("\tChoose Any One Condition (1, 2, 3, 4, 5, 6): "))
        print(under_line)

        actions = {
            1: lambda: download_video(input('\tEnter a YouTube Video URL: ')),
            2: lambda: download_playlist(input('\tEnter a Playlist Video URL: ')),
            3: lambda: download_MP3_Stream(input('\tEnter a YouTube Video(Song) URL: ')),
            4: lambda: download_MP3_Streams_Custom(input('\tEnter a YouTube Video(Song) URL: ')),
            5: lambda: download_Playlist_Custom(input('\tEnter a YouTube Playlist Video URL: ')),
            6: exit
        }
        actions = actions.get(user_choice)
        if(actions):
            actions()
        else:
            print(f"\tInvalid choice: {user_choice}. Please try again!")

if __name__ == "__main__":
    main()
