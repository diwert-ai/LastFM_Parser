from requests import get
from bs4 import BeautifulSoup
from csv import writer, QUOTE_ALL
from track import Track
from album import Album


class LastFMScraper:
    tags = ['rock', 'hip-hop', 'indie', 'jazz', 'reggae', 'british', 'punk', '80s', 'dance', 'electronic', 'metal',
            'acoustic', 'rnb', 'hardcore', 'country', 'blues', 'alternative', 'classical', 'rap', 'country', 'composer',
            'modern classical', 'neoclassical', 'post-punk', 'russian']

    def __init__(self, csv_file_name, tag_indices=(0,), total_pages=1, album_pos_start=1,
                 album_pos_end=2, verbose=False):
        self.csv_file_name = csv_file_name
        self.tags_indices = tag_indices
        self.total_pages = total_pages
        self.album_pos_start = album_pos_start
        self.album_pos_end = album_pos_end
        self.verbose = verbose

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
    def get_album_tracks_list(album_soup):
        album_tracks_list = []
        album_tracks_list_data = album_soup.find_all('section', {'id': 'tracklist'})
        if album_tracks_list_data:
            album_tracks = album_tracks_list_data[0].find_all('tr', class_='chartlist-row')
            for track_pos, track in enumerate(album_tracks, 1):
                track_duration = track.find_all('td', class_='chartlist-duration')[0].get_text().strip()
                track_listeners = \
                    int(track.find_all('td', class_='chartlist-bar')[0].get_text().strip().split()[0].replace(',', ''))
                track_name = track.find_all('td', class_='chartlist-name')[0].get_text().strip()
                album_tracks_list.append(Track(track_pos, track_name, track_duration, track_listeners))

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
        album.tracks_list = self.get_album_tracks_list(album_soup)
        album.tag = album_tag
        album.page = album_page
        album.num = album_num
        return album

    def save_to_csv(self, album):
        if self.verbose:
            print(album)
        album_tracks = [track.to_tuple() for track in album.tracks_list]
        with open(self.csv_file_name, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = writer(csv_file, delimiter=' ', quotechar='|', quoting=QUOTE_ALL)
            csv_writer.writerow([album.tag, album.page, album.num, album.name, album.artist, album.cover,
                                 album.listeners, album.scrobbles, album.tracks_total, album.length,
                                 album.release_date, album_tracks])

    def process_data(self, album_tag, album_page):
        albums_data = self.get_albums_data(album_tag, album_page)
        for album_num, album_data in enumerate(albums_data[self.album_pos_start - 1:self.album_pos_end], 1):
            self.save_to_csv(self.get_album(album_data, album_tag, album_page, album_num))

    def run(self):
        for album_tag_index in self.tags_indices:
            for album_page in range(1, self.total_pages + 1):
                self.process_data(self.tags[album_tag_index], album_page)
