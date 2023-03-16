import requests
from bs4 import BeautifulSoup


def main():
    fm_url = 'https://www.last.fm/tag/classical/albums?page=1'
    fm_page = requests.get(fm_url)
    fm_soup = BeautifulSoup(fm_page.text, 'html')
    artist_albums_section = fm_soup.find_all('section', {'id': 'artist-albums-section'})
    albums = artist_albums_section[0].find_all('li', class_='resource-list--release-list-item-wrap')

    for album in albums:
        print(album.find_all('h3')[0].get_text().strip())
        print('https://www.last.fm' + album.find_all('a', class_='link-block-target')[0].get('href'))
        print(album.find_all('p', class_='resource-list--release-list-item-artist')[0].get_text().strip())
        print(album.find_all('img')[0].get('src'))
        aux_text = album.find_all('p', class_='resource-list--release-list-item-aux-text')
        for text in aux_text:
            print(text.get_text().strip())

        print('-------------------------------')


if __name__ == '__main__':
    main()

