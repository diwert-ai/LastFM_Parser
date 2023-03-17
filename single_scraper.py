from requests import get
from bs4 import BeautifulSoup
from csv import writer, QUOTE_ALL


def lastfm_scraper():
    csv_file_name = 'lastfm.csv'
    tags = ['rock', 'hip-hop', 'indie', 'jazz', 'reggae', 'british', 'punk', '80s', 'dance', 'electronic', 'metal',
            'acoustic', 'rnb', 'hardcore', 'country', 'blues', 'alternative', 'classical', 'rap', 'country', 'composer',
            'modern classical', 'neoclassical', 'post-punk', 'russian']
    tag, page, album_start, album_end = tags[-3], 1, 0, 2
    for page in range(1, 2):
        fm_url = f'https://www.last.fm/tag/{tag}/albums?page={page}'
        fm_page = get(fm_url)
        fm_soup = BeautifulSoup(fm_page.text, 'lxml')
        artist_albums_section = fm_soup.find_all('section', {'id': 'artist-albums-section'})
        albums = artist_albums_section[0].find_all('li', class_='resource-list--release-list-item-wrap')
        print(f'tag: {tag}, page: {page}, album start: {album_start}, album end: {album_end}')
        for album_num, album in enumerate(albums[album_start:album_end], 1):
            album_name = album.find_all('h3')[0].get_text().strip()
            album_href = 'https://www.last.fm' + album.find_all('a', class_='link-block-target')[0].get('href')
            album_artist = album.find_all('p', class_='resource-list--release-list-item-artist')[0].get_text().strip()
            album_cover = album.find_all('img')[0].get('src')
            album_aux_text = album.find_all('p', class_='resource-list--release-list-item-aux-text')
            album_listeners = album_aux_text[0].get_text().strip()
            album_page = get(album_href)
            album_soup = BeautifulSoup(album_page.text, 'lxml')
            album_meta = album_soup.find_all('ul', class_='header-metadata-tnew')
            album_counters = album_meta[0].find_all('abbr')
            album_scrobbles = album_counters[1].get('title')
            print(f'name: {album_name}\nartist: {album_artist}\ncover: {album_cover}\nlisteners: {album_listeners}')
            print(f'scrobbles: {album_scrobbles}')
            album_catalogue = album_soup.find_all('dl', class_='catalogue-metadata')
            album_cat_length = album_cat_release_date = None
            if album_catalogue:
                album_catalogue_data = album_catalogue[0].find_all('dd', class_='catalogue-metadata-description')
                album_cat_length = album_catalogue_data[0].get_text().strip()
                if len(album_catalogue_data) > 1:
                    album_cat_release_date = album_catalogue_data[1].get_text().strip()
            print(f'catalogue release date: {album_cat_release_date}')
            print(f'catalogue length: {album_cat_length}')
            album_tracklist = album_soup.find_all('section', {'id': 'tracklist'})
            if album_tracklist:
                album_tracks = album_tracklist[0].find_all('tr', class_='chartlist-row')
                for track_pos, track in enumerate(album_tracks, 1):
                    track_duration = track.find_all('td', class_='chartlist-duration')[0].get_text().strip()
                    track_listeners = track.find_all('td', class_='chartlist-bar')[0].get_text().strip()
                    track_name = track.find_all('td', class_='chartlist-name')[0].get_text().strip()
                    print(track_pos, track_name, track_duration, track_listeners)
            with open(csv_file_name, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = writer(csv_file, delimiter=' ', quotechar='|', quoting=QUOTE_ALL)
                csv_writer.writerow([tag, page, album_num, album_name, album_artist, album_cover,
                                     album_listeners, album_cat_length, album_cat_release_date])
            print('---------------------------------------------------------------------------------')


if __name__ == '__main__':
    lastfm_scraper()
