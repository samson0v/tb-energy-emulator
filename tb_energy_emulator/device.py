from abc import abstractmethod
import asyncio
import logging
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, isclass
from os import listdir, path

from tb_energy_emulator.sensor import Sensor
from tb_energy_emulator.storages.modbus.modbus_store import ModbusStore
from tb_energy_emulator.storages.opcua.opcua_store import OpcuaStore


STORES = {
    'modbus': ModbusStore,
    'opcua': OpcuaStore
}


class BaseDevice:
    def __init__(self, config, storage_type, clock):
        self.__config = config
        self._clock = clock
        self.__name = config.get('name')
        self.__log = logging.getLogger(self.__name)
        self.__storage_type = storage_type

        self.__load_class_attributes()

        self._storage = self.__create_storage()

    def __str__(self):
        return self.__dict__.__str__()

    @abstractmethod
    def update(self):
        pass

    @property
    def name(self):
        return self.__name

    def __load_class_attributes(self):
        self.__log.info('\tLoading sensors...')

        for sensor_config in self.__config.get('values', []):
            try:
                sensor_obj = Sensor(self.__storage_type, sensor_config)
                self.__log.info(f'\t- {sensor_config['name']} sensor added')
                setattr(self, sensor_config['name'], sensor_obj)
            except Exception as e:
                self.__log.error(f'{sensor_config['name']} sensor loading failed: {e}')

        self.__log.info('\t[✔] Sensors loaded')

    def __create_storage(self):
        self.__log.info('\tCreating storage...')
        if self.__storage_type not in STORES:
            self.__log.error(f'Unknown store type: {self.__storage_type}. Using default: modbus')
            return ModbusStore(self.__config)

        storage = STORES[self.__storage_type](self.__config)

        self.__log.info('\t[✔] Storage created')
        return storage

    async def __init_storage_values(self):
        self.__log.info('Initializing storage values...')

        for value_config in self.__config.get('values', []):
            try:
                init_value = value_config['initValue']
                await self._storage.set_value(value=init_value, **value_config[self.__storage_type])

                self.__log.info(f'\t- {value_config['name']} initialized with value: {init_value}')
            except Exception as e:
                self.__log.error(f'{value_config['name']} value loading failed: {e}')
                continue

        self.__log.info('[✔] Storage values initialized')

    async def start(self):
        await self._storage.start()

    async def on(self, with_init_values=True):
        if with_init_values:
            await self.__init_storage_values()

        self.running.value = True
        await self._storage.set_value(value=self.running.value, **self.running.config)

    async def off(self):
        self.running.value = False
        await self._storage.set_value(value=self.running.value, **self.running.config)

        print(self._storage._ModbusStore__storage.store['c'].values[0:10])


class Devices:
    def __init__(self):
        self.__log = logging.getLogger('Devices')
        self.__devices = {}

    def add_device(self, device: BaseDevice):
        self.__devices[device.name] = device
        self.__log.info(f'\t[✔] {device.name} device loaded')

    def get_device_by_name(self, name):
        return self.__devices.get(name)

    def load_devices(self, config, clock):
        self.__log.info('Loading devices...')

        for device_config in config.get('devices', []):
            device_class = DeviceModuleLoader.import_module(device_config.get('className', 'name'))
            if not issubclass(device_class, BaseDevice):
                self.__log.error(f'\t{device_config['name']} device loading failed: {device_class}')
                continue

            self.__log.info(f'\tLoading {device_config['name']} device...')

            storage_type = device_config.get('storageType', config.get('storeType', 'modbus'))
            device = device_class(device_config, storage_type, clock)

            self.add_device(device)

        self.__log.info('[✔] Devices loaded')

    async def start(self):
        asyncio.gather(*[device.start() for device in self.__devices.values()])

    async def on(self):
        for device in self.__devices.values():
            await device.on()

    async def off(self):
        for device in self.__devices.values():
            await device.off()

    async def update(self):
        for device in self.__devices.values():
            await device.update()

    def log_values(self):
        for device in self.__devices.values():
            self.__log.info(device)


class DeviceModuleLoader:
    ROOT_PATH = path.abspath(path.dirname(__file__))
    DEVICES_FOLDER = ROOT_PATH + path.sep + 'devices'
    LOADED_DEVICES = {}

    @staticmethod
    def import_module(module_name, extension_type=None):
        errors = []

        if extension_type:
            buffered_module_name = extension_type + module_name
        else:
            buffered_module_name = module_name

        if DeviceModuleLoader.LOADED_DEVICES.get(buffered_module_name):
            return DeviceModuleLoader.LOADED_DEVICES[buffered_module_name]

        try:
            current_extension_path = DeviceModuleLoader.DEVICES_FOLDER

            if extension_type:
                current_extension_path += path.sep + extension_type

            if path.exists(current_extension_path):
                for file in listdir(current_extension_path):
                    if not file.startswith('__') and (file.endswith('.py') or file.endswith('.pyc')):
                        try:
                            module_spec = spec_from_file_location(module_name,
                                                                  current_extension_path + path.sep + file)

                            if module_spec is None:
                                continue

                            module = module_from_spec(module_spec)
                            module_spec.loader.exec_module(module)
                            for extension_class in getmembers(module, isclass):
                                if module_name in extension_class:
                                    DeviceModuleLoader.LOADED_DEVICES[buffered_module_name] = extension_class[1]
                                    return extension_class[1]
                        except ImportError as e:
                            errors.append(e.msg)
                            continue
        except Exception as e:
            errors.append(e)
        return errors
