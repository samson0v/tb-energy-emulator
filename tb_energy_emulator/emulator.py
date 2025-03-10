import asyncio
import logging
from json import load

from tb_energy_emulator.clocks.real_time_clock import RealtimeClock
from tb_energy_emulator.clocks.simulation_clock import SimulationClock
from tb_energy_emulator.device import Devices


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

CLOCK_TYPES = {
    'simulation': SimulationClock,
    'realtime': RealtimeClock
}


class Emulator:
    def __init__(self, config_path):
        self._log = logging.getLogger('TbEnergyEmulator')

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._config = self.__load_config(config_path)

        clock_type_name = self._config.get('clockType', 'simulation')
        self._clock = CLOCK_TYPES[clock_type_name](float(self._config.get('globalClockUpdateFrequency', 1.0)))

        self._running = False

        self._devices = Devices()
        self._devices.load_devices(self._config, self._clock)

    @staticmethod
    def __load_config(config_path):
        with open(config_path, 'r') as config_file:
            return load(config_file)

    async def _run(self):
        self._running = True
