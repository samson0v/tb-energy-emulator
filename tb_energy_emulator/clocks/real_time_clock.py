from asyncio import sleep
import datetime

from tb_energy_emulator.clock import Clock


class RealtimeClock(Clock):
    def __init__(self, update_frequency=1):
        super().__init__(update_frequency)

        self.__time = datetime.datetime.now().time()

    def __str__(self):
        return f'\n-----------' \
            f'\n|⏰: {self.get_time_in_human_readable_format()}|' \
            f'\n-----------'

    @property
    def hours(self):
        return self.__time.hour

    @property
    def minutes(self):
        return self.__time.minute

    def get_time_in_human_readable_format(self):
        return self.__time.strftime('%H:%M')

    async def tick(self):
        self.__time = datetime.datetime.now().time()
        await sleep(self._update_frequency)
