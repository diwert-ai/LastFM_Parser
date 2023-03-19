from scraper import LastFMScraper
import pandas as pd


def main():
    scraper = LastFMScraper(csv_file_name='lastfm_current.csv', verbose=False, tag_indices=(0, ),
                            album_pos_start=1, album_pos_end=20,
                            total_pages=25)
    scraper.run()
    df = pd.DataFrame(scraper.data_container)
    df.to_csv('lastfm_pandas.csv', index=False)


if __name__ == '__main__':
    main()
