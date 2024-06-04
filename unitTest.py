import unittest
from unittest.mock import patch, mock_open
from main import get_list_of_countries_object, get_countrycode, get_citydata, RawDataCountryWrapper, status, Trip

class TestMain(unittest.TestCase):
    def setUp(self):
        self.country_object = RawDataCountryWrapper(name="Austria", alpha_2="AT")
        self.list_of_countries_object = [self.country_object]
        self.trip = Trip("Vienna", "Austria")

    def test_get_list_of_countries_object(self):
        with patch("builtins.open", mock_open(read_data="name,alpha_2\nAustria,AT")):
            result = get_list_of_countries_object()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "Austria")
            self.assertEqual(result[0].alpha_2, "AT")

    def test_get_countrycode(self):
        countrycode, status_code = get_countrycode("Austria", self.list_of_countries_object)
        self.assertEqual(countrycode, "AT")
        self.assertEqual(status_code, status.NO_ERROR)

        countrycode, status_code = get_countrycode("Nonexistent", self.list_of_countries_object)
        self.assertIsNone(countrycode)
        self.assertEqual(status_code, status.COUNTRYCODE_NOT_FOUND)

    @patch('requests.get')
    def test_get_citydata(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = "content"
        data, status_code = get_citydata("Vienna", "AT")
        self.assertEqual(data, "content")
        self.assertEqual(status_code, status.NO_ERROR)

    def test_trip(self):
        self.assertEqual(self.trip.city, "Vienna")
        self.assertEqual(self.trip.country, "Austria")
        self.assertIsNone(self.trip.countrycode)
        self.trip.add_countrycode("AT")
        self.assertEqual(self.trip.countrycode, "AT")

if __name__ == '__main__':
    unittest.main()