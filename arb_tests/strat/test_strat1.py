from arb import es

import unittest

from arb_tests import remove_testing_data


class TestStra1(unittest.TestCase):

    @classmethod
    def setUp(cls):
        remove_testing_data(es)

    @classmethod
    def tearDown(cls):
        remove_testing_data(es)



if __name__ == '__main__':
    unittest.main()

    # pass


