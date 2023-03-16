import requests
from bs4 import BeautifulSoup


def main():
    tags = ['rock', 'hip-hop', 'indie', 'jazz', 'reggae', 'british', 'punk', '80s', 'dance', 'electronic', 'metal',
            'acoustic', 'rnb', 'hardcore', 'country', 'blues', 'alternative', 'classical', 'rap', 'country']
    tag, page = tags[17], 1
    fm_url = f'https://www.last.fm/tag/{tag}/albums?page={page}'
    fm_page = requests.get(fm_url)
    fm_soup = BeautifulSoup(fm_page.text, 'lxml')
    artist_albums_section = fm_soup.find_all('section', {'id': 'artist-albums-section'})
    albums = artist_albums_section[0].find_all('li', class_='resource-list--release-list-item-wrap')
    print(f'tag: {tag}, page: {page}')
    for album in albums[6:7]:
        album_name = album.find_all('h3')[0].get_text().strip()
        album_href = 'https://www.last.fm' + album.find_all('a', class_='link-block-target')[0].get('href')
        album_artist = album.find_all('p', class_='resource-list--release-list-item-artist')[0].get_text().strip()
        album_cover = album.find_all('img')[0].get('src')
        album_aux_text = album.find_all('p', class_='resource-list--release-list-item-aux-text')
        album_listeners = album_aux_text[0].get_text().strip()
        album_release_date, album_tracks_num = map(str.strip, album_aux_text[1].get_text().strip().split('\n'))\
            if len(album_aux_text) > 1\
            else (None, None)
        album_page = requests.get(album_href)
        album_soup = BeautifulSoup(album_page.text, 'lxml')
        album_meta = album_soup.find_all('ul', class_='header-metadata-tnew')
        album_counters = album_meta[0].find_all('abbr')
        album_scrobbles = album_counters[1].get('title')
        print(f'name: {album_name}\nartist: {album_artist}\ncover: {album_cover}\nlisteners: {album_listeners}')
        print(f'release_date: {album_release_date}\ntracks_num: {album_tracks_num}\nscrobbles:{album_scrobbles}')
        album_tracklist = album_soup.find_all('section', {'id': 'tracklist'})
        album_tracks = album_tracklist[0].find_all('tr', class_='chartlist-row')
        for track_pos, track in enumerate(album_tracks, 1):
            track_duration = track.find_all('td', class_='chartlist-duration')[0].get_text().strip()
            track_listeners = track.find_all('td', class_='chartlist-bar')[0].get_text().strip()
            track_name = track.find_all('td', class_='chartlist-name')[0].get_text().strip()
            print(track_pos, track_name, track_duration, track_listeners)
        print('--------------------------------------------------------------------------')


if __name__ == '__main__':
    main()
