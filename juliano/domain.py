import datetime


class Event:
    def __init__(self, grade, created=None):
        self.grade = grade
        self.created = created or datetime.datetime.utcnow()


class Item:
    INCREMENT = dict(
        [
            (0, -0.8),
            (1, -0.54),
            (2, -0.32),
            (3, -0.14),
            (4, 0),
            (5, 0.1),
        ]
    )

    def __init__(self, word, id=None):
        self.id = id
        self.word = word
        self.is_active = True
        self.created = datetime.datetime.utcnow()
        self.events = []
        self.repitition_number = 0
        self.easiness_factor = 2.5

    def to_dict(self):
        return dict(id=self.id, word=self.word, is_active=self.is_active)

    @property
    def last_learned(self):
        return max((event.created for event in self.events), default=None)

    def add_event(self, grade, created=None):
        event = Event(grade, created)
        self.events.append(event)
        return event

    def train(self, grade):
        """Spaced repitition algorithm

        https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
        """
        event = self.add_event(grade)

        if self.repitition_number < 3:
            self.inter_repitition_interval = datetime.timedelta(days=1)
        else:
            self.inter_repitition_interval = (
                self.inter_repitition_interval * self.easiness_factor
            )

        self.easiness_factor += self.INCREMENT[grade]

        if self.easiness_factor < 1.3:
            self.easiness_factor = 1.3

        self.next_iteration = event.created + self.inter_repitition_interval

    @property
    def todo(self):
        return self.is_active and (
            self.next_iteration is None
            or (self.next_iteration.date() <= datetime.date.today())
        )
