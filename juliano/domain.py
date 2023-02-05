import datetime


class Event:
    def __init__(self, grade, created=None):
        self.grade = grade
        self.created = created or datetime.datetime.utcnow()


class Item:
    # INCREMENT = dict(
    #     [
    #         (0, -0.8),
    #         (1, -0.54),
    #         (2, -0.32),
    #         (3, -0.14),
    #         (4, 0),
    #         (5, 0.1),
    #     ]
    # )

    INTERVALS = (0, 1, 3, 7)

    def __init__(
        self, word=None, id=None, user=None, next_iteration=None, created=None
    ):
        self.id = id
        self.user = user
        self.word = word or ""
        self.is_active = True
        self.created = created or datetime.datetime.utcnow()
        self.events = []
        self.easiness_factor = 2.5
        self.inter_repitition_interval = datetime.timedelta(days=1)
        self.next_iteration = next_iteration or self.created

    def to_dict(self):
        return dict(id=self.id, word=self.word, is_active=self.is_active)

    @property
    def last_learned(self):
        return max((event.created for event in self.events), default=None)

    @property
    def repitition_number(self):
        return len(self.events)

    def add_event(self, grade, created=None):
        event = Event(grade, created)
        self.events.append(event)
        return event

    def train(self, grade, date=None):
        event = self.add_event(grade, date)

        try:
            interval = self.INTERVALS[self.repitition_number]
        except IndexError:
            interval = max(self.INTERVALS)
        self.next_iteration = event.created + datetime.timedelta(days=interval)

        # """Spaced repitition algorithm

        # https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
        # """
        # event = self.add_event(grade, date)

        # if self.repitition_number > 2:
        #     self.inter_repitition_interval = (
        #         self.inter_repitition_interval * self.easiness_factor
        #     )

        # self.easiness_factor += self.INCREMENT[grade]

        # if self.easiness_factor < 1.3:
        #     self.easiness_factor = 1.3

        # self.next_iteration = event.created + self.inter_repitition_interval

    @property
    def todo(self):
        today = datetime.datetime.utcnow().date()
        return self.is_active and (
            self.next_iteration is None or (self.next_iteration.date() <= today)
        )


def filter_todo_items(items, n=None, max_trainings=None):
    todos = [
        item
        for item in items
        if item.todo
        and (max_trainings is None or item.repitition_number <= max_trainings)
    ]
    if n:
        today = datetime.datetime.utcnow().date()
        trained_today = len(
            [
                item
                for item in items
                if item.last_learned and item.last_learned.date() == today
            ]
        )
        limit = max(0, n - trained_today)
        return todos[0:limit]
    return todos
