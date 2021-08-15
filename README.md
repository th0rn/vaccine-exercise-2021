# vaccination-exercise

## Quickstart

* git pull \<this project>
* cd \<project root>
* chmod +x runner.sh
* ./runner.sh

### Running tests

* python -m unittest tests/test_core.py

## Technology chosen

### Frontend

There of course is room to use a flashy framework for presentation, but it seemed less
important here than in many other cases. After all, in a real world scenario, this would
be serious data with serious implications, where any misunderstandings might be costly.
There were also some issues with the data that needed to be presented according to the
specifications - with either single day or 10 day values, graphing them across time
would inevitably cause issues with weekends (or different amounts of weekends),
plausibly misleading the user to think there is a trend somewhere where there isn't one.

Some potentially important data that was not requested in the spec were a breakdown of
doses available in each healthcare region, and similarly doses about to expire in each
region.

### Backend

Flask seemed very well suited for serving python objects over http and was very easy to
implement. Even with a database, it would probably still have been a good choice, but
here that was not done, as explained below.

### Database

No database was used here, opting for just python objects instead. This presumably comes
at some performance penalty, but with only 5k + 7k datasets and relatively simple
calculations, the performance of the application seems more than sufficient. Presumably,
this type of application would be used by central and perhaps regional health
authorities - implying a small userbase, where the performance implications of needing
to recalculate values is probably not so severe.

## Other thoughts

If indeed the data is only meant to be queried at a precision of one day, then this app
could be greatly optimized by pre-rendering all the html (even with new data
coming in, it would trivial to render new html for the new data with cron, etc.) and
simply serving it off of a CDN. It would make the (no longer an) app much faster for the
user, much lighter to host, and easier to make. I opted not to do this, since I imagine
it's not how the task was intended to be completed, but nonetheless I thought it's worth
mentioning.

## Original task

THL has ordered us to create a vaccination database which contains information about vaccine orders and vaccinations.

We have received files which contains the base data for the application

The Orders are in different files named by the manufacturer of a vaccine.

Injections must be used in 30 days after the arrival of the bottle.

[name].source "Zerpfy"|"Antiqua"|"SolarBuddhica"

The source file has one json item per line.

## Format of an order

```json
{
  "id": "universal identifier of the order",
  "healthCareDistrict": "HYKS|KYS|OYS|TAYS|TYKS",
  "orderNumber": "Rising number of the order",
  "responsiblePerson": "Name of the person who is responsible to track the delivery",
  "injections": "number of injections available in a bottle",
  "arrived": "ISO datetime",
  "vaccine": "Zerpfy|Antiqua|SolarBuddhica"
}
```

## Example order

SolarBuddhica.source:

```json
{
  "id": "2b00bc58-3faf-4d06-bb11-ef47aad8086a",
  "orderNumber": 4194,
  "responsiblePerson": "Arhippa Pihkala",
  "healthCareDistrict": "TYKS",
  "vaccine": "SolarBuddhica",
  "injections": 6,
  "arrived": "2021-04-07T01:10:30.696768Z"
}
```

## Vaccination structure

vaccinations.source is a json array which has information of all the vaccinations currently made

The datastructure is

```json
{
  "vaccination-id": "universal identifier of the vaccination",
  "gender": "male|female|nonbinary",
  "sourceBottle": "universal identifier of the bottle",
  "injected": "Datetime"
}
```

## Example vaccination

```json
{"vaccination-id":"e28a0fb5-3956-4ba6-827f-4dcae64e4cda",
"sourceBottle":"2b00bc58-3faf-4d06-bb11-ef47aad8086a",
"gender":"nonbinary",
"vaccinationDate":"2021-04-08T11:00:20.740994Z"}
```

# The exercise

Make a web application for presenting some interesting data about the vaccinations.

Return the exercise as a link to your GitHub repository.

## Technology choices

Feel free to use whatever you think is best for this kind of stuff.

React/Vue.js/Angular or something else for the web frontend. All is fine.

Swift/Kotlin/React Native/Flutter etc. or a mobile technology of your choice.

Node.js/Clojure/Go/Rust/Kotlin or something else for the backend.

Some kind of database could be useful for aggregating the data. MySQL/Postgresql/Oracle/FreemanDB or maybe noSQL?

## List of interesting things

For given day like 2021-04-12T11:10:06

* How many orders and vaccines have arrived total?
* How many of the vaccinations have been used?
* How many orders/vaccines per producer?
* How many bottles have expired on the given day (remember a bottle expires 30 days after arrival)
* How many vaccines expired before the usage -> remember to decrease used injections from the expired bottle
* How many vaccines are left to use?
* How many vaccines are going to expire in the next 10 days?

Perhaps there is some other data which could tell us some interesting things?

## Some numbers to help you

* Total number of orders 5000
* Vaccinations done 7000
* "2021-03-20" arrived 61 orders.
* When counted from "2021-04-12T11:10:06.473587Z" 12590 vaccines expired before usage (injections in the expiring bottles 17423
  and injections done from the expired bottles 4833)

## Some tips

* You don't need to do all these for a good result.
* You can make graphs from the data but textual representation suffice also.
* Think about the tests for your application.
* You can test the frontend also
* Add README.md which have instructions how to build/run your software and how to run the tests.
