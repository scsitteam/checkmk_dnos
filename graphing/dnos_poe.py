#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Copyright (C) 2024  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from cmk.graphing.v1 import graphs, metrics, perfometers

metric_pse_power = metrics.Metric(
    name='pse_power',
    title=metrics.Title('Power Usage'),
    unit=metrics.Unit(notation=metrics.DecimalNotation(symbol='W'), precision=metrics.StrictPrecision(digits=2)),
    color=metrics.Color.BLUE,
)

metric_pse_power_limit = metrics.Metric(
    name='pse_power_limit',
    title=metrics.Title('Power Limit'),
    unit=metrics.Unit(notation=metrics.DecimalNotation(symbol='W'), precision=metrics.StrictPrecision(digits=2)),
    color=metrics.Color.DARK_BLUE,
)

metric_pse_current = metrics.Metric(
    name='pse_current',
    title=metrics.Title('Current Draw'),
    unit=metrics.Unit(notation=metrics.DecimalNotation(symbol='A'), precision=metrics.StrictPrecision(digits=2)),
    color=metrics.Color.BLUE,
)

metric_pse_volt = metrics.Metric(
    name='pse_volt',
    title=metrics.Title('Voltage'),
    unit=metrics.Unit(notation=metrics.DecimalNotation(symbol='V'), precision=metrics.StrictPrecision(digits=2)),
    color=metrics.Color.BLUE,
)

graph_metric_dnos_if64_poe = graphs.Graph(
    name='dnos_if64_poe',
    title=graphs.Title('PoE PSE'),
    minimal_range=graphs.MinimalRange(0, metrics.MaximumOf('pse_power_limit', metrics.Color.BLACK)),
    compound_lines=['pse_power'],
    simple_lines=['pse_power_limit']
)

perfometer_pse_power = perfometers.Perfometer(
    name='pse_power',
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed('pse_power_limit')),
    segments=['pse_power'],
)
