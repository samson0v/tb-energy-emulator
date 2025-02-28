# ThingsBoard Energy Emulator

This is a simple modbus/opc-ua energy emulator that can be used to test Modbus/OPC-UA integration with platform using ThingsBoard IoT Gateway.

## Devices

- Generator
- Consumption

## Devices Structure

### Modbus Servers

| Device     | Unit Id | Port  |
| ---------- | :------ | :---: |
| Consuption | 1       | 5021  |
| Generator  | 1       | 5022  |

### Consuption

| Sensors        | Default value | Modbus Register Type | Modbus Address |
| :------------- | :-----------: | -------------------- | -------------: |
| Voltage L1     |      221      | HR                   |              1 |
| Voltage L2     |      221      | HR                   |              2 |
| Voltage L3     |      221      | HR                   |              3 |
| Frequency L1   |      50       | HR                   |              4 |
| Frequency L2   |      50       | HR                   |              5 |
| Frequency L3   |      50       | HR                   |              6 |
| Consumption L3 |               | HR                   |              7 |
| Consumption L3 |               | HR                   |              8 |
| Consumption L3 |               | HR                   |              9 |
| Running        |     False     | CO                   |              1 |

### Generator

| Sensors         | Default value | Modbus Register Type | Modbus Address |
| :-------------- | :-----------: | -------------------- | -------------: |
| Oil Temperature |      11       | HR                   |              1 |
| Frequency       |      50       | HR                   |              2 |
| Voltage         |      221      | HR                   |              3 |
| Fuel Level      |      100      | HR                   |              4 |
| Output Power    |     20000     | HR                   |              5 |
| Current         |      101      | HR                   |              6 |
| Running         |     False     | CO                   |              1 |

### OPC-UA Servers

| Device     | Host                                     |
| ---------- | :--------------------------------------- |
| Consuption | opc.tcp://0.0.0.0:4841/freeopcua/server/ |
| Generator  | opc.tcp://0.0.0.0:4840/freeopcua/server/ |

###  Consuption

| Sensors        | Default value | Modbus Register Type |
| :------------- | :-----------: | -------------------- |
| Voltage L1     |      221      | ns=1; s=VoltageL1    |
| Voltage L2     |      221      | ns=1; s=VoltageL2    |
| Voltage L3     |      221      | ns=1; s=VoltageL3    |
| Frequency L1   |      50       | ns=1; s=VoltageL1    |
| Frequency L2   |      50       | ns=1; s=VoltageL2    |
| Frequency L3   |      50       | ns=1; s=VoltageL3    |
| Consumption L3 |               | ns=1; s=FrequencyL1  |
| Consumption L3 |               | ns=1; s=FrequencyL2  |
| Consumption L3 |               | ns=1; s=FrequencyL3  |
| Running        |     False     | CO                   |

### Generator

| Sensors         | Default value | Modbus Register Type   |
| :-------------- | :-----------: | ---------------------- |
| Oil Temperature |      11       | ns=1; s=OilTemperature |
| Frequency       |      50       | ns=1; s=Frequency      |
| Voltage         |      221      | ns=1; s=Voltage        |
| Fuel Level      |      100      | ns=1; s=FuelLevel      |
| Output Power    |     20000     | ns=1; s=OutputPower    |
| Current         |      101      | ns=1; s=Current        |
| Running         |     False     | ns=1; i=Running        |

## Installation

1. Pull emulator docker image:
    ```bash
    docker pull thingsboard/tb-energy-emulator:latest
    ```
2. Run the emulator using the following command, which will start the emulator on ports 5021-5025:
    ```bash
    docker run --rm -d --name tb-energy-emulator -p 5021-5025:5021-5025 tb-modbus-drilling-rig-emulator
    ```
   ***Note***: *If you run the gateway first - it may take up to 2 minutes since the emulator starts to the gateway
   connects to it*.
3. Create a new gateway device in ThingsBoard and copy the access token.
4. Pull gateway image from Dockerhub using the following command:
    ```bash
    docker pull thingsboard/tb-gateway:latest
    ```
5. Replace YOUR_ACCESS_TOKEN with the access token of the gateway device and host (if you want to connect to
   ThingsBoard, not on your machine) in docker-compose.yml.
6. Run the gateway using the following command:
    ```bash
    docker-compose up
    ```
7. Add Modbus connector and configure the ThingsBoard IoT Gateway on UI to connect to the emulated devices. You can find
   configuration in *modbus_configuration.json*.
8. The gateway connects to emulated devices, creates them on the platform, starts receive data from devices and send it
   to ThingsBoard.
