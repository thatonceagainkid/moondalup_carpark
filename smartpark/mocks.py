from interfaces import CarparkSensorListener
from interfaces import CarparkDataProvider
from config_parser import parse_config
import time
import os

'''
    TODO: 
    - make your own module, or rename this one. Yours won't be a mock-up, so "mocks" is a bad name here.
    - Read your configuration from a file. 
    - Write entries to a log file when something happens.
    - The "display" should update instantly when something happens
    - Make a "Car" class to contain information about cars:
        * License plate number. You can use this as an identifier
        * Entry time
        * Exit time
    - The manager class should record all activity. This includes:
        * Cars arriving
        * Cars departing
        * Temperature measurements.
    - The manager class should provide informtaion to potential customers:
        * The current time (optional)
        * The number of bays available
        * The current temperature
    
'''
class MockCarparkManager(CarparkSensorListener,CarparkDataProvider):
    #constant, for where to get the configuration data
    CONFIG_FILE = os.path.join(os.path.dirname(__file__),\
        "\..\\samples_and_snippets\\carpark_config.txt")

    def __init__(self):
  #      configuration = parse_config(MockCarparkManager.CONFIG_FILE)
        pass

    @property
    def available_spaces(self):
        return 1000

    @property
    def temperature(self):
        return 1000

    @property
    def current_time(self):
        return time.localtime()

    def incoming_car(self,license_plate):
        print('Car in! ' + license_plate)

    def outgoing_car(self,license_plate):
        print('Car out! ' + license_plate)

    def temperature_reading(self,reading):
        print(f'temperature is {reading}')

class Car:
    def __init__(self,plate=None):
        self.LicensePlate = plate