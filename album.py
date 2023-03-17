class Album:
    def __init__(self, album_name, album_href, album_artist, album_cover,
                 album_scrobbles, album_listeners, album_tracks_total, album_length, album_release_date):
        self.name = album_name
        self.href = album_href
        self.artist = album_artist
        self.cover = album_cover
        self.scrobbles = album_scrobbles
        self.listeners = album_listeners
        self.tracks_total = album_tracks_total
        self.length = album_length
        self.release_date = album_release_date
        self.tracks_list = None
        self.tag = None
        self.page = None
        self.num = None

    def __str__(self):
        t_list = '\n'.join(map(str, self.tracks_list))
        return f'tag: {self.tag}\npage: {self.page}\nnum: {self.num}\n' + \
            f'name: {self.name}\nhref: {self.href}\nartist: {self.artist}\n' + \
            f'cover: {self.cover}\nscrobbles: {self.scrobbles:_}\nlisteners: {self.listeners:_}\n' + \
            f'tracks_total: {self.tracks_total}\nlength: {self.length}\nrelease_date: {self.release_date}\n' + \
            f'track_list:\n{t_list}'
