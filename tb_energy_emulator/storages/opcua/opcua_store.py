import logging
from typing import Dict, Any

from asyncua import ua, Server

from tb_energy_emulator.storage import Storage


class OpcuaStore(Storage):
    def __init__(self, config):
        self.__log = logging.getLogger('OpcuaStore')
        self.__running = False
        self.__config = config['opcuaSettings']
        self.__uri = 'http://thingsboard.github.io'
        self.__idx = None
        self.__main_device = None
        self.__server = Server()

        self.__setup_server()

    def __setup_server(self):
        self.__server.set_endpoint(self.__config['host'])
        self.__server.set_server_name('TB Energy Emulator OPC UA Server')
        self.__server.set_security_policy(
            [
                ua.SecurityPolicyType.NoSecurity
            ]
        )

    async def start(self):
        if self.__running:
            return

        await self.__start_server()

    async def __start_server(self):
        await self.__server.init()
        self.__idx = await self.__server.register_namespace(self.__uri)
        device_type = await self.__server.nodes.base_object_type.add_object_type(self.__idx, "MainDevice")
        self.__main_device = await self.__server.nodes.objects.add_object(self.__idx, "MainDevice", device_type)
        await self.__server.start()

    def update_values(self, values: Dict[str, Any]) -> None:
        pass

    async def set_value(self, node_id=None, value=None, name=None) -> None:
        if node_id is None or value is None:
            raise ValueError('Invalid arguments')

        if name:
            await self.__main_device.add_variable(node_id, name, value)
        else:
            await self.__server.write_attribute_value(node_id, value)

    def get_value(self, key: str) -> Any:
        pass
