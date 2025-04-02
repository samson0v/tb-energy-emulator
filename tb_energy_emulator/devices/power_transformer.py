from enum import Enum

from tb_energy_emulator.constants import CONSUMPTION_RESET_PERIOD, DAILY_RATE_HOURS, MAX_OUTPUT_POWER
from tb_energy_emulator.device import BaseDevice


class PhaseMode(Enum):
    OFF = 0
    ON = 1
    BYPASS = 2


class PowerTransformer(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__max_output_power = MAX_OUTPUT_POWER
        self.__last_updated_day_consumption_time = None
        self.__last_updated_night_consumption_time = None
        self.__last_consumption_reset_time = 0

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\tday consumption: {self.day_consumption} Wh, night consumption: {self.night_consumption} Wh' \
            f'\n\tfrequency: {self.frequency} Hz, current: {self.current} A, power output: {self.power} W' \
            f'\n\tinput voltage: ({self.input_voltage_l1}, {self.input_voltage_l2}, {self.input_voltage_l3})' \
            f'\n\toutput voltage: ({self.output_voltage_l1}, {self.output_voltage_l2}, {self.output_voltage_l3})' \
            f'\n\tphase modes: {self.l1_mode}, {self.l2_mode}, {self.l3_mode}'

    async def off(self):
        await super().off()

        self.frequency.value = 0
        self.current.value = 0
        self.power.value = 0

        self.input_voltage_l1.value = 0
        self.input_voltage_l2.value = 0
        self.input_voltage_l3.value = 0

        self.output_voltage_l1.value = 0
        self.output_voltage_l2.value = 0
        self.output_voltage_l3.value = 0

        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)
        await self._storage.set_value(value=self.current.value, **self.current.config)
        await self._storage.set_value(value=self.power.value, **self.power.config)
        await self._storage.set_value(value=self.input_voltage_l1.value, **self.input_voltage_l1.config)
        await self._storage.set_value(value=self.input_voltage_l2.value, **self.input_voltage_l2.config)
        await self._storage.set_value(value=self.input_voltage_l3.value, **self.input_voltage_l3.config)
        await self._storage.set_value(value=self.output_voltage_l1.value, **self.output_voltage_l1.config)
        await self._storage.set_value(value=self.output_voltage_l2.value, **self.output_voltage_l2.config)
        await self._storage.set_value(value=self.output_voltage_l3.value, **self.output_voltage_l3.config)

    async def update(self, input_power=0):
        await super().update()

        if self.running.value:
            await self.__update_current()
            await self.__update_frequency()
            await self.__update_input_voltage()
            await self.__update_output_voltage()
            await self.__update_power_output(input_power)
            await self.__update_consumptions()

    async def update_running_status(self):
        await super().update()

    async def __update_current(self):
        self.current.generate_value()

        await self._storage.set_value(value=int(self.current.value), **self.current.config)

    async def __update_frequency(self):
        self.frequency.generate_value()

        await self._storage.set_value(value=self.frequency.value, **self.frequency.config)

    async def __update_input_voltage(self):
        self.input_voltage_l1.generate_value()
        self.input_voltage_l2.generate_value()
        self.input_voltage_l3.generate_value()

        await self._storage.set_value(value=self.input_voltage_l1.value, **self.input_voltage_l1.config)
        await self._storage.set_value(value=self.input_voltage_l2.value, **self.input_voltage_l2.config)
        await self._storage.set_value(value=self.input_voltage_l3.value, **self.input_voltage_l3.config)

    async def __update_output_voltage(self):
        await self.__update_output_voltage_for_phase(self.input_voltage_l1, self.output_voltage_l1, self.l1_mode)
        await self.__update_output_voltage_for_phase(self.input_voltage_l2, self.output_voltage_l2, self.l2_mode)
        await self.__update_output_voltage_for_phase(self.input_voltage_l3, self.output_voltage_l3, self.l3_mode)

        await self._storage.set_value(value=self.output_voltage_l1.value, **self.output_voltage_l1.config)
        await self._storage.set_value(value=self.output_voltage_l2.value, **self.output_voltage_l2.config)
        await self._storage.set_value(value=self.output_voltage_l3.value, **self.output_voltage_l3.config)

    async def __update_output_voltage_for_phase(self, phase_input, phase_output, phase_mode):
        await self.__update_phase_mode(phase_mode)

        if phase_mode.value == PhaseMode.ON.value:
            phase_output.generate_value()
        elif phase_mode.value == PhaseMode.BYPASS.value:
            phase_output.value = phase_input.get_value_without_multiplier()
        else:
            phase_output.value = 0

    async def __update_phase_mode(self, phase_mode):
        phase_mode_updated = await self._storage.get_value(**phase_mode.config)
        if phase_mode_updated != phase_mode.value:
            phase_mode.value = phase_mode_updated

    async def __update_power_output(self, input_power):
        max_power_output = self.__get_max_power_output()
        if input_power > max_power_output:
            self.power.value = max_power_output
        else:
            self.power.value = input_power

        await self._storage.set_value(value=int(self.power.value), **self.power.config)

    def __get_max_power_output(self):
        running_phases_num = tuple(filter(lambda x: x.value == PhaseMode.ON.value or x.value == PhaseMode.BYPASS.value,
                                          [self.l1_mode, self.l2_mode, self.l3_mode]))
        return (len(running_phases_num) * self.__max_output_power) / 3

    async def __update_consumptions(self):
        hours = self._clock.hours
        minutes = self._clock.minutes

        if hours in DAILY_RATE_HOURS:
            if self.__last_updated_day_consumption_time != minutes:
                await self.__update_consumption(self.day_consumption)
                self.__last_updated_day_consumption_time = minutes
                await self.__check_and_reset_consumtption()
        else:
            if self.__last_updated_night_consumption_time != minutes:
                await self.__update_consumption(self.night_consumption)
                self.__last_updated_night_consumption_time = minutes
                await self.__check_and_reset_consumtption()

    async def __update_consumption(self, consumption):
        consumption.value += self.power.value / 60
        await self._storage.set_value(value=int(consumption.value / 10), **consumption.config)

    async def __check_and_reset_consumtption(self):
        if self.__last_consumption_reset_time >= CONSUMPTION_RESET_PERIOD:
            self.day_consumption.value = 0
            self.night_consumption.value = 0
            self.__last_consumption_reset_time = 0

            await self._storage.set_value(value=self.day_consumption.value, **self.day_consumption.config)
            await self._storage.set_value(value=self.night_consumption.value, **self.night_consumption.config)
        else:
            self.__last_consumption_reset_time += 1
