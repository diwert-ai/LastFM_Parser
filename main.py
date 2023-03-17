from scraper import LastFMScraper


def main():
    scraper = LastFMScraper(csv_file_name='test.csv', verbose=True, tag_indices=(-1, -2, -3))
    scraper.run()


if __name__ == '__main__':
    main()
