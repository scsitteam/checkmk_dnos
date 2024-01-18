#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# dnos_cpu - Dell Networking OS Temperature Check for Checkmk
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

# Example excerpt from SNMP data:
# Relevant SNMP OIDs:
# DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesUnitIndex.1.0 = Gauge32: 1
# DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorIndex.1.0 = Gauge32: 0
# DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.1.0 = INTEGER: fixed(1)
# DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.1.0 = INTEGER: normal(1)
# DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.1.0 = INTEGER: 34


from typing import Optional, List

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    get_value_store,
    OIDEnd,
    register,
    Service,
    SNMPTree,
    startswith,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import DiscoveryResult, StringTable
from cmk.base.plugins.agent_based.utils.temperature import check_temperature, TempParamType

DevStatusMap = {
    '1': (State.OK, 'normal'),
    '2': (State.WARN, 'warning'),
    '3': (State.CRIT, 'critial'),
    '4': (State.UNKNOWN, 'shutdown'),
    '5': (State.UNKNOWN, 'notpresent'),
    '6': (State.UNKNOWN, 'notoperational'),
}


def parse_dnos_temp(string_table: StringTable) -> Optional[dict]:
    if not string_table:
        return None

    return {f"Unit {s[0]} Sensor {s[1]}": (int(s[3]), DevStatusMap.get(s[2], (State.UNKNOWN, 'unknown'))) for s in string_table}


register.snmp_section(
    name = "dnos_temp",
    parse_function=parse_dnos_temp,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.8.1',
        oids = [
            '1',  # DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesUnitIndex
            '2',  # DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorIndex
            '3',  # DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState
            '5',  # DNOS-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature
        ],
    ),
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.674.10895.")
)

def parse_dnos10_temp(string_table: List[StringTable]) -> Optional[dict]:
    if not string_table:
        return None
    
    temp = {f"Chassis {s[0]}": int(s[1]) for s in string_table[0]}
    temp.update({f"Card {s[0]}": int(s[1]) for s in string_table[1]})

    return temp

register.snmp_section(
    name = "dnos10_temp",
    parse_function=parse_dnos10_temp,
    fetch = [
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.1.3.1',
            oids = [
                OIDEnd(),
                '11',  # DELLEMC-OS10-CHASSIS-MIB::os10ChassisTemp
            ],
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1',
            oids = [
                OIDEnd(),
                '5',  # DELLEMC-OS10-CHASSIS-MIB::os10CardTemp
            ],
        ),
    ],
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.674.11000.5000.100")
)


def discovery_dnos_temp(section: dict) -> DiscoveryResult:
    for sensor in section.keys():
        yield Service(item=sensor)


def check_dnos_temp(item: str, params: TempParamType, section: dict):
    if item not in section:
        return
    yield from check_temperature(
        reading=section[item][0],
        params=params,
        unique_name=item,
        value_store=get_value_store(),
        dev_status=section[item][1][0],
        dev_status_name=section[item][1][1],
    )


register.check_plugin(
    name="dnos_temp",
    service_name="Temperature %s",
    discovery_function=discovery_dnos_temp,
    check_function=check_dnos_temp,
    check_default_parameters={"levels": (80.0, 90.0), "device_levels_handling": "worst"},
    check_ruleset_name="temperature",
)


def check_dnos10_temp(item: str, params: TempParamType, section: dict):
    if item not in section:
        return
    yield from check_temperature(
        reading=section[item],
        params=params,
        unique_name=item,
        value_store=get_value_store(),
    )


register.check_plugin(
    name="dnos10_temp",
    service_name="Temperature %s",
    discovery_function=discovery_dnos_temp,
    check_function=check_dnos10_temp,
    check_default_parameters={"levels": (80.0, 90.0), "device_levels_handling": "worst"},
    check_ruleset_name="temperature",
)