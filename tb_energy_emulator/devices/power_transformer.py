from tb_energy_emulator.device import BaseDevice


class PowerTransformer(BaseDevice):
    def __init__(self, config, storage_type, clock):
        super().__init__(config, storage_type, clock)
