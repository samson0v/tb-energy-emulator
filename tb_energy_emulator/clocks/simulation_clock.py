from asyncio import sleep

from tb_energy_emulator.clock import Clock


class SimulationClock(Clock):
    def __init__(self, update_frequency=1.0):
        super().__init__(update_frequency=update_frequency)

        self.one_day_duration = 1440
        self.__time = 0

    def __str__(self):
        return f'\n-----------' \
            f'\n|⏰: {self.get_time_in_human_readable_format()}|' \
            f'\n-----------'

    @property
    def hours(self):
        return self.__time // 60

    @property
    def minutes(self):
        return self.__time % 60

    def get_time_in_human_readable_format(self):
        return f'{self.hours:02}:{self.minutes:02}'

    async def tick(self):
        if self.__time >= self.one_day_duration:
            self.__time = 0
        else:
            self.__time += 1

        await sleep(self._update_frequency)
