import unittest
from desoper import works_colombia


class Test_hello(unittest.TestCase):
    def test__working(self):
        self.assertEqual(works_colombia.data())


if __name__ == '__main__':
    unittest.main()
