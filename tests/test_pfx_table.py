# -*- coding: utf8 -*-
"""
tests.pfx_table_test
------------------
"""

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from rtrlib import PfxTable

# flag constants for asserting the validation result
VALID = 1 << 0
INVALID = 1 << 1
UNKNOWN = 1 << 2
LENGTH_INVALID = 1 << 3
AS_INVALID = 1 << 4


class PfxTableTest(unittest.TestCase):

    DEFAULT_RECORDS = [
        (10010, '110.1.0.0', 20, 24),
        (10020, '120.1.0.0', 20, 32),
        (10030, '130::', 64, 64)
    ]

    def setUp(self):
        """
        Create a new prefix table instance for any test method
        """
        self.pfx_table = PfxTable()

    def tearDown(self):
        """
        Close and remove the current prefix table instance
        """
        self.pfx_table.close()

    def test_v4(self):
        """
        - Test IPV4 record in prefix table
        """
        self._fill_table(self.DEFAULT_RECORDS)

        self._assert(10010, '110.1.0.0', 20, VALID)
        self._assert(10010, '110.1.0.0', 24, VALID)
        self._assert(10010, '110.1.8.0', 23, VALID)
        self._assert(10010, '110.1.0.0', 18, UNKNOWN)
        self._assert(10010, '110.1.0.0', 30, INVALID)
        self._assert(10011, '110.1.0.0', 20, INVALID)

        self._assert_r(10010, '110.1.0.0', 20, VALID)
        self._assert_r(10010, '110.1.0.0', 24, VALID)
        self._assert_r(10010, '110.1.8.0', 23, VALID)
        self._assert_r(10010, '110.1.0.0', 18, UNKNOWN)
        self._assert_r(10010, '110.1.0.0', 30, INVALID | LENGTH_INVALID)
        self._assert_r(10011, '110.1.0.0', 20, INVALID | AS_INVALID)

    def test_v6(self):
        """
        - Test IPV6 record in prefix table
        """
        self._fill_table(self.DEFAULT_RECORDS)

        self._assert(10030, '130::', 64, VALID)
        self._assert(10030, '130::', 66, INVALID)
        self._assert(10030, '130::', 62, UNKNOWN)

        self._assert_r(10030, '130::', 64, VALID)
        self._assert_r(10030, '130::', 66, INVALID | LENGTH_INVALID)
        self._assert_r(10030, '130::', 62, UNKNOWN)

    def test_duplicate(self):
        """
        - Add duplicate record into prefix table (same prefix range, other AS number)
        """
        self._fill_table(self.DEFAULT_RECORDS)
        self._fill_table([(10020, '110.1.0.0', 22, 24)])

        self._assert(10010, '110.1.0.0', 20, VALID)
        self._assert(10010, '110.1.0.0', 24, VALID)
        self._assert(10020, '110.1.0.0', 22, VALID)
        self._assert(10020, '110.1.0.0', 24, VALID)

    def test_remove(self):
        """
        - Remove record from prefix table
        """
        self._fill_table(self.DEFAULT_RECORDS)
        self.pfx_table.remove_record(10010, '110.1.0.0', 20, 24)

        self._assert(10010, '110.1.0.0', 20, UNKNOWN)

    def _fill_table(self, records):
        """
        Adds a list of record tuples to the prefix talbe.
        Each tuple must contain these four elements:
            * as number (int)
            * ip address (str)
            * min range length (int)
            * max range length (int)
        :param records: List of records to be added to the prefix table
        :type records: list
        """
        for record in records:
            self.pfx_table.add_record(*record)

    def _assert(self, asn, ip, mask, exp_flags):
        """
        Let the prefix table validate the given IP prefix
        and check the returned validation result
        """
        r = self.pfx_table.validate(asn, ip, mask)
        record = "AS{0}:{1}/{2}".format(asn, ip, mask)
        self._assert_flag(r.is_valid, bool(exp_flags & VALID), record, "is invalid", "is valid")
        self._assert_flag(r.is_invalid, bool(exp_flags & INVALID), record, "is valid", "is invalid")
        self._assert_flag(r.not_found, bool(exp_flags & UNKNOWN), record, "was found", "not found")

    def _assert_r(self, asn, ip, mask, exp_flags):
        """
        Let the prefix table validate the given IP prefix
        and check the returned validation result
        """
        r = self.pfx_table.validate_r(asn, ip, mask)
        record = "AS{0}:{1}/{2}".format(asn, ip, mask)
        self._assert_flag(r.is_valid, bool(exp_flags & VALID), record, "is invalid", "is valid")
        self._assert_flag(r.is_invalid, bool(exp_flags & INVALID), record, "is valid", "is invalid")
        self._assert_flag(r.not_found, bool(exp_flags & UNKNOWN), record, "was found", "not found")
        self._assert_flag(r.length_invalid, bool(exp_flags & LENGTH_INVALID), record, "has invalid length", "has valid length")
        self._assert_flag(r.as_invalid, bool(exp_flags & AS_INVALID), record, "has invalid AS", "has valid AS")

    def _assert_flag(self, act_flag, exp_val, record, msg_exp_true, msg_exp_false):
        self.assertEqual(act_flag, exp_val, "{0} {1}".format(record, msg_exp_true if exp_val else msg_exp_false))


if __name__ == '__main__':
    unittest.main()
