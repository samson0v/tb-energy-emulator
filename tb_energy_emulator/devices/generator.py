from tb_energy_emulator.device import BaseDevice


class Generator(BaseDevice):
    FUEL_RATE_BY_CONSUMPTION = {
        10000: 3,
        15_000: 8,
        20_000: 13
    }
    MINIMUM_FUEL_RATE = 3

    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__efficiency = 0.85
        self.__fuel_energy_density = 34.2
        self.__fuel_rate = self.MINIMUM_FUEL_RATE

    def __str__(self):
        return f'\n{self.name}: ' \
            f'\n\ttemperature: {self.oil_temperature} °C, voltage: {self.voltage} V, frequency: {self.frequency} Hz' \
            f'\n\toutput power: {self.output_power} W, ' \
            f'fuel level: {self.fuel_level} %, fuel rate: {self.__fuel_rate} l/h'

    async def off(self):
        super().off()

        self.voltage.value = 0
        self.output_power.value = 0

        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)
        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)

    async def update(self, consuption):
        if self.running:
            await self.__update_oil_temperature()
            await self.__update_voltage()
            await self.__update_output_power(consuption)
            await self.__update_fuel_level()
            await self.__update_frequency()
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
        self.__fuel_rate = self.FUEL_RATE_BY_CONSUMPTION.get(consuption, self.MINIMUM_FUEL_RATE)
        self.output_power.value = self.__efficiency * self.__fuel_energy_density * self.__fuel_rate
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

    async def __decrease_oil_temperature(self):
        if self.oil_temperature.value > 0:
            self.oil_temperature.value -= 1

            await self._storage.set_value(value=self.oil_temperature.value, **self.oil_temperature.config)
