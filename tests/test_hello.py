import unittest
from desoper import prueba


class Test_hello(unittest.TestCase):
    def test__working(self):
        self.assertEqual(prueba.hello(),'Hello, World!', True)


if __name__ == '__main__':
    unittest.main()
