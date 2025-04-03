import random
from tb_energy_emulator.device import BaseDevice

from tb_energy_emulator.constants import (
    FUEL_VOLUME,
    MINIMUM_FUEL_RATE,
    FUEL_RATE_BY_CONSUMPTION
)


class Generator(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__fuel_rate = MINIMUM_FUEL_RATE
        self.__fuel_volume = FUEL_VOLUME

        self.__start_time = 0
        self.__end_time = 0

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\ttemperature: {self.oil_temperature} °C, voltage: {self.voltage} V, frequency: {self.frequency} Hz' \
            f'\n\toutput power: {self.output_power} W, ' \
            f'fuel level: {self.fuel_level} %, fuel rate: {self.__fuel_rate} l/h'

    async def on(self, with_init_values=True):
        await super().on(with_init_values)

        self.__start_time = self._clock.time

    async def off(self):
        await super().off()
        await self.__update_operating_hours()

        self.voltage.value = 0
        self.output_power.value = 0
        self.frequency.value = 0

        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)
        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)

    async def __update_operating_hours(self):
        self.__end_time = self._clock.time

        timestamp = round((self.__end_time - self.__start_time) / self._clock.ticks_num_in_hour, 1)

        self.total_working_duration.value = self.total_working_duration.get_value_without_multiplier() + timestamp
        self.current_session_duration.value = timestamp

        await self._storage.set_value(value=self.total_working_duration.value, **self.total_working_duration.config)
        await self._storage.set_value(value=self.current_session_duration.value, **self.current_session_duration.config)

    async def update(self, consuption):
        await self.update_running_status()

        if self.running.value:
            await self.__update_oil_temperature(consuption)
            await self.__update_voltage()
            await self.__update_output_power(consuption)
            await self.__update_frequency()
            await self.__update_fuel_level()
        else:
            await self.__decrease_oil_temperature()

    async def update_running_status(self):
        running = bool(await self._storage.get_value(**self.running.config))

        if running != self.running.value:
            self.running.value = running

            if running:
                await self.on(with_init_values=False)
                self.fuel_level.value = 100
                await self._storage.set_value(value=self.fuel_level.value, **self.fuel_level.config)
                self.__fuel_volume = FUEL_VOLUME
            else:
                await self.off()

    async def __update_oil_temperature(self, consumption):
        '''
        Three cases are available:
        - generator warming up
        - generator under load
        - generator without load
        '''

        if self.oil_temperature.value <= 85:
            self.oil_temperature.value += 1
        else:
            if consumption == 0:
                self.oil_temperature.value = self.generate_temperature(self.oil_temperature.value, 86, 95)
            else:
                if self.oil_temperature.value <= 96:
                    self.oil_temperature.value += 1
                else:
                    self.oil_temperature.value = self.generate_temperature(self.oil_temperature.value, 97, 105)

        await self._storage.set_value(value=self.oil_temperature.value, **self.oil_temperature.config)

    def generate_temperature(self, current_temperature, min_value, max_value):
        new_number = current_temperature + random.randint(-1, 1)
        return max(min_value, min(max_value, new_number))

    async def __update_voltage(self):
        self.voltage.generate_value()

        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)

    async def __update_output_power(self, consumption):
        self.__fuel_rate = self.__get_fuel_rate(consumption)
        self.output_power.value = consumption
        await self._storage.set_value(value=int(self.output_power.value), **self.output_power.config)

    def __get_fuel_rate(self, consumption):
        fule_rate = None

        for cons, rate in FUEL_RATE_BY_CONSUMPTION.items():
            if consumption in cons:
                fule_rate = rate

        if fule_rate is None:
            fule_rate = MINIMUM_FUEL_RATE

        return fule_rate

    async def __update_fuel_level(self):
        self.__fuel_volume -= self.__fuel_rate / self._clock.ticks_num_in_hour

        if self.__fuel_volume <= 0:
            self.__fuel_volume = 0
            await self.off()

        self.fuel_level.value = (self.__fuel_volume / FUEL_VOLUME) * 100

        await self._storage.set_value(value=int(self.fuel_level.value), **self.fuel_level.config)

    async def __update_frequency(self):
        self.frequency.generate_value()

        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)

    async def __decrease_oil_temperature(self):
        if self.oil_temperature.value > 0 and self.oil_temperature.value > self.oil_temperature.min_value:
            self.oil_temperature.value -= 1

            await self._storage.set_value(value=self.oil_temperature.value, **self.oil_temperature.config)
