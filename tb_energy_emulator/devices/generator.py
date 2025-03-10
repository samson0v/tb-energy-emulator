from tb_energy_emulator.device import BaseDevice

from tb_energy_emulator.constants import (
    MINIMUM_FUEL_RATE,
    FUEL_RATE_BY_CONSUMPTION,
    GENERATOR_EFFICIENCY,
    FUEL_ENERGY_DENSITY
)


class Generator(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__efficiency = GENERATOR_EFFICIENCY
        self.__fuel_energy_density = FUEL_ENERGY_DENSITY
        self.__fuel_rate = MINIMUM_FUEL_RATE

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\ttemperature: {self.oil_temperature} °C, voltage: {self.voltage} V, frequency: {self.frequency} Hz' \
            f'\n\toutput power: {self.output_power} W, ' \
            f'fuel level: {self.fuel_level} %, fuel rate: {self.__fuel_rate} l/h'

    async def off(self):
        await super().off()

        self.voltage.value = 0
        self.output_power.value = 0
        self.frequency.value = 0

        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)
        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)

    async def update(self, consuption):
        if self.running.value:
            await self.__update_oil_temperature()
            await self.__update_voltage()
            await self.__update_output_power(consuption)
            await self.__update_frequency()
            await self.__update_fuel_level()
        else:
            await self.__decrease_oil_temperature()

    async def __update_oil_temperature(self):
        if self.oil_temperature.value <= self.oil_temperature.max_value:
            self.oil_temperature.value = self.oil_temperature.value + 1

        await self._storage.set_value(value=self.oil_temperature.value, **self.oil_temperature.config)

    async def __update_voltage(self):
        self.voltage.generate_value()

        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)

    async def __update_output_power(self, consuption):
        self.__fuel_rate = FUEL_RATE_BY_CONSUMPTION.get(consuption, MINIMUM_FUEL_RATE)
        self.output_power.value = int(self.__efficiency * self.__fuel_energy_density * self.__fuel_rate)
        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)

    async def __update_fuel_level(self):
        new_level = self.fuel_level.value - self.__fuel_rate
        if new_level <= 0:
            self.fuel_level.value = 0
            await self.off()
        else:
            self.fuel_level.value = new_level

        await self._storage.set_value(value=self.fuel_level.value, **self.fuel_level.config)

    async def __update_frequency(self):
        self.frequency.generate_value()

        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)

    async def __decrease_oil_temperature(self):
        if self.oil_temperature.value > 0 and self.oil_temperature.value > self.oil_temperature.min_value:
            self.oil_temperature.value -= 1

            await self._storage.set_value(value=self.oil_temperature.value, **self.oil_temperature.config)
