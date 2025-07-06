from pathlib import Path
import yt_dlp
from os import listdir
from os.path import isfile, join
from datetime import datetime
import json

from helpers.string_helper import sanitize_filename

def exception_extract_yt_code(report):
    # TODO Handle this garbage better
    return report[(report.find('[youtube] ') + len('[youtube] ')) : (report.find('[youtube] ') + len('[youtube] ')) + 11]

def link_extract_yt_code(url): # TODO needs a little bit improvements
    return url.replace('https://www.youtube.com/watch?v=', '')

class YouTubeEnvironment:
    CACHE_SAVED_IN = 'cache/youtube/'

    def __init__(self, data):
        self.data = data

        ydl_opts = { # TODO maybe also grab from config?
            'skip_download': True,
            'quiet': True,
            'force_generic_extractor': False,
            'extract_flat': 'in_playlist'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
            i_got = ytdl.extract_info(data.url, download = False)
            if i_got == None:
                self.error = True
                return
            entries = list(i_got.get('entries'))
            self.title = i_got['title']
            self.id = i_got['id']
            self.entries = entries
            self.playlist_length = len(self.entries)
            self.error = False
            self.cache_load()

    def analyse(self):
        Path(self.data.backup_location).mkdir(parents=True, exist_ok=True)
        self.only_files = [f for f in listdir(self.data.backup_location) if isfile(join(self.data.backup_location, f))] # TODO handle maybe with ID as this is garbage
        self.to_download = [f"{entrie['url']}" for entrie in self.entries if entrie['title'] + f'.{self.data.extension}' not in self.only_files and all(code not in f"{entrie['url']}" for code in self.unavailable_videos) and all(code not in f"{entrie['url']}" for code in self.validation_required_videos)]
        self.to_download = [i for i in self.to_download if all(link_extract_yt_code(i) not in url for url in self.downloaded_urls) ]
        self.cache_save()

    def cache_save(self):
        Path(self.CACHE_SAVED_IN).mkdir(parents=True, exist_ok=True)
        with open(self.CACHE_SAVED_IN + sanitize_filename(self.id) + '.json', 'w') as file:
            file.write(json.dumps({'title': self.title, 'unavailable_videos' : self.unavailable_videos, 'validation_required_videos': self.validation_required_videos, 'downloaded_urls': self.downloaded_urls}))

    def cache_load(self):
        if Path(self.CACHE_SAVED_IN + sanitize_filename(self.id) + '.json').is_file():
            with open(self.CACHE_SAVED_IN + sanitize_filename(self.id) + '.json', 'r') as file:
                contents = json.loads(file.read())
                self.unavailable_videos = contents.get('unavailable_videos')
                if self.unavailable_videos == None:
                    self.unavailable_videos = []
                self.validation_required_videos = contents.get('validation_required_videos')
                if self.validation_required_videos == None:
                    self.validation_required_videos = []
                self.downloaded_urls = contents.get('downloaded_urls')
                if self.downloaded_urls == None:
                    self.downloaded_urls = []
                print(f'unavailable videos: {self.unavailable_videos}\nValidation Required Videos: {self.validation_required_videos}')
        else:
            self.unavailable_videos = []
            self.validation_required_videos = []
            self.downloaded_urls = []

    def start(self):
        print(f'Running {self.title}')
        _ydl_opts = {
            'skip_download': False,
            'quiet': True,
            'extract_flat': False,
            'outtmpl': self.data.backup_location + self.data.file_template, # TODO handle this shit better
            'extract_audio': True,
            'format': 'bestaudio[ext=m4a]', 
            'verbose': False
        }
        with yt_dlp.YoutubeDL(self.data.options['ydl_opts'] if self.data.options['ydl_opts'] != None else _ydl_opts) as ytdl:
            for url in self.to_download:
                try:
                    ytdl.download(url)
                    self.downloaded_urls.append(link_extract_yt_code(url))
                    self.cache_save() # TODO temp shitz
                except Exception as e: # TODO Handle exceptions better, also it is possible that there are more exceptions that were not considered
                    report = repr(e)
                    if 'The current session has been rate-limited' in report or "This video has been removed for violating YouTube's Terms of Service" in report:
                        raise Exception('The current session has been rate-limited')
                    if 'Video unavailable.' in report:
                        self.failed_download(e, self.unavailable_videos) 
                    elif 'This video is only available to Music Premium members' in report or 'Sign in to confirm your age.' in report or "Private video." in report:
                        self.failed_download(e, self.validation_required_videos)
                    else:
                        print(f'{datetime.now()} - {report}')
                        return False
                    
    def failed_download(self, exception, append_list):
        report = repr(exception)
        code_found = exception_extract_yt_code(report)
        append_list.append(code_found)
        self.cache_save()
        print(f'{datetime.now()} - {report}')

    def generate_m3u(self):
        # TODO
        print('m3u generator not implemented... yet!')
