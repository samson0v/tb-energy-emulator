# ThingsBoard Energy Emulator

This is a simple modbus/opc-ua energy emulator that can be used to test Modbus/OPC-UA integration with platform using ThingsBoard IoT Gateway.

## Devices

- Generator
- Consumption

## Devices Structure

### Modbus Servers

| Device            | Unit Id | Port  |
| ----------------- | :------ | :---: |
| Consuption        | 1       | 5040  |
| Generator         | 1       | 5041  |
| Solar Batteries   | 1       | 5042  |
| Wind Turbine      | 1       | 5043  |
| Power Transformer | 1       | 5044  |
| Batteries         | 1       | 5045  |
| Inverter          | 1       | 5046  |

### Consuption

| Sensors              | Default value | Modbus Register Type | Modbus Address |
| :------------------- | :-----------: | -------------------- | -------------: |
| Voltage L1           |      221      | HR                   |              1 |
| Voltage L2           |      221      | HR                   |              2 |
| Voltage L3           |      221      | HR                   |              3 |
| Frequency L1         |      50       | HR                   |              4 |
| Frequency L2         |      50       | HR                   |              5 |
| Frequency L3         |      50       | HR                   |              6 |
| Consumption L3       |               | HR                   |              7 |
| Consumption L3       |               | HR                   |              8 |
| Consumption L3       |               | HR                   |              9 |
| Consumption          |               | HR                   |             10 |
| Required Consumption |               | HR                   |             11 |
| Daily Consumption    |               | HR                   |             12 |
| Running              |     False     | CO                   |              1 |

### Generator

| Sensors                  | Default value | Modbus Register Type | Modbus Address |
| :----------------------- | :-----------: | -------------------- | -------------: |
| Oil Temperature          |      11       | HR                   |              1 |
| Frequency                |      50       | HR                   |              2 |
| Voltage                  |      221      | HR                   |              3 |
| Fuel Level               |      100      | HR                   |              4 |
| Output Power             |     20000     | HR                   |              5 |
| Current                  |      101      | HR                   |              6 |
| Current Session Duration |               | HR                   |              7 |
| Total Working Duration   |               | HR                   |              8 |
| Running                  |     False     | CO                   |              1 |

### Solar Batteries

| Sensors      | Default value | Modbus Register Type | Modbus Address |
| :----------- | :-----------: | -------------------- | -------------: |
| Illuminance  |               | HR                   |              1 |
| Voltage      |               | HR                   |              2 |
| Temperature  |      10       | HR                   |              3 |
| Output Power |               | HR                   |              4 |
| Current      |               | HR                   |              5 |
| Running      |     False     | CO                   |              1 |

### Wind Turbine

| Sensors        | Default value | Modbus Register Type | Modbus Address |
| :------------- | :-----------: | -------------------- | -------------: |
| Output Power   |               | HR                   |              1 |
| Rotor Speed    |               | HR                   |              2 |
| Wind Speed     |               | HR                   |              3 |
| Wind Direction |               | HR                   |              4 |
| Running        |     False     | CO                   |              1 |

### Power Transformer

| Sensors           | Default value | Modbus Register Type | Modbus Address |
| :---------------- | :-----------: | -------------------- | -------------: |
| Frequency         |      50       | HR                   |              1 |
| Input Voltage L1  |      221      | HR                   |              2 |
| Input Voltage L2  |      221      | HR                   |              3 |
| Input Voltage L3  |      221      | HR                   |              4 |
| Output Voltage L1 |      221      | HR                   |              5 |
| Output Voltage L2 |      221      | HR                   |              6 |
| Output Voltage L3 |      221      | HR                   |              7 |
| Current           |               | HR                   |              8 |
| Power             |               | HR                   |              9 |
| L1 Mode           |       1       | HR                   |             10 |
| L2 Mode           |       1       | HR                   |             11 |
| L3 Mode           |       1       | HR                   |             12 |
| Day Consumption   |               | HR                   |             13 |
| Night Consumption |               | HR                   |             14 |
| Running           |     False     | CO                   |              1 |

### Batteries

| Sensors           | Default value | Modbus Register Type | Modbus Address |
| :---------------- | :-----------: | -------------------- | -------------: |
| Batteries Mode    |       0       | HR                   |              7 |
| Level             |      100      | HR                   |              8 |
| Temperature       |      11       | HR                   |              9 |
| Voltage           |     110.4     | HR                   |             10 |
| Charge Current    |       0       | HR                   |             11 |
| Cycle Count       |       0       | HR                   |             12 |
| Discharge Current |       0       | HR                   |             13 |
| Running           |     False     | CO                   |              1 |
| Running 1         |     False     | CO                   |              2 |
| Running 2         |     False     | CO                   |              3 |
| Running 3         |     False     | CO                   |              4 |
| Running 4         |     False     | CO                   |              5 |
| Running 5         |     False     | CO                   |              6 |

### Inverter

| Sensors           | Default value | Modbus Register Type | Modbus Address |
| :---------------- | :-----------: | -------------------- | -------------: |
| Mode              |       0       | HR                   |              1 |
| Input Voltage L1  |      221      | HR                   |              2 |
| Input Voltage L2  |      221      | HR                   |              3 |
| Input Voltage L3  |      221      | HR                   |              4 |
| Output Voltage L1 |      221      | HR                   |              5 |
| Output Voltage L2 |      221      | HR                   |              6 |
| Output Voltage L3 |      221      | HR                   |              7 |
| Temperature L1    |      11       | HR                   |              8 |
| Temperature L2    |      11       | HR                   |              9 |
| Temperature L3    |      11       | HR                   |             10 |
| Charger Mode      |       0       | HR                   |             11 |
| Current L1        |       0       | HR                   |             12 |
| Current L2        |       0       | HR                   |             13 |
| Current L3        |       0       | HR                   |             14 |
| Current           |       0       | HR                   |             15 |
| Power L1          |       0       | HR                   |             16 |
| Power L2          |       0       | HR                   |             17 |
| Power L3          |       0       | HR                   |             18 |
| Power             |       0       | HR                   |             19 |
| Running           |     False     | CO                   |              1 |

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
    docker run --rm -d --name tb-energy-emulator -p 5040-5046:5040-5046 thingsboard/tb-energy-emulator:latest
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
