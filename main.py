from scraper import LastFMScraper
from time import sleep


def main():
    result = None
    while result != 'End!':
        scraper = LastFMScraper(csv_file_name='lastfm2.csv')
        try:
            result = scraper.run()
        except Exception as e:
            print(e)
            sleep(10)


if __name__ == '__main__':
    main()
