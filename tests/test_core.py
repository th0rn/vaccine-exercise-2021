#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for core module. """

import unittest
from datetime import datetime

import core


class TestForKnownGoodValues(unittest.TestCase):
    """Test for known good values. """

    def test_total_order_count(self):
        """Test that total order count is 5000, as given. """
        self.assertEqual(core.inv.data_count, 5000)

    def test_total_administration_count(self):
        """Test that total number of vaccinations administered is 7000, as given. """
        self.assertEqual(core.adm.data_count, 7000)

    def test_for_known_order_count(self):
        """It is known that 61 ampoules arrived on '2021-03-20'. """
        self.assertEqual(core.inv.orders_arrived_on(datetime(2021, 3, 20)), 61)

    def test_vaccines_expired_before_usage(self):
        """It is known that 12'590 vaccines expired by '2021-04-12T11:10:06.473587Z'.

        """
        time = datetime.fromisoformat('2021-04-12+11:10:06.473587')
        self.assertEqual(core.inv.total_doses_expired(time), 12590)


if __name__ == '__main__':
    unittest.main()
