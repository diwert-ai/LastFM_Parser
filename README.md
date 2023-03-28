# last.fm parser/scraper
## Homework #4 (HSE DPO DS Python course)

- The parser traverses the albums (and tracks) pages on https://last.fm and saves parsed data to csv file.
- The tags are retrieved from a following list: `tags = ['rock', 'hip-hop', 'indie', 'jazz', 'reggae', 'british', 'punk', 
'80s', 'dance', 'electronic', 'metal', 'acoustic', 'rnb', 'hardcore', 'country', 'blues', 'alternative', 'classical',
'rap', 'composer', 'modern classical', 'neoclassical', 'post-punk', 'russian']`.

- For each tag, last.fm gives access to the first 25 pages. Each page features 20 albums. If an album has a track page,
album and track information is saved to a csv file.

- The following information is saved in the csv file: `['album href', 'album tag', 'album page', 'album num', 
'album name', 'album artist',
'album cover href', 'album listeners', 'album scrobbles', 'album tracks_total',
'album length', 'album release date', 'track pos', 'track name', 'track duration',
'track listeners', 'track scrobbles', 'track href']`

- The scraper is started with the command `python main.py`

- The assembled dataset is archived in the file `lastfm.zip` (compressed with the `ZIP_LZMA` parameter - see details in
`csvzip.py`)

- To load a csv dataset into a pandas DataFrame run `df = pd.read_csv('lastfm2.csv', quotechar='|', quoting=csv.QUOTE_ALL,
delimiter=' ')` (see details in `lastfm_dataset_view.ipynb`)
