#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The backend for our vaccine data app. """

import argparse
import json
from types import SimpleNamespace
import datetime
from collections import namedtuple

MANUFACTURERS = ['Antiqua', 'SolarBuddhica', 'Zerpfy', ]

ORDERS_DATA = [
    'resources/Antiqua.source',
    'resources/SolarBuddhica.source',
    'resources/Zerpfy.source',
]

ADMINISTRATION_DATA = 'resources/vaccinations.source'


class Order():
    """ One bottle of vaccine, containing multiple doses. """
    def __init__(self, uuid, orderNumber, responsiblePerson, healthCareDistrict,
                 vaccine, injections, arrived, ):
        self.uuid = uuid
        self.order_number = orderNumber
        self.responsible_person = responsiblePerson
        self.healthcare_district = healthCareDistrict
        self.vaccine = vaccine  # The name of the manufacturer, currently one of three.
        self.injections = injections  # Number of doses of the vaccine in the bottle.
        # The third-party package dateutil could parse ISO 8601 format dates, but we opt
        # to do this simple trick instead to keep moving.
        iso_time = arrived.replace('T', '+').strip('Z')
        self.arrived = datetime.datetime.fromisoformat(iso_time)
        self.doses = []

    def dose(self, dose):
        """Record a dosing from this bottle. """
        self.doses.append(dose)

    def expired(self, time):
        """Returns whether the bottle has expired by <time>. """
        return self.arrived + datetime.timedelta(days=30) < time

    def expired_on_day(self, time):
        """Returns whether the bottle has expired or will expire on _day_ of <time>.

        Note:
         Here, we're looking at bottles and do not care about doses or lack thereof. """
        assert isinstance(time, datetime.date)
        return self.arrived.date() + datetime.timedelta(days=30) == time

    def doses_expired(self, time):
        """Return number of doses in this bottle that have expired on _this_ *day*. """
        if not self.expired_on_day(time):
            return 0
        #  if self.expired_on_day(time) and not self.expired_on_day(time):
            #  return 0
        return self.injections - len(self.doses)

    def doses_expiring(self, time):
        """Return number of doses expiring in the next 10 days. """
        if self.expired(time):
            return 0
        # Vaccines were declared to expire 30 days from being received, so 20 days after
        # begin received they are "about to expire in 10 days", the cutoff given for the
        # warning.
        if self.arrived + datetime.timedelta(days=20) > time:
            return 0
        return self.injections - len(self.doses)

    def doses_expiring_by_district(self, time):
        """Return number of doses expiring in the next 10 days, but by district. """
        if self.expired(time):
            return (0, None)
        # Vaccines were declared to expire 30 days from being received, so 20 days after
        # begin received they are "about to expire in 10 days", the cutoff given for the
        # warning.
        if self.arrived + datetime.timedelta(days=20) > time:
            return (0, None)
        return (self.injections - len(self.doses), self.healthcare_district)

    def doses_left(self, time):
        """Return the number of (non-expired) doses left from this bottle.

        Notable here is that since this application seems to be intended to be able to
        provide (then) up-to-date information for times in the past, we also have to
        account for vaccinations that have not yet arrived. In theory, doses in ampoules
        not yet received are still "left" and are also "not about to expire", but it
        seems like they should be discounted, although that may or may not be the case
        depending on how this information is meant to be used.

        """
        if self.expired(time):
            return 0
        # Note: It was not clear from the specifications when cutoffs should be done by
        # the day and when by the time, so there may be some ambiguity or inconsistency
        # here.
        if self.arrived.date() > time.date():
            return 0
        return self.injections - len(self.doses)


class Inventory():
    def __init__(self):
        """Load order data from resources. """

        self.orders = []

        for file in ORDERS_DATA:
            with open(file) as fd:
                for datum in fd:
                    x = json.loads(datum, object_hook=lambda d: SimpleNamespace(**d))
                    order = Order(x.id, x.orderNumber, x.responsiblePerson,
                                  x.healthCareDistrict, x.vaccine, x.injections, x.arrived)
                    self.orders.append(order)

        self.data_count = len(self.orders)
        print(self.data_count, 'orders loaded.')

    def orders_arrived_on(self, time):
        """ For given time like 2021-04-12T11:10:06, how many orders have arrived or will
        arrive on the date that this time is on. """

        orders_arrived = 0

        for order in self.orders:
            if order.arrived.date() == time.date():
                orders_arrived += 1

        return orders_arrived

    def orders_arrived_by(self, time):
        """ For given time like 2021-04-12T11:10:06, how many orders have arrived total. """

        orders_arrived = 0

        for order in self.orders:
            if order.arrived < time:
                orders_arrived += 1

        return orders_arrived

    def orders_arrived_on_by_manufacturer(self, time):
        """ For given time like 2021-04-12T11:10:06, how many orders have arrived or
        will arrive on the date that this time is on. """

        orders_by_manufacturer = {}

        for manufacturer in MANUFACTURERS:
            orders_arrived = 0
            doses_arrived = 0

            for order in self.orders:
                if order.arrived.date() == time.date() and order.vaccine == manufacturer:
                    orders_arrived += 1
                    doses_arrived += order.injections

            #  orders_by_manufacturer[manufacturer] = (orders_arrived, doses_arrived)
            #  orders_by_manufacturer[manufacturer] = '%s/%s' % (orders_arrived, doses_arrived)
            orders_by_manufacturer[manufacturer] = {}
            orders_by_manufacturer[manufacturer]['ampoules'] = orders_arrived
            orders_by_manufacturer[manufacturer]['doses'] = doses_arrived

        return orders_by_manufacturer

    def vaccines_arrived_on(self, time):
        """ For given time like 2021-04-12T11:10:06, how many *vaccines* have arrived or
        will arrive on the date that this time is on. """

        vaccines_arrived = 0

        for order in self.orders:
            if order.arrived.date() == time.date():
                vaccines_arrived += order.injections

        return vaccines_arrived

    def expired_on_day(self, time):
        """Return the number of ampoules that expire(d) on this day. """

        expirations = 0
        for ampoule in self.orders:
            if ampoule.expired_on_day(time.date()):
                expirations += 1
        return expirations

    def doses_expired_on_day(self, time):
        """Return total amount of _doses_ that expire(d) on the _day_ of this time. """
        expirations = 0
        for ampoule in self.orders:
            if ampoule.expired_on_day(time.date()):
                expirations += ampoule.doses_expired(time.date())
        return expirations

    def total_doses_expired(self, time):
        """Return the total number of doses expired up to this moment in <time>. """
        expirations = 0
        for ampoule in self.orders:
            if ampoule.expired(time):
                # Doses of an ampoule are the ones that have been given out from it.
                expirations += ampoule.injections - len(ampoule.doses)

        return expirations

    def doses_left(self, time):
        """Return the amount of doses that are still available at the end of the day.

        """

        remaining = 0
        for ampoule in self.orders:
            remaining += ampoule.doses_left(time)

        return remaining

    def doses_expiring(self, time):
        """Return the amount of doses in all ampoules expiring in the next 10 days.

        TODO: Rounded, or by time? """
        expiring = 0
        for ampoule in self.orders:
            expiring += ampoule.doses_expiring(time)

        return expiring

    def doses_expiring_by_district(self, time):
        """Return the amount of doses in all ampoules expiring in the next 10 days, but
        by district.

        """
        expiring_by_district = {}
        for ampoule in self.orders:
            (doses_expiring, district) = ampoule.doses_expiring_by_district(time)
            if doses_expiring > 0:
                if district in expiring_by_district:
                    expiring_by_district[district] += doses_expiring
                else:
                    expiring_by_district[district] = doses_expiring

        print(expiring_by_district)
        return expiring_by_district


inv = Inventory()


class Dose():
    def __init__(self, vaccination_id, source_bottle, gender, vaccination_date):
        self.vaccination_id = vaccination_id
        self.source_bottle = source_bottle
        self.gender = gender
        iso_time = vaccination_date.replace('T', '+').strip('Z')
        self.vaccination_date = datetime.datetime.fromisoformat(iso_time)


class Administration():
    def __init__(self, inventory):
        """Load vaccine administration data from resources. """

        self.administrations = []

        with open(ADMINISTRATION_DATA) as f:
            for administration in f:
                x = json.loads(
                    administration,
                    object_hook=lambda d: namedtuple('X', d.keys(), rename=True)(*d.values())
                )
                dose = Dose(x._0, x.gender, x.sourceBottle, x.vaccinationDate)
                self.administrations.append(dose)
                for ampoule in inventory.orders:
                    if ampoule.uuid == x.sourceBottle:
                        ampoule.dose(dose)

        self.data_count = len(self.administrations)
        print(self.data_count, 'administrations loaded.')

    def vaccines_administered_on(self, time):
        """ For given time like 2021-04-12T11:10:06, how many *doses* have or will be
        administered on the date that this time is on. """

        administrations_given = 0

        for admin in self.administrations:
            if admin.vaccination_date.date() == time.date():
                administrations_given += 1

        return administrations_given


# We pass the inventory here to be able to discount administered doses.
adm = Administration(inv)
