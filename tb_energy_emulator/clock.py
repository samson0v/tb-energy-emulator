from abc import abstractmethod


class Clock:
    def __init__(self, update_frequency=1.0):
        self._update_frequency = update_frequency

    @property
    def update_frequency(self):
        return self._update_frequency

    @property
    @abstractmethod
    def ticks_num_in_hour(self):
        pass

    @property
    @abstractmethod
    def hours(self):
        pass

    @property
    @abstractmethod
    def minutes(self):
        pass

    @abstractmethod
    def get_time_in_human_readable_format(self):
        pass

    @abstractmethod
    async def tick(self):
        pass
