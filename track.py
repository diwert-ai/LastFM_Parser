class Track:
    def __init__(self, track_pos, track_name, track_duration, track_listeners, track_scrobbles, track_href):
        self.pos = track_pos
        self.name = track_name
        self.duration = track_duration
        self.listeners = track_listeners
        self.scrobbles = track_scrobbles
        self.href = track_href

    def __str__(self):
        return f'#{self.pos} {self.name} {self.duration} {self.listeners:_} {self.scrobbles:_} {self.href}'

    def to_tuple(self):
        return self.pos, self.name, self.duration, self.listeners, self.scrobbles, self.href
