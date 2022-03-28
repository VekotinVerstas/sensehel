from rest_framework.test import APITestCase


class SenseHelAPITestCase(APITestCase):
    def assert_dict_contains(self, superset, subset, path=''):
        for key, expected in subset.items():
            full_path = path + key
            received = superset.get(key, None)
            if isinstance(expected, dict) and isinstance(received, dict):
                self.assert_dict_contains(superset[key], expected, full_path + '.')
            else:
                assert received == expected, 'Value mismatch for key {}: {} != {}'.format(
                    full_path, expected, received
                )
