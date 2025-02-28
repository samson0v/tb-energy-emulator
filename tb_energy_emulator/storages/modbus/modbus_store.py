import asyncio
from typing import Dict, Any

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext

from tb_energy_emulator.storage import Storage


class ModbusStore(Storage):
    def __init__(self, config):
        self.__running = False
        self.__server_config = config.get('modbusSettings', {})

        self.__identity = self.__setup_identity()
        self.__devices_context = self.__setup_devices_context()

    @staticmethod
    def __setup_identity():
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'ThingsBoard'
        identity.ProductCode = 'EnergyEmulator'
        identity.VendorUrl = 'https://thingsboard.io/'
        identity.ProductName = 'Energy Emulator'
        identity.ModelName = 'Modbus TCP Emulator'
        identity.MajorMinorRevision = '1.0'

        return identity

    def __setup_devices_context(self):
        self.__storage = ModbusSlaveContext()
        return ModbusServerContext(slaves={self.__server_config['slaveId']: self.__storage}, single=False)

    async def start(self):
        if self.__running:
            return

        await asyncio.create_task(self.__start_server(self.__server_config['port'], self.__devices_context))

    async def __start_server(self, port, context):
        await StartAsyncTcpServer(context=context, identity=self.__identity, address=("0.0.0.0", port))

    def update_values(self, values: Dict[str, Any]) -> None:
        pass

    async def set_value(self, function_code=None, address=None, value=None, **kwargs) -> None:
        if function_code is None or address is None or value is None:
            raise ValueError('Invalid arguments')

        self.__storage.setValues(function_code, address, [value])

    def get_value(self, key: str) -> Any:
        pass
