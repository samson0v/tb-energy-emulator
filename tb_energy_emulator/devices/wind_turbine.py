from random import randint

from tb_energy_emulator.device import BaseDevice
from tb_energy_emulator.constants import (
    ROTOR_RADIUS,
    WIND_SPEED_BY_TIME,
    TIP_SPEED_RATIO
)


class WindTurbine(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__rotor_radius = ROTOR_RADIUS
        self.__tip_speed_ratio = TIP_SPEED_RATIO
        self.__swept_area = 3.14 * self.__rotor_radius ** 2

    def __str__(self):
        return f'\n{self.name} (running: {self.running.value}): ' \
            f'\n\twind speed: {self.wind_speed} m/s, rotor speed: {self.rotor_speed} rpm' \
            f'\n\toutput power: {self.output_power} W, wind direction: {self.wind_direction}°'

    async def update(self):
        await super().update()

        if self.running.value:
            await self.__update_wind_direction()
            await self.__update_wind_speed()
            await self.__update_turbine_performance()

    async def off(self):
        await super().off()

        self.output_power.value = 0
        self.rotor_speed.value = 0

        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.rotor_speed.value, **self.rotor_speed.config)

    async def __update_wind_direction(self):
        self.wind_direction.value = (self.wind_direction.value / 100) + 0.24
        if self.wind_direction.value / 100 >= 360:
            self.wind_direction.value = 0

        await self._storage.set_value(value=self.wind_direction.value, **self.wind_direction.config)

    async def __update_wind_speed(self):
        hour = self._clock.hours

        for (r, wind_speed) in WIND_SPEED_BY_TIME.items():
            if hour in r:
                self.wind_speed.value = randint(wind_speed[0], wind_speed[-1])
                break

        await self._storage.set_value(value=self.wind_speed.value, **self.wind_speed.config)

    async def __update_turbine_performance(self):
        output_power, rotor_speed = self.__calculate_power_output()

        self.output_power.value = output_power
        self.rotor_speed.value = rotor_speed

        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.rotor_speed.value, **self.rotor_speed.config)

    def __calculate_power_output(self):
        if self.wind_speed.value < 2:
            return 0, 0

        output_power = self.__swept_area * self.wind_speed.value ** 3
        rotor_speed = (self.__tip_speed_ratio * self.wind_speed.value) / self.__rotor_radius

        return int(output_power), int(rotor_speed)
