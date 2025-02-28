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
        await self.start_generating()

        while self._running:
            self._log.info(f'{self._clock}')

            consumption = self._devices.get_device_by_name('Consumption')
            await consumption.update()
            generator = self._devices.get_device_by_name('Generator')
            await generator.update(consumption.needed_consumption)
            self._devices.log_values()

            await self._clock.tick()

    async def start_generating(self):
        self._devices.on()


if __name__ == '__main__':
    emulator = TbEnergyEmulator(config_path='/Users/vitaliibidochka/Documents/Python Projects/tb-energy-emulator/config.json')

    try:
        asyncio.run(emulator.run())
    except KeyboardInterrupt:
        pass
