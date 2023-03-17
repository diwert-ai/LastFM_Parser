class Track:
    def __init__(self, track_pos, track_name, track_duration, track_listeners):
        self.pos = track_pos
        self.name = track_name
        self.duration = track_duration
        self.listeners = track_listeners

    def __str__(self):
        return f'#{self.pos} {self.name} {self.duration} {self.listeners:_}'

    def to_tuple(self):
        return self.pos, self.name, self.duration, self.listeners
