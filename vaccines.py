#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flask app to render our templates with data. """

import datetime

from flask import Flask, redirect, url_for, render_template, session
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms import validators, SubmitField
from wtforms.ext.dateutil.fields import DateTimeField
from flask_datepicker import datepicker

#  import main
import core

app = Flask(__name__)

app.config['SECRET_KEY'] = 'test'


class InfoForm(FlaskForm):
    time = DateTimeField('Time', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')


#  datepicker(app)


@app.route("/", methods=['GET', 'POST'])
def index():
    """Show starting page, with only the search/lookup form. """
    form = InfoForm()
    if form.validate_on_submit():
        session['time'] = form.time.data
        t = form.time.data
        return redirect(
            '/%s/%s/%s/%s/%s/%s/%s' % (t.year, t.month, t.day,
                                       t.hour, t.minute, t.second, t.microsecond)
        )
    return render_template('index.html', form=form)


@app.route("/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:sec>/<int:microsec>",
           methods=['GET', 'POST'])
def show_time(year, month, day, hour, minute, sec, microsec):
    """Show vaccination data for a single day, with a form to make another search. """
    form = InfoForm()
    if form.validate_on_submit():
        session['time'] = form.time.data
        t = form.time.data
        return redirect(
            '/%s/%s/%s/%s/%s/%s/%s' % (
                t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond
            )
        )

    time = datetime.datetime(year, month, day, hour, minute, sec, microsec)
    easy_date = '%s.%s.%s' % (time.day, time.month, time.year)
    t = time + datetime.timedelta(days=1)

    #  administrations = core.load_administrations()

    info = {
        'orders_arrived_on': core.inv.orders_arrived_on(time),
        'vaccines_arrived_on': core.inv.vaccines_arrived_on(time),
        'administrations': core.adm.administrations,
        'admins_on': core.adm.vaccines_administered_on(time),
        'by_man': core.inv.orders_arrived_on_by_manufacturer(time),
        'expired_on_day': core.inv.expired_on_day(time),
        'doses_expired_on_day': core.inv.doses_expired_on_day(time),
        'doses_left': core.inv.doses_left(time),
        'doses_expiring': core.inv.doses_expiring(time),
        'total_doses_expired': core.inv.total_doses_expired(time),
        'total_ampoule_count': core.inv.data_count,
        'total_admin_count': core.adm.data_count,
        'doses_expiring_by_district': core.inv.doses_expiring_by_district(time),
        'easy_date': '%s.%s.%s' % (time.day, time.month, time.year),
        'tomorrow': url_for(
            'show_time',
            year=t.year,
            month=t.month,
            day=t.day,
            hour=t.hour,
            minute=t.minute,
            sec=t.second,
            microsec=t.microsecond,
        ),
    }

    t = time + datetime.timedelta(days=-1)
    info['yesterday'] = url_for('show_time',
                                year=t.year, month=t.month, day=t.day, hour=t.hour,
                                minute=t.minute, sec=t.second, microsec=t.microsecond,
                                )

    return render_template('info.html', form=form, info=info)
