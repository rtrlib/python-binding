import unittest
from .test_pfx_table import PfxTableTest


def suite():
    loader = unittest.TestLoader()
    s = loader.loadTestsFromTestCase(PfxTableTest)
    return s


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
