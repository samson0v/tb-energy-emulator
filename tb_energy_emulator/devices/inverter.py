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

        self.__only_charge_batteries = False
        self.__green_energy_system_off = False

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

        await self.__update_input_voltage()
        await self.__update_output_voltage()
        await self.__update_temperatures()

        await self.get_output(solar_batteries,
                              wind_turbine,
                              power_transformer,
                              generator,
                              batteries,
                              consumption)
        await self.__update_output_power()
        await self.__update_output_current()

    async def get_output(self, solar_batteries, wind_turbine, power_transformer, generator, batteries, consumption):
        self.power.value = 0  # NOTE: consumption output

        if self.mode.value == Mode.INVERTER_ONLY.value:
            await power_transformer.update(0)
            await self.__on_green_energy(solar_batteries, wind_turbine)
            await self.__inverter_only_mode(solar_batteries,
                                            wind_turbine,
                                            generator,
                                            batteries,
                                            consumption)
        elif self.mode.value == Mode.CHARGER_ONLY.value:
            await self.__on_green_energy(solar_batteries, wind_turbine)
            await self.__charger_only_mode(solar_batteries,
                                           wind_turbine,
                                           power_transformer,
                                           generator,
                                           batteries,
                                           consumption)
        elif self.mode.value == Mode.ON.value:
            await self.__on_green_energy(solar_batteries, wind_turbine)
            await self.__on_mode(solar_batteries, wind_turbine, batteries, power_transformer, generator, consumption)
        elif self.mode.value == Mode.OFF.value:
            await self.__off_green_evergy(solar_batteries, wind_turbine)
            await self.__off_mode(generator, power_transformer, consumption)

        await self._storage.set_value(value=int(self.power.value), **self.power.config)

        await batteries.update()
        await self.__manage_consumption(consumption)

    async def __manage_consumption(self, consumption):
        if self.power.value == 0:
            await consumption.off()
        else:
            await consumption.on(with_init_values=False)

        await consumption.update(self.power.value)

    async def __on_green_energy(self, solar_batteries, wind_turbine):
        if self.__green_energy_system_off:
            await solar_batteries.on()
            await wind_turbine.on()

            self.__green_energy_system_off = False

    async def __off_green_evergy(self, solar_batteries, wind_turbine):
        if solar_batteries.running.value:
            self.__green_energy_system_off = True
            await solar_batteries.off()

        if wind_turbine.running.value:
            self.__green_energy_system_off = True
            await wind_turbine.off()

    async def __inverter_only_mode(self, solar_batteries, wind_turbine, generator, batteries, consumption):
        total_output_power = 0

        total_output_power += solar_batteries.output_power.value
        total_output_power += wind_turbine.output_power.value

        if total_output_power < consumption.needed_consumption:
            if batteries.running.value:
                needed_power = consumption.needed_consumption - total_output_power
                total_output_power += await batteries.discharge(needed_power)
            else:
                await batteries.reset_discharge_current()

        if total_output_power < consumption.needed_consumption:
            if generator.running.value:
                generator_input = consumption.needed_consumption - total_output_power
                await generator.update(generator_input)
                total_output_power += generator_input
        else:
            await generator.update(0)

        if total_output_power >= consumption.needed_consumption:
            self.power.value = consumption.needed_consumption
        else:
            self.power.value = total_output_power

    async def __charger_only_mode(self,
                                  solar_batteries,
                                  wind_turbine,
                                  power_transformer,
                                  generator,
                                  batteries,
                                  consumption):
        await batteries.reset_discharge_current()

        needed_power = consumption.needed_consumption + 2000 if batteries.level.value < 100 else consumption.needed_consumption
        total_power_output = await self.get_power_from_all_sources(solar_batteries,
                                                                   wind_turbine,
                                                                   power_transformer,
                                                                   generator,
                                                                   needed_power)

        if batteries.level.value < 100:
            batteries_input = total_power_output - consumption.needed_consumption if total_power_output > consumption.needed_consumption else 0
            total_power_output -= batteries_input
            await batteries.update(batteries_input)
            await self.update_charger_mode(batteries.charge_current.value)
        else:
            await batteries.reset_charge_current()

        if total_power_output >= consumption.needed_consumption:
            self.power.value = consumption.needed_consumption
        else:
            self.power.value = total_power_output

    async def __on_mode(self, solar_batteries, wind_turbine, batteries, power_transformer, generator, consumption):
        total_power_output = 0

        total_power_output += solar_batteries.output_power.value
        total_power_output += wind_turbine.output_power.value

        if total_power_output >= consumption.needed_consumption:
            batteries_input = total_power_output - consumption.needed_consumption
            await batteries.update(batteries_input)
            await self.update_charger_mode(batteries.charge_current.value)
            self.power.value = consumption.needed_consumption
        else:
            await batteries.reset_charge_current()
            needed_power = consumption.needed_consumption - total_power_output

            if self.__only_charge_batteries and batteries.level.value >= 80:
                self.__only_charge_batteries = False

            if batteries.level.value > 50 and batteries.running.value and not self.__only_charge_batteries:
                total_power_output += await batteries.discharge(needed_power)
                self.power.value = consumption.needed_consumption
                await power_transformer.update(0)
                await generator.update(0)
            else:
                await batteries.reset_discharge_current()
                self.__only_charge_batteries = True if batteries.running.value else False
                needed_power = needed_power + 2000 if batteries.level.value < 100 and batteries.running.value else needed_power
                await power_transformer.update(needed_power)
                total_power_output += power_transformer.power.value

                if total_power_output < consumption.needed_consumption:
                    await batteries.reset_charge_current()

                    if generator.running.value:
                        await generator.update(consumption.needed_consumption - total_power_output)
                        total_power_output = consumption.needed_consumption
                        self.power.value = total_power_output
                    else:
                        await generator.update(0)
                        self.power.value = total_power_output
                else:
                    self.power.value = consumption.needed_consumption
                    await generator.update(0)

                    batteries_input = total_power_output - consumption.needed_consumption
                    await batteries.update(batteries_input)
                    await self.update_charger_mode(batteries.charge_current.value)

    async def __off_mode(self, generator, power_transformer, consumption):
        self.power.value = await self.find_power_for_consumption(generator,
                                                                 power_transformer,
                                                                 consumption.needed_consumption)

    async def find_power_for_consumption(self, generator, power_transformer, needed_power):
        output_power = 0

        await power_transformer.update(needed_power)
        if power_transformer.power.value > 0:
            output_power += power_transformer.power.value

        if needed_power > output_power:
            if generator.running.value:
                await generator.update(needed_power - output_power)
                output_power = needed_power
        else:
            await generator.update(0)

        return output_power

    async def get_power_from_all_sources(self,
                                         solar_batteries,
                                         wind_turbine,
                                         power_transformer,
                                         generator,
                                         needed_power):
        total_power_output = 0

        total_power_output += solar_batteries.output_power.value
        total_power_output += wind_turbine.output_power.value

        if total_power_output < needed_power:
            await power_transformer.update(needed_power - total_power_output)
            total_power_output += power_transformer.power.value

            if total_power_output < needed_power:
                if generator.running.value:
                    await generator.update(needed_power - total_power_output)
                    total_power_output = needed_power
            else:
                await generator.update(0)

        return total_power_output

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

        await self._storage.set_value(value=self.charger_mode.value, **self.charger_mode.config)

    async def __update_output_current(self):
        self.current_l1.value = self.__calculate_current(self.power_l1.value,
                                                         self.output_voltage_l1.get_value_without_multiplier())
        self.current_l2.value = self.__calculate_current(self.power_l2.value,
                                                         self.output_voltage_l2.get_value_without_multiplier())
        self.current_l3.value = self.__calculate_current(self.power_l3.value,
                                                         self.output_voltage_l3.get_value_without_multiplier())

        self.current.value = round(self.current_l1.value + self.current_l2.value + self.current_l3.value, 1)

        await self._storage.set_value(value=self.current.value, **self.current.config)
        await self._storage.set_value(value=int(self.current_l1.value), **self.current_l1.config)
        await self._storage.set_value(value=int(self.current_l2.value), **self.current_l2.config)
        await self._storage.set_value(value=int(self.current_l3.value), **self.current_l3.config)

    def __calculate_current(self, power, voltage):
        return power / voltage

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
