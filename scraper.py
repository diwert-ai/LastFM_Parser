from requests import get
from bs4 import BeautifulSoup
from csv import writer, QUOTE_ALL
from track import Track
from album import Album
from tqdm import tqdm
from pickle import load, dump
from os.path import exists


class LastFMScraper:
    tags = ['rock', 'hip-hop', 'indie', 'jazz', 'reggae', 'british', 'punk', '80s', 'dance', 'electronic', 'metal',
            'acoustic', 'rnb', 'hardcore', 'country', 'blues', 'alternative', 'classical', 'rap', 'country', 'composer',
            'modern classical', 'neoclassical', 'post-punk', 'russian']

    def __init__(self, csv_file_name, checkpoint_file_name='.lfm_checkpoint',
                 tag_indices=None, total_pages=None, album_pos_start=None,
                 album_pos_end=None, verbose=False):
        self.csv_file_name = csv_file_name
        self.checkpoint_file_name = checkpoint_file_name
        self.tags_indices = tag_indices if tag_indices else tuple(range(len(self.tags)))
        self.total_pages = total_pages if total_pages else 25
        self.album_pos_start = album_pos_start if album_pos_start else 1
        self.album_pos_end = album_pos_end if album_pos_end else 20
        self.verbose = verbose
        self.data_container = list()
        self.checkpoint = None

    @staticmethod
    def get_albums_data(tag, page):
        fm_url = f'https://www.last.fm/tag/{tag}/albums?page={page}'
        fm_page = get(fm_url)
        fm_soup = BeautifulSoup(fm_page.text, 'lxml')
        artist_albums_section = fm_soup.find_all('section', {'id': 'artist-albums-section'})
        albums = artist_albums_section[0].find_all('li', class_='resource-list--release-list-item-wrap')
        return albums

    @staticmethod
    def get_album_metadata(album_href):
        album_page = get(album_href)
        album_soup = BeautifulSoup(album_page.text, 'lxml')
        album_meta = album_soup.find_all('ul', class_='header-metadata-tnew')
        return album_meta, album_soup

    @staticmethod
    def get_album_catalogue_metadata(album_soup):
        album_catalogue = album_soup.find_all('dl', class_='catalogue-metadata')
        album_length = album_release_date = album_tracks_total = None
        if album_catalogue:
            album_catalogue_data = album_catalogue[0].find_all('dd', class_='catalogue-metadata-description')
            description_zero_split = album_catalogue_data[0].get_text().strip().split(',')
            album_tracks_total = int(description_zero_split[0].strip().split()[0])
            if len(description_zero_split) > 1:
                album_length = description_zero_split[1].strip()
            if len(album_catalogue_data) > 1:
                album_release_date = album_catalogue_data[1].get_text().strip()
        return album_length, album_tracks_total, album_release_date

    @staticmethod
    def get_track_scrobbles(track_href):
        track_scrobbles = 0
        track_page = get(track_href)
        track_soup = BeautifulSoup(track_page.text, 'lxml')
        track_data = track_soup.find_all('abbr')
        if len(track_data) > 1:
            track_scrobbles = int(track_data[1].get('title').strip().replace(',', ''))
        return track_scrobbles

    def get_album_tracks_list(self, album_soup):
        album_tracks_list = []
        album_tracks_list_data = album_soup.find_all('section', {'id': 'tracklist'})
        if album_tracks_list_data:
            album_tracks = album_tracks_list_data[0].find_all('tr', class_='chartlist-row')
            for track_pos, track in enumerate(album_tracks, 1):
                track_href_tail = track.find_all('td', class_='chartlist-name')[0].find_all('a')[0].get('href')
                track_href, track_scrobbles = None, 0
                if track_href_tail:
                    track_href = 'https://www.last.fm' + track_href_tail
                    track_scrobbles = self.get_track_scrobbles(track_href)
                track_duration = track.find_all('td', class_='chartlist-duration')[0].get_text().strip()
                if self.verbose:
                    print(f'track href: {track_href}')
                    print(f'track scrobbles: {track_scrobbles}')
                    print(f'processing chartlist-bar text: '
                          f'{track.find_all("td", class_="chartlist-bar")[0].get_text().strip()}')
                chart_list_bar_text = track.find_all("td", class_="chartlist-bar")[0].get_text().strip()
                track_listeners = 0
                if chart_list_bar_text:
                    track_listeners = int(chart_list_bar_text.split()[0].replace(',', ''))
                track_name = track.find_all('td', class_='chartlist-name')[0].get_text().strip()
                album_tracks_list.append(Track(track_pos, track_name, track_duration,
                                               track_listeners, track_scrobbles, track_href))

        return album_tracks_list

    def get_album(self, album_data, album_tag, album_page, album_num):
        album_name = album_data.find_all('h3')[0].get_text().strip()
        album_href = 'https://www.last.fm' + album_data.find_all('a', class_='link-block-target')[0].get('href')
        album_artist = album_data.find_all('p', class_='resource-list--release-list-item-artist')[0].get_text().strip()
        album_cover = album_data.find_all('img')[0].get('src')
        album_aux_text = album_data.find_all('p', class_='resource-list--release-list-item-aux-text')
        album_listeners = int(album_aux_text[0].get_text().strip().split()[0].replace(',', ''))
        album_metadata, album_soup = self.get_album_metadata(album_href)
        album_counters = album_metadata[0].find_all('abbr')
        album_scrobbles = int(album_counters[1].get('title').replace(',', ''))
        album_length, album_tracks_total, album_release_date = self.get_album_catalogue_metadata(album_soup)
        album = Album(album_name, album_href, album_artist, album_cover, album_scrobbles, album_listeners,
                      album_tracks_total,
                      album_length, album_release_date)
        if self.verbose:
            print(f'album processing: {album_name}')
        album.tracks_list = self.get_album_tracks_list(album_soup)
        album.tag = album_tag
        album.page = album_page
        album.num = album_num
        return album

    def write_csv_head(self):
        with open(self.csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = writer(csv_file, delimiter=' ', quotechar='|', quoting=QUOTE_ALL)
            csv_writer.writerow(['album href', 'album tag', 'album page', 'album num', 'album name', 'album artist',
                                 'album cover href', 'album listeners', 'album scrobbles', 'album tracks_total',
                                 'album length', 'album release date', 'track pos', 'track name', 'track duration',
                                 'track listeners', 'track scrobbles', 'track href'])

    def save_data(self, album, start_track_pos):
        if self.verbose:
            print(album)

        for album_track in album.tracks_list[start_track_pos-1:]:
            with open(self.csv_file_name, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = writer(csv_file, delimiter=' ', quotechar='|', quoting=QUOTE_ALL)
                csv_writer.writerow([album.href, album.tag, album.page, album.num, album.name, album.artist,
                                     album.cover, album.listeners, album.scrobbles, album.tracks_total, album.length,
                                     album.release_date, album_track.pos, album_track.name, album_track.duration,
                                     album_track.listeners, album_track.scrobbles, album_track.href])
                self.checkpoint = {'csv': self.csv_file_name,
                                   'last tag index': self.tags.index(album.tag),
                                   'last page': album.page,
                                   'last album num': album.num,
                                   'last album href': album.href,
                                   'last track pos': album_track.pos,
                                   'last track href': album_track.href,
                                   'tracks total': album.tracks_total}
                with open(self.checkpoint_file_name, 'wb') as cp_file:
                    dump(self.checkpoint, cp_file)

    def process_data(self, album_tag, album_page, start_album_num, start_track_pos):
        albums_data = self.get_albums_data(album_tag, album_page)
        pbar = tqdm(enumerate(albums_data[start_album_num - 1:self.album_pos_end], start_album_num),
                    desc=f'Tag: {album_tag} | Page {album_page}',
                    total=self.album_pos_end - start_album_num + 1)
        for album_num, album_data in pbar:
            self.save_data(self.get_album(album_data, album_tag, album_page, album_num), start_track_pos)
            start_track_pos = 1

    def run(self):
        print('Searching checkpoint file...', end=' ')
        if exists(self.checkpoint_file_name):
            with open(self.checkpoint_file_name, 'rb') as cp_file:
                self.checkpoint = load(cp_file)

        if self.checkpoint:
            print('checkpoint file found!')
            print(self.checkpoint)
        else:
            print('checkpoint file not found! Starting scraping from scratch!')
            print('Writing csv head...', end=' ')
            self.write_csv_head()
            print('ok!')

        start_tag_index = self.checkpoint['last tag index'] if self.checkpoint else 0
        start_page = self.checkpoint['last page'] if self.checkpoint else 1
        start_album_num = self.checkpoint['last album num'] if self.checkpoint else 1
        start_track_pos = self.checkpoint['last track pos'] + 1 if self.checkpoint else 1
        print(f'Start tag index: {start_tag_index}')
        print(f'Start page: {start_page}')
        print(f'Start album number on the page: {start_album_num}')
        print(f'Start track position in album: {start_track_pos}')

        for album_tag_index in self.tags_indices[start_tag_index:]:
            for album_page in range(start_page, self.total_pages + 1):
                self.process_data(self.tags[album_tag_index], album_page, start_album_num, start_track_pos)
                start_album_num = self.album_pos_start
                start_track_pos = 1
            start_page = 1
