import unittest
from desoper import works_colombia


class Test_hello(unittest.TestCase):
    def test__working(self):
        self.assertEqual(works_colombia.all_works(("ttps://api.openalex.org/publishers?filter=country_codes:CO"))


if __name__ == '__main__':
    unittest.main()
