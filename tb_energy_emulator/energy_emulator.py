import asyncio
import logging

from tb_energy_emulator.emulator import Emulator


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TbEnergyEmulator(Emulator):
    def __init__(self, config_path):
        super().__init__(config_path)

    async def run(self):
        await super()._run()

        await self._devices.start()
        await self._devices.on()

        while self._running:
            self._log.info(f'{self._clock}')

            power_transformer = self._devices.get_device_by_name('Power Transformer')
            await power_transformer.update_running_status()

            wind_turbine = self._devices.get_device_by_name('Wind Turbine')
            await wind_turbine.update()

            solar_batteries = self._devices.get_device_by_name('Solar Batteries')
            await solar_batteries.update()

            generator = self._devices.get_device_by_name('Generator')
            await generator.update_running_status()

            consumption = self._devices.get_device_by_name('Consumption')
            batteries = self._devices.get_device_by_name('Batteries')
            inverter = self._devices.get_device_by_name('Inverter')

            await inverter.update(solar_batteries,
                                  wind_turbine,
                                  power_transformer,
                                  generator,
                                  batteries,
                                  consumption)

            self._devices.log_values()

            await self._clock.tick()


if __name__ == '__main__':
    config_path = './config.json'
    emulator = TbEnergyEmulator(config_path=config_path)

    try:
        asyncio.run(emulator.run())
    except KeyboardInterrupt:
        pass
