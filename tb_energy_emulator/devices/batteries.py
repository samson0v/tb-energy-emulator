from enum import Enum

from tb_energy_emulator.constants import (
    CAPACITY_WH,
    CHARGIN_DURATION_AFTER_80_PERCENT,
    CHARGING_DURATION_IN_HOURS,
    MAX_CHARGING_LEVEL_WITH_BATTERY_LIFE
)
from tb_energy_emulator.device import BaseDevice


class BatteriesMode(Enum):
    OPTIMIZED_WITH_BATTERY_LIFE = 0
    OPTIMIZED_WITHOUT_BATTERY_LIFE = 1
    KEEP_BATTERY_CHARGED = 2
    EXTERNAL_CONTROL = 3


class Batteries(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)

        self.__charging = False
        self.__capacity_Wh = CAPACITY_WH
        self.__charging_duration_in_hours = CHARGING_DURATION_IN_HOURS
        self.__last_updated_level = 0

    def __str__(self):
        return f'\n{self.name} (running: {self.running}): ' \
            f'\n\tbattery 1: {self.running_1}, battery 2: {self.running_2} ' \
            f'battery 3: {self.running_3}, battery 4: {self.running_4} ' \
            f'battery 5: {self.running_5}' \
            f'\n\tbatteries mode: {self.batteries_mode}' \
            f'\n\tlevel: {self.level} %, current: {self.charge_current} A, voltage: {self.voltage} V' \
            f'\n\ttemperature: {self.temperature} °C, cycle count: {self.cycle_count}'

    def get_all_bateries(self):
        return [self.running_1, self.running_2, self.running_3, self.running_4, self.running_5]

    async def off(self):
        await super().off()

        await self.__off_all_batteries()

    async def on(self, with_init_values=True):
        await super().on(with_init_values)

        await self.__on_all_batteries()

    async def __off_all_batteries(self):
        for battery in self.get_all_bateries():
            battery.value = False
            await self._storage.set_value(value=battery.value, **battery.config)

    async def __on_all_batteries(self):
        for battery in self.get_all_bateries():
            battery.value = True
            await self._storage.set_value(value=battery.value, **battery.config)

    async def update(self, input_power):
        await super().update()

        if self.running.value:
            await self.__check_and_update_states()
            await self.__check_and_update_batteries_mode()
            await self.__update_temperature()

            await self.__update_cycle_count()
            await self.charge(input_power)
        else:
            self.__decrease_temperature()

    async def __update_cycle_count(self):
        if self.level.value == 0:
            self.cycle_count.value += 1
            await self._storage.set_value(value=self.cycle_count.value, **self.cycle_count.config)

    async def charge(self, input_power):
        if self.__last_updated_level < self._clock.hours:
            self.__reset_charging_duration()

            if self.batteries_mode.value == BatteriesMode.KEEP_BATTERY_CHARGED.value:
                self.__charge_with_keep_battery_charged_mode(input_power)
            elif self.batteries_mode.value == BatteriesMode.EXTERNAL_CONTROL.value:
                self.__charge_with_optimized_without_battery_life_mode(input_power)
            elif self.batteries_mode.value == BatteriesMode.OPTIMIZED_WITHOUT_BATTERY_LIFE.value:
                self.__charge_with_optimized_without_battery_life_mode(input_power)
            elif self.batteries_mode.value == BatteriesMode.OPTIMIZED_WITH_BATTERY_LIFE.value:
                self.__charge_with_optimized_with_battery_life_mode(input_power)
            else:
                self._log.warning(f'Unknown batteries mode: {self.batteries_mode.value}. '
                                  'Using default mode: KEEP BATTERY CHARGED')
                self.__charge_with_keep_battery_charged_mode(input_power)

            await self._storage.set_value(value=int(self.level.value), **self.level.config)
            await self._storage.set_value(value=int(self.charge_current.value), **self.charge_current.config)
            await self._storage.set_value(value=self.voltage.value, **self.voltage.config)

            self.__last_updated_level = self._clock.hours

    async def discharge(self, input_power):
        output_power = await self.__discharge(input_power)

        await self._storage.set_value(value=int(self.level.value), **self.level.config)
        await self._storage.set_value(value=int(self.discharge_current.value), **self.discharge_current.config)
        await self._storage.set_value(value=self.voltage.value, **self.voltage.config)

        return output_power

    async def __discharge(self, input_power):
        output_power = 0

        if self.level.value > 0:
            self.discharge_current.value = input_power / self.voltage.get_value_without_multiplier()

            if self.discharge_current.value > self.discharge_current.max_value:
                input_power = self.discharge_current.max_value * self.voltage.get_value_without_multiplier()
                self.discharge_current.value = self.discharge_current.max_value

            current_energy_Wh = (self.level.value / 100) * self.__capacity_Wh
            new_energy_Wh = current_energy_Wh - input_power

            if new_energy_Wh < 0:
                new_energy_Wh = 0
                output_power = 0
            else:
                output_power = input_power

            self.level.value = (new_energy_Wh / self.__capacity_Wh) * 100

        return output_power

    def __charge_with_keep_battery_charged_mode(self, input_power):
        if self.level.value < 100 and input_power > 0:
            self.__calculate_charge_current(input_power)

            energy_added_Wh = input_power * self.__charging_duration_in_hours
            current_energy_Wh = (self.level.value / 100) * self.__capacity_Wh
            new_energy_Wh = current_energy_Wh + energy_added_Wh

            if new_energy_Wh > self.__capacity_Wh:
                new_energy_Wh = self.__capacity_Wh

            self.level.value = (new_energy_Wh / self.__capacity_Wh) * 100

    def __charge_with_optimized_with_battery_life_mode(self, input_power):
        if self.level.value < MAX_CHARGING_LEVEL_WITH_BATTERY_LIFE and input_power > 0:
            self.__calculate_charge_current(input_power)

            energy_added_Wh = input_power * self.__charging_duration_in_hours
            current_energy_Wh = (self.level.value / 100) * self.__capacity_Wh
            new_energy_Wh = current_energy_Wh + energy_added_Wh

            if new_energy_Wh > self.__capacity_Wh:
                new_energy_Wh = self.__capacity_Wh

            self.level.value = (new_energy_Wh / self.__capacity_Wh) * 100

    def __charge_with_optimized_without_battery_life_mode(self, input_power):
        if self.level.value < 100 and input_power > 0:
            self.__calculate_charge_current(input_power)

            if self.level.value > 80:
                self.__charging_duration_in_hours = CHARGIN_DURATION_AFTER_80_PERCENT

            energy_added_Wh = input_power * self.__charging_duration_in_hours
            current_energy_Wh = (self.level.value / 100) * self.__capacity_Wh
            new_energy_Wh = current_energy_Wh + energy_added_Wh

            if new_energy_Wh > self.__capacity_Wh:
                new_energy_Wh = self.__capacity_Wh

            self.level.value = (new_energy_Wh / self.__capacity_Wh) * 100

    def __calculate_charge_current(self, input_power):
        if self.level.value <= 85:
            self.charge_current.value = input_power / self.voltage.get_value_without_multiplier()

            if self.charge_current.value > self.charge_current.max_value:
                input_power = self.charge_current.max_value * self.voltage.get_value_without_multiplier()
                self.charge_current.value = self.charge_current.max_value
        elif 85 < self.level.value >= 95:
            self.charge_current.value = 30
        elif self.level.value > 95 and self.level.value < 100:
            self.charge_current.value = 10
        else:
            self.charge_current.value = 0

    async def __check_and_update_states(self):
        for battery in self.get_all_bateries():
            await self.__check_state(battery)

    async def __check_state(self, battery):
        is_running = bool(await self._storage.get_value(**battery.config))

        if is_running != battery.value:
            battery.value = is_running
            await self._storage.set_value(value=battery.value, **battery.config)

            await self.__update_batteries_perfomance(battery.value)

    async def __update_batteries_perfomance(self, is_battery_plugged):
        if not is_battery_plugged:
            self.level.value -= 100 / len(self.get_all_bateries())
            self.charge_current.value -= 79 / len(self.get_all_bateries())
            self.__capacity_Wh -= 15000
        else:
            self.level.value += 100 / len(self.get_all_bateries())
            self.charge_current.value += 79 / len(self.get_all_bateries())
            self.__capacity_Wh += 15000

        await self._storage.set_value(value=int(self.level.value), **self.level.config)
        await self._storage.set_value(value=int(self.charge_current.value), **self.charge_current.config)

    async def __check_and_update_batteries_mode(self):
        batteries_mode = await self._storage.get_value(**self.batteries_mode.config)

        if batteries_mode != self.batteries_mode.value:
            self.batteries_mode.value = batteries_mode
            await self._storage.set_value(value=self.batteries_mode.value, **self.batteries_mode.config)

    async def __update_temperature(self):
        if self.__charging:
            if self.temperature.value <= self.temperature.max_value:
                self.temperature.value += 1
        else:
            if self.temperature.value >= 40:
                self.temperature.value -= 1

        await self._storage.set_value(value=self.temperature.value, **self.temperature.config)

    async def __decrease_temperature(self):
        if self.temperature.value > self.temperature.min_value:
            self.temperature.value -= 1
            await self._storage.set_value(value=self.temperature.value, **self.temperature.config)

    def __reset_charging_duration(self):
        self.__charging_duration_in_hours = CHARGING_DURATION_IN_HOURS
