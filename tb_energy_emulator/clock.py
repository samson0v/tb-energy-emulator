from abc import abstractmethod


class Clock:
    def __init__(self, update_frequency=1.0):
        self._update_frequency = update_frequency

    @property
    @abstractmethod
    def hours(self):
        return self.__time // 60

    @property
    @abstractmethod
    def minutes(self):
        return self.__time % 60

    @abstractmethod
    def get_time_in_human_readable_format(self):
        pass

    @abstractmethod
    async def tick(self):
        pass
