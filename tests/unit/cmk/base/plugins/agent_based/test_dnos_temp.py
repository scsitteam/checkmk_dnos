#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Dell OS6 Check for Checkmk
#
# Copyright (C) 2023  Marius Rieder <marius.rieder@scs.ch>
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
#

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import dnos_temp


def get_value_store():
    return {}


@pytest.mark.parametrize('string_table, result', [
    ([], None),
    ([['1', '0', '1', '34']], {"1:0": (34, (State.OK, 'normal'))}),
    ([['1', '0', '1', '34'], ['2', '1', '2', '35']], {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))}),
])
def test_parse_dnos_temp(string_table, result):
    assert dnos_temp.parse_dnos_temp(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    ({"1:0": (34, 1)}, [Service(item='1:0')]),
])
def test_discovery_phion_service(section, result):
    assert list(dnos_temp.discovery_dnos_temp(section)) == result


@pytest.mark.parametrize('item, params, section, result', [
    (
        'FOO', {}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        []
    ),
    (
        '1:0', {}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        [
            Metric('temp', 34.0),
            Result(state=State.OK, summary='Temperature: 34 °C'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (no levels found)'),
        ]
    ),
    (
        '2:1', {}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        [
            Metric('temp', 35.0),
            Result(state=State.OK, summary='Temperature: 35 °C'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (no levels found)'),
        ]
    ),
    (
        '2:1', {"device_levels_handling": "worst"}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        [
            Metric('temp', 35.0),
            Result(state=State.OK, summary='Temperature: 35 °C'),
            Result(state=State.WARN, summary='State on device: warning'),
            Result(state=State.OK, notice='Configuration: show most critical state'),
        ]
    ),
    (
        '1:0', {'levels': (30, 40), 'levels_lower': (10, 5)}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        [
            Metric('temp', 34.0, levels=(30.0, 40.0,)),
            Result(state=State.WARN, summary='Temperature: 34 °C (warn/crit at 30 °C/40 °C)'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (used user levels)'),
        ]
    ),
    (
        '1:0', {'levels': (30, 40), 'levels_lower': (10, 5), "device_levels_handling": "worst"}, {"1:0": (34, (State.OK, 'normal')), "2:1": (35, (State.WARN, 'warning'))},
        [
            Metric('temp', 34.0, levels=(30.0, 40.0,)),
            Result(state=State.WARN, summary='Temperature: 34 °C (warn/crit at 30 °C/40 °C)'),
            Result(state=State.OK, notice='Configuration: show most critical state'),
        ]
    ),
])
def test_check_dnos_temp(monkeypatch, item, params, section, result):
    monkeypatch.setattr(dnos_temp, 'get_value_store', get_value_store)
    assert list(dnos_temp.check_dnos_temp(item, params, section)) == result
