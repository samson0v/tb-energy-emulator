import asyncio
import logging
from json import load

from tb_energy_emulator.device import Devices
from tb_energy_emulator.clock import Clock


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Emulator:
    def __init__(self, config_path):
        self._log = logging.getLogger('TbEnergyEmulator')

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._config = self.__load_config(config_path)

        self._clock = Clock(float(self._config.get('globalClockUpdateFrequency', 1.0)))

        self._running = False

        self._devices = Devices()
        self._devices.load_devices(self._config, self._clock)

    @staticmethod
    def __load_config(config_path):
        with open(config_path, 'r') as config_file:
            return load(config_file)

    async def _run(self):
        self._running = True
