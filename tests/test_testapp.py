import unittest
import requests

class TestQuestsEndpoint(unittest.TestCase):
    def test_get_quests_valid_coordinates(self): # for Stanford campus
        # Test with valid latitude and longitude
        lat = 37.426
        lon = -122.165
        
        response = requests.get(f"http://localhost:8000/quests?lat={lat}&lon={lon}")
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check response is JSON
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        
        # Check response structure
        data = response.json()
        self.assertIsInstance(data, list)
        
        # If there are quests, verify their structure
        if len(data) > 0:
            for quest in data:
                self.assertIn('id', quest)
                self.assertIn('title', quest)
                self.assertIn('description', quest)
                self.assertIn('location', quest)
                self.assertIsInstance(quest['location'], dict)
                self.assertIn('latitude', quest['location'])
                self.assertIn('longitude', quest['location'])

    def test_get_quests_invalid_coordinates(self):
        # Test with invalid coordinates
        invalid_coords = [
            ('abc', -122.165),
            (37.426, 'xyz'),
            (None, -122.165),
            (37.426, None)
        ]
        
        for lat, lon in invalid_coords:
            response = requests.get(f"http://localhost:8000/quests?lat={lat}&lon={lon}")
            self.assertEqual(response.status_code, 400)

    def test_get_quests_out_of_range_coordinates(self):
        # Test with out of range coordinates
        out_of_range = [
            (91, -122.165),  # latitude > 90
            (-91, -122.165), # latitude < -90
            (37.426, 181),   # longitude > 180
            (37.426, -181)   # longitude < -180
        ]
        
        for lat, lon in out_of_range:
            response = requests.get(f"http://localhost:8000/quests?lat={lat}&lon={lon}")
            self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()