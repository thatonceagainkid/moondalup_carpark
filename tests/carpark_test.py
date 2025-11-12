import unittest
import sys,os
from pathlib import Path
cwd = Path(os.path.dirname(__file__))
parent = str(cwd.parent)

sys.path.append(parent + "/smartpark")

#Change the line below to import your manager class
from mocks import MockCarparkManager

class TestConfigParsing(unittest.TestCase):
   
    def test_fresh_carpark(self):
        # arrange
        # act
        carpark = MockCarparkManager()
        # assert
        self.assertEqual(1000,carpark.available_spaces)

    def test_car_in(self):
        # arrange
        carpark = MockCarparkManager()
        # act
        carpark.incoming_car("LICENSE")
        # assert
        self.assertEqual(999,carpark.available_spaces)

    def test_car_out_unrecognised_plate(self):
        # arrange
        carpark = MockCarparkManager()
        carpark.incoming_car("LICENSE")
        self.assertEqual(999,carpark.available_spaces)
        # act
        carpark.outgoing_car("LICENSE")
        # assert
        self.assertEqual(1000,carpark.available_spaces)
    
    def temperature_changed(self):
        pass

if __name__=="__main__":
    unittest.main()
