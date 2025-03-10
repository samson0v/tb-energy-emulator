from enum import Enum

from tb_energy_emulator.device import BaseDevice


class PhaseMode(Enum):
    OFF = 0
    ON = 1
    BYPASS = 2


class PowerTransformer(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
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

    async def update(self):
        await super().update()

        if self.running.value:
            await self.__update_current()
            await self.__update_frequency()
            await self.__update_input_voltage()
            await self.__update_output_voltage()
            await self.__update_power_output()

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

    async def __update_power_output(self):
        if self.l1_mode.value == PhaseMode.ON.value:
            self.power.value = self.current.value * self.output_voltage_l1.get_value_without_multiplier()
        elif self.l2_mode.value == PhaseMode.ON.value:
            self.power.value = self.current.value * self.output_voltage_l2.get_value_without_multiplier()
        elif self.l3_mode.value == PhaseMode.ON.value:
            self.power.value = self.current.value * self.output_voltage_l3.get_value_without_multiplier()

        await self._storage.set_value(value=int(self.power.value), **self.power.config)
