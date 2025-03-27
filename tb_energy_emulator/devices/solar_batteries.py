import math
import random

from tb_energy_emulator.device import BaseDevice
from tb_energy_emulator.constants import (
    LUX_BY_TIME,
    TEMPERATURE_BY_TIME,
    SOLAR_BATTERIES_V_CELL,
    SOLAR_BATTERIES_C_V,
    SOLAR_BATTERIES_NUM_CELLS,
    SOLAR_BATTERIES_I_SC_REF
)


class SolarBatteries(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__num_cells = SOLAR_BATTERIES_NUM_CELLS
        self.__V_cell = SOLAR_BATTERIES_V_CELL
        self.__C_v = SOLAR_BATTERIES_C_V
        self.__I_sc = SOLAR_BATTERIES_I_SC_REF

        self.__last_updated_illuminance_time = 0

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\tilluminance: {self.illuminance} lx, temperature: {self.temperature} °C' \
            f'\n\toutput power: {self.output_power} W, voltage: {self.voltage} V, current: {self.current} A'

    async def off(self):
        await super().off()

        self.__last_updated_illuminance_time = 0

        self.illuminance.value = 0
        self.temperature.value = 0
        self.output_power.value = 0
        self.voltage.value = 0
        self.current.value = 0

        await self._storage.set_value(value=self.illuminance.value, **self.illuminance.config)
        await self._storage.set_value(value=self.temperature.value, **self.temperature.config)
        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)
        await self._storage.set_value(value=self.current.value, **self.current.config)

    async def update(self):
        await super().update()

        if self.running.value:
            await self.__update_lux_by_time()
            await self.__update_temperature_by_time()
            await self.__update_electrical_performance()

    async def __update_lux_by_time(self):
        hour = self._clock.hours

        if self.__last_updated_illuminance_time != hour:
            for (r, lux) in LUX_BY_TIME.items():
                if hour in r:
                    self.illuminance.value = lux
                    self.__last_updated_illuminance_time = hour
                    break
        else:
            min_value = self.illuminance.value - 100
            max_value = self.illuminance.value + 100
            new_number = self.illuminance.value + random.randint(-5, 5)
            self.illuminance.value = max(min_value, min(max_value, new_number))

        await self._storage.set_value(value=int(self.illuminance.value / 10), **self.illuminance.config)

    async def __update_temperature_by_time(self):
        hour = self._clock.hours

        for (r, temperature) in TEMPERATURE_BY_TIME.items():
            if hour in r:
                self.temperature.value = temperature
                break

        await self._storage.set_value(value=self.temperature.value, **self.temperature.config)

    async def __update_electrical_performance(self):
        power_output, voltage, current = self.__calculate_power_output(self.illuminance.value, self.temperature.value)

        self.output_power.value = power_output
        self.voltage.value = voltage
        self.current.value = current

        await self._storage.set_value(value=self.output_power.value, **self.output_power.config)
        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)
        await self._storage.set_value(value=self.current.value, **self.current.config)

    def __calculate_power_output(self, lux, temperature):
        V_base = self.__num_cells * (self.__V_cell + self.__C_v * (temperature - 25))
        voltage = V_base * (1 - math.exp(-lux / 20000))
        current = self.__I_sc * (lux / 100000)
        power_output = voltage * current

        return int(power_output), int(voltage), int(current)
