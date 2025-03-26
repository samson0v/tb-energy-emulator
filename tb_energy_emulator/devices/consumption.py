import random

from tb_energy_emulator.device import BaseDevice
from tb_energy_emulator.constants import (
    CONSUPTION_BY_TIME,
    MINIMUM_CONSUMPTION,
)


class Consumption(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__needed_power = MINIMUM_CONSUMPTION
        self.__last_updated_consumption_time = 0

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\ttotal consumtion: {self.consumption} W' \
            f'\n\tfrequency (Hz): ({self.frequency_l1}, {self.frequency_l2}, {self.frequency_l3}), ' \
            f'\n\tvoltage (V): ({self.voltage_l1}, {self.voltage_l2}, {self.voltage_l3})' \
            f'\n\tconsumption (W): ({self.consumption_l1}, {self.consumption_l2}, {self.consumption_l3})'

    async def off(self):
        await super().off()

        self.voltage_l1.value = 0
        self.voltage_l2.value = 0
        self.voltage_l3.value = 0

        self.frequency_l1.value = 0
        self.frequency_l2.value = 0
        self.frequency_l3.value = 0

        self.consumption_l1.value = 0
        self.consumption_l2.value = 0
        self.consumption_l3.value = 0
        self.consumption.value = 0

        await self._storage.set_value(value=self.voltage_l1.value, **self.voltage_l1.config)
        await self._storage.set_value(value=self.voltage_l2.value, **self.voltage_l2.config)
        await self._storage.set_value(value=self.voltage_l3.value, **self.voltage_l3.config)

        await self._storage.set_value(value=self.frequency_l1.value, **self.frequency_l1.config)
        await self._storage.set_value(value=self.frequency_l2.value, **self.frequency_l2.config)
        await self._storage.set_value(value=self.frequency_l3.value, **self.frequency_l3.config)

        await self._storage.set_value(value=self.consumption_l1.value, **self.consumption_l1.config)
        await self._storage.set_value(value=self.consumption_l2.value, **self.consumption_l2.config)
        await self._storage.set_value(value=self.consumption_l3.value, **self.consumption_l3.config)
        await self._storage.set_value(value=self.consumption.value, **self.consumption.config)

    @property
    def needed_consumption(self):
        return self.__needed_power

    async def update(self, input_power):
        await super().update()

        if self.running.value:
            await self.__update_consumption_by_time()
            await self.__update_frequency()
            await self.__update_voltage()
            await self.__update_consumption(input_power)

    async def __update_frequency(self):
        self.frequency_l1.generate_value()
        self.frequency_l2.generate_value()
        self.frequency_l3.generate_value()

        await self._storage.set_value(value=self.frequency_l1.value, **self.frequency_l1.config)
        await self._storage.set_value(value=self.frequency_l2.value, **self.frequency_l2.config)
        await self._storage.set_value(value=self.frequency_l3.value, **self.frequency_l3.config)

    async def __update_voltage(self):
        self.voltage_l1.generate_value()
        self.voltage_l2.generate_value()
        self.voltage_l3.generate_value()

        await self._storage.set_value(value=self.voltage_l1.value, **self.voltage_l1.config)
        await self._storage.set_value(value=self.voltage_l2.value, **self.voltage_l2.config)
        await self._storage.set_value(value=self.voltage_l3.value, **self.voltage_l3.config)

    async def __update_consumption(self, input_power):
        phase_1, phase_2, phase_3 = self.distribute_consuption(input_power)

        self.consumption_l1.value = phase_1
        self.consumption_l2.value = phase_2
        self.consumption_l3.value = phase_3

        self.consumption.value = input_power

        await self._storage.set_value(value=int(self.consumption_l1.value), **self.consumption_l1.config)
        await self._storage.set_value(value=int(self.consumption_l2.value), **self.consumption_l2.config)
        await self._storage.set_value(value=int(self.consumption_l3.value), **self.consumption_l3.config)
        await self._storage.set_value(value=int(self.consumption.value), **self.consumption.config)

    def distribute_consuption(self, max_consumption, num_phases=3, deviation=0.1):
        base_value = max_consumption // num_phases
        min_value = int(base_value * (1 - deviation))
        max_value = int(base_value * (1 + deviation))

        phases = [random.randint(min_value, max_value) for _ in range(num_phases - 1)]

        last_phase = max_consumption - sum(phases)
        phases.append(last_phase)

        if last_phase < min_value:
            diff = min_value - last_phase
            phases[-1] = min_value
            phases[phases.index(max(phases[:-1]))] -= diff

        elif last_phase > max_value:
            diff = last_phase - max_value
            phases[-1] = max_value
            phases[phases.index(min(phases[:-1]))] += diff

        return phases

    async def __update_consumption_by_time(self):
        hour = self._clock.hours

        if self.__last_updated_consumption_time != hour:
            for (r, consumption) in CONSUPTION_BY_TIME.items():
                if hour in r:
                    self.__needed_power = consumption
                    self.__last_updated_consumption_time = hour
                    break
        else:
            min_value = self.__needed_power - 50
            max_value = self.__needed_power + 50
            new_number = self.__needed_power + random.randint(-2, 2)
            self.__needed_power = max(min_value, min(max_value, new_number))
