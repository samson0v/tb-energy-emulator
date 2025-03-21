from enum import Enum
import random
from tb_energy_emulator.device import BaseDevice


class Mode(Enum):
    ON = 0
    CHARGER_ONLY = 1
    INVERTER_ONLY = 2
    OFF = 3


class ChargeMode(Enum):
    MAINS_ON = 0
    BULK = 1
    ABSORPTION = 2
    FLOAT = 3


class Inverter(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\tmode: {self.mode}' \
            f'\n\tinput voltage: ({self.input_voltage_l1}, {self.input_voltage_l2}, {self.input_voltage_l3})' \
            f'\n\toutput voltage: ({self.output_voltage_l1}, {self.output_voltage_l2}, {self.output_voltage_l3})' \
            f'\n\ttemperature: ({self.temperature_l1}, {self.temperature_l2}, {self.temperature_l3})' \
            f'\n\ttotal current: {self.current} A, ' \
            f'currents: ({self.current_l1}, {self.current_l2}, {self.current_l3})' \
            f'\n\ttotal output power: {self.power}, ' \
            f'output power: ({self.power_l1}, {self.power_l2}, {self.power_l3})' \
            f'\n\tcharger mode: {self.charger_mode}'

    async def off(self):
        await super().off()

        self.current.value = 0
        self.current_l1.value = 0
        self.current_l2.value = 0
        self.current_l3.value = 0

        self.power.value = 0
        self.power_l1.value = 0
        self.power_l2.value = 0
        self.power_l3.value = 0

        self.output_voltage_l1.value = 0
        self.output_voltage_l2.value = 0
        self.output_voltage_l3.value = 0

        self.input_voltage_l1.value = 0
        self.input_voltage_l2.value = 0
        self.input_voltage_l3.value = 0

        await self._storage.set_value(value=self.current.value, **self.current.config)
        await self._storage.set_value(value=self.current_l1.value, **self.current_l1.config)
        await self._storage.set_value(value=self.current_l2.value, **self.current_l2.config)
        await self._storage.set_value(value=self.current_l3.value, **self.current_l3.config)

        await self._storage.set_value(value=self.power.value, **self.power.config)
        await self._storage.set_value(value=self.power_l1.value, **self.power_l1.config)
        await self._storage.set_value(value=self.power_l2.value, **self.power_l2.config)
        await self._storage.set_value(value=self.power_l3.value, **self.power_l3.config)

        await self._storage.set_value(value=self.output_voltage_l1.value, **self.output_voltage_l1.config)
        await self._storage.set_value(value=self.output_voltage_l2.value, **self.output_voltage_l2.config)
        await self._storage.set_value(value=self.output_voltage_l3.value, **self.output_voltage_l3.config)

        await self._storage.set_value(value=self.input_voltage_l1.value, **self.input_voltage_l1.config)
        await self._storage.set_value(value=self.input_voltage_l2.value, **self.input_voltage_l2.config)
        await self._storage.set_value(value=self.input_voltage_l3.value, **self.input_voltage_l3.config)

    async def update(self, solar_batteries, wind_turbine, power_transformer, generator, batteries, consumption):
        await super().update()
        await self.__check_and_update_mode()

        if self.running.value:
            await self.__update_input_voltage()
            await self.__update_output_voltage()
            await self.__update_temperatures()

            await self.get_output(solar_batteries,
                                  wind_turbine,
                                  power_transformer,
                                  generator,
                                  batteries,
                                  consumption)
            await self.__update_output_current()
            await self.__update_output_power()
        else:
            await self.__decrease_temperatures()

    async def get_output(self, solar_batteries, wind_turbine, power_transformer, generator, batteries, consumption):
        batteries_input = 0
        self.power.value = 0  # NOTE: consumption output

        if self.mode.value == Mode.INVERTER_ONLY.value:
            batteries_input = 0
            self.power.value = await batteries.discharge(consumption.needed_consumption)
        elif self.mode.value == Mode.CHARGER_ONLY.value:
            batteries_input = self.get_power_for_batteries_charging(solar_batteries,
                                                                    wind_turbine,
                                                                    power_transformer,
                                                                    generator)

            await batteries.update(batteries_input)
            await self.update_charger_mode(batteries.charge_current.value)

            self.power.value = 0
        elif self.mode.value == Mode.ON.value:
            batteries_input = self.get_power_for_batteries_charging(solar_batteries,
                                                                    wind_turbine,
                                                                    power_transformer,
                                                                    generator)

            await batteries.update(batteries_input)
            await self.update_charger_mode(batteries.charge_current.value)
            self.power.value = await batteries.discharge(consumption.needed_consumption)

            if self.power.value < consumption.needed_consumption:
                needed_power = consumption.needed_consumption - self.power.value
                self.power.value = self.find_power_for_consumption(generator,
                                                                   power_transformer,
                                                                   needed_power)

        await self._storage.set_value(value=int(self.power.value), **self.power.config)

        if consumption.needed_consumption > self.power.value:
            consumption.off()
        else:
            consumption.on(with_init_values=False)

    def get_power_for_batteries_charging(self, solar_batteries, wind_turbine, power_transformer, generator):
        total_power_output = 0

        if solar_batteries.output_power.value > 0:
            total_power_output += solar_batteries.output_power.value

        if wind_turbine.output_power.value > 0:
            total_power_output += wind_turbine.output_power.value

        if total_power_output == 0:
            if power_transformer.power.value > 0:
                total_power_output += power_transformer.power.value

        if total_power_output == 0:
            if generator.output_power.value > 0:
                total_power_output += generator.output_power.value

        return total_power_output

    def find_power_for_consumption(self, generator, power_transformer, needed_power):
        output_power = 0

        if generator.output_power.value > 0:
            output_power += generator.output_power.value

        if output_power < needed_power:
            if power_transformer.power.value > 0:
                output_power += power_transformer.power.value

        return output_power

    async def __check_and_update_mode(self):
        mode = await self._storage.get_value(**self.mode.config)

        if mode != self.mode.value:
            self.mode.value = mode
            await self._storage.set_value(value=self.mode.value, **self.mode.config)

            await self.__update_running()

    async def __update_running(self):
        if self.mode.value == Mode.ON.value:
            await self.on()
        elif self.mode.value == Mode.OFF.value:
            await self.off()

    async def __update_input_voltage(self):
        self.input_voltage_l1.generate_value()
        self.input_voltage_l2.generate_value()
        self.input_voltage_l3.generate_value()

        await self._storage.set_value(value=self.input_voltage_l1.value, **self.input_voltage_l1.config)
        await self._storage.set_value(value=self.input_voltage_l2.value, **self.input_voltage_l2.config)
        await self._storage.set_value(value=self.input_voltage_l3.value, **self.input_voltage_l3.config)

    async def __update_output_voltage(self):
        self.output_voltage_l1.generate_value()
        self.output_voltage_l2.generate_value()
        self.output_voltage_l3.generate_value()

        await self._storage.set_value(value=self.output_voltage_l1.value, **self.output_voltage_l1.config)
        await self._storage.set_value(value=self.output_voltage_l2.value, **self.output_voltage_l2.config)
        await self._storage.set_value(value=self.output_voltage_l3.value, **self.output_voltage_l3.config)

    async def __update_temperatures(self):
        self.__update_temperature(self.temperature_l1)
        self.__update_temperature(self.temperature_l2)
        self.__update_temperature(self.temperature_l3)

        await self._storage.set_value(value=int(self.temperature_l1.value), **self.temperature_l1.config)
        await self._storage.set_value(value=int(self.temperature_l2.value), **self.temperature_l2.config)
        await self._storage.set_value(value=int(self.temperature_l3.value), **self.temperature_l3.config)

    def __update_temperature(self, temperature):
        if temperature.value < temperature.max_value - 10:
            temperature.value += 1
        elif 39 <= temperature.value:
            temperature.generate_value()

    async def __decrease_temperatures(self):
        self.decrease_temperature(self.temperature_l1)
        self.decrease_temperature(self.temperature_l2)
        self.decrease_temperature(self.temperature_l3)

        await self._storage.set_value(value=self.temperature_l1.value, **self.temperature_l1.config)
        await self._storage.set_value(value=self.temperature_l2.value, **self.temperature_l2.config)
        await self._storage.set_value(value=self.temperature_l3.value, **self.temperature_l3.config)

    def decrease_temperature(self, temperature):
        if temperature.value > temperature.min_value:
            temperature.value -= 1

    async def update_charger_mode(self, charge_current):
        if charge_current > 30:
            self.charger_mode.value = ChargeMode.MAINS_ON.value
        elif charge_current == 30:
            self.charger_mode.value = ChargeMode.BULK.value
        elif charge_current == 10:
            self.charger_mode.value = ChargeMode.ABSORPTION.value
        else:
            self.charger_mode.value = ChargeMode.FLOAT.value

    async def __update_output_current(self):
        self.current.generate_value()
        current_1, current_2, current_3 = self.distibute_value(self.current.get_value_without_multiplier())

        self.current_l1.value = current_1
        self.current_l2.value = current_2
        self.current_l3.value = current_3

        await self._storage.set_value(value=self.current.value, **self.current.config)
        await self._storage.set_value(value=int(self.current_l1.value), **self.current_l1.config)
        await self._storage.set_value(value=int(self.current_l2.value), **self.current_l2.config)
        await self._storage.set_value(value=int(self.current_l3.value), **self.current_l3.config)

    async def __update_output_power(self):
        power_1, power_2, power_3 = self.distibute_value(self.power.value)

        self.power_l1.value = power_1
        self.power_l2.value = power_2
        self.power_l3.value = power_3

        await self._storage.set_value(value=int(self.power_l1.value), **self.power_l1.config)
        await self._storage.set_value(value=int(self.power_l2.value), **self.power_l2.config)
        await self._storage.set_value(value=int(self.power_l3.value), **self.power_l3.config)

    def distibute_value(self, value, values_num=3, deviation=0.1):
        base_value = value // values_num
        min_value = int(base_value * (1 - deviation))
        max_value = int(base_value * (1 + deviation))

        values = [random.randint(min_value, max_value) for _ in range(values_num - 1)]

        last_value = value - sum(values)
        values.append(last_value)

        if last_value < min_value:
            diff = min_value - last_value
            values[-1] = min_value
            values[values.index(max(values[:-1]))] -= diff
        elif last_value > max_value:
            diff = last_value - max_value
            values[-1] = max_value
            values[values.index(min(values[:-1]))] += diff

        return values
