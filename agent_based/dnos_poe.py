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

from collections.abc import Sequence
from dataclasses import dataclass

from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    exists,
    Metric,
    OIDEnd,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringByteTable,
)


@dataclass
class PsePortTable:
    index: str
    power_limit: float
    power: float
    current: float
    volt: int
    temp: int
    status: int


Section = Sequence[PsePortTable]


def parse_dnos_poe(
    string_table: StringByteTable,
) -> Sequence[PsePortTable]:
    return [
        PsePortTable(
            index=str(line[0].split('.')[1]),
            power_limit=int(line[1]) / 1000,
            power=int(line[2]) / 1000,
            current=int(line[3]) / 1000,
            volt=int(line[4]),
            temp=int(line[5]),
            status=int(line[6]),
        )
        for line in string_table
    ]


snmp_section_dnos_poe = SimpleSNMPSection(
    name = 'dnos_poe',
    parse_function=parse_dnos_poe,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.15.1.1.1',
        oids = [
            OIDEnd(),
            '1',  # DNOS-POWER-ETHERNET-MIB::agentPethPowerLimit
            '2',  # DNOS-POWER-ETHERNET-MIB::agentPethOutputPower
            '3',  # DNOS-POWER-ETHERNET-MIB::agentPethOutputCurrent
            '4',  # DNOS-POWER-ETHERNET-MIB::agentPethOutputVolt
            '5',  # DNOS-POWER-ETHERNET-MIB::agentPethTemperature
            '9',  # DNOS-POWER-ETHERNET-MIB::agentPethFaultStatus
        ],
    ),
    detect=exists('.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.15.1.1.1.*'),
)


def discover_dnos_poe(
    section_dnos_poe: Section | None,
    section_if64: Section | None,
) -> DiscoveryResult:
    if section_dnos_poe is None:
        return
    for port in section_dnos_poe:
        if port.power > 0:
            item = next((i.attributes.descr for i in section_if64 if i.attributes.index == port.index), port.index)
            yield Service(item=item)


def check_dnos_poe(
    item: str,
    section_dnos_poe: Section | None,
    section_if64: Section | None,
) -> CheckResult:
    if section_dnos_poe is None:
        return
    item = next((i.attributes.index for i in section_if64 if i.attributes.descr == item), item)
    for port in section_dnos_poe:
        if port.index != item:
            continue

        alias = next((i.attributes.alias for i in section_if64 if i.attributes.index == item), None)
        if alias:
            yield Result(state=State.OK, summary=f"[{alias}]")

        yield from check_levels(
            value=port.power,
            metric_name='pse_power',
            render_func=lambda x: f"{x} Watts",
            boundaries=(0, port.power_limit)
        )
        yield Metric(
            name='pse_power_limit',
            value=port.power_limit
        )

        yield from check_levels(
            value=port.current,
            metric_name='pse_current',
            render_func=lambda x: f"{x * 1000} Milliamps",
        )

        yield from check_levels(
            value=port.volt,
            metric_name='pse_volt',
            render_func=lambda x: f"{x} Volt",
            boundaries=(44, 57)
        )


check_plugin_dnos_poe = CheckPlugin(
    name='dnos_poe',
    sections=['dnos_poe', 'if64'],
    service_name="PoE %s",
    discovery_function=discover_dnos_poe,
    check_function=check_dnos_poe,
)
