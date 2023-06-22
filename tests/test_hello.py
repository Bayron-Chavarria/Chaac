import unittest
from desoper import probar123


class Test_hello(unittest.TestCase):
    def test__working(self):
        self.assertEqual(probar123.hello(),'Hello, World!', True)


if __name__ == '__main__':
    unittest.main()
