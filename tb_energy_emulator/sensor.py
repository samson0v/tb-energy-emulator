import random


class Sensor:
    def __init__(self, storage_type, config):
        self.storage_type = storage_type

        if self.storage_type == 'opcua':
            self.__config = config.get('opcua')
        else:
            self.__config = config.get('modbus')

        self.__value = config.get('initValue', 0)
        self.min_value = config.get('minValue')
        self.max_value = config.get('maxValue')
        self.__deviation = config.get('deviation', 1)

    def __str__(self):
        return f'{self.value}'

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.min_value and self.max_value:
            if self.min_value >= value >= self.max_value:
                raise ValueError(f'Value {value} is out of range [{self.min_value}, {self.max_value}]')

        self.__value = value

    @property
    def config(self):
        return self.__config

    @property
    def address(self):
        if self.storage_type == 'opcua':
            return self.__config['nodeId']
        else:
            return self.__config['address']

    @property
    def modbus_register_type(self):
        return self.__config.get('registerType')

    @property
    def opcua_data_type(self):
        return self.__config.get('dataType')

    def generate_value(self):
        new_number = self.value + random.randint(-self.__deviation, self.__deviation)
        self.value = max(self.min_value, min(self.max_value, new_number))
