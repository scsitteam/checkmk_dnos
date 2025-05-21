#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# dnos_labels - Dell Networking OS Host labels
#
# Copyright (C) 2023-2024  Marius Rieder <marius.rieder@scs.ch>
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
# DNOS-SWITCHING-MIB::agentInventoryMachineModel.0 = STRING: "N1124T-ON"
# DNOS-SWITCHING-MIB::agentInventorySoftwareVersion.0 = STRING: "6.7.1.17"


from typing import Optional, List

from cmk.agent_based.v2 import (
    exists,
    HostLabel,
    HostLabelGenerator,
    SimpleSNMPSection,
    SNMPSection,
    SNMPTree,
    startswith,
    StringTable,
)


def parse_dnos_agentinventory(string_table: StringTable) -> dict:
    if not string_table:
        return None
    return dict(
        model=string_table[0][0],
        version=string_table[0][1],
    )


def host_label_dnos_agentinventory(section: dict) -> HostLabelGenerator:
    yield HostLabel("dnos/model", section['model'])
    yield HostLabel("dnos/version", section['version'])
    yield HostLabel("dnos/major", section['version'].split('.')[0])


snmp_section_dnos_agentinventory = SimpleSNMPSection(
    name = "dnos_agentinventory",
    parse_function=parse_dnos_agentinventory,
    host_label_function=host_label_dnos_agentinventory,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.1',
        oids = [
            '3',  # DNOS-SWITCHING-MIB::agentInventoryMachineModel
            '13',  # DNOS-SWITCHING-MIB::agentInventorySoftwareVersion
        ],
    ),
    detect=exists(".1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.1.3.*"),
)


def parse_dnos10_agentinventory(string_table: List[StringTable]) -> Optional[dict]:
    if not string_table:
        return None

    imageVersions = dict(string_table[1])
    cardType = dict(string_table[3])

    return dict(
        model=cardType[string_table[2][0][0]].split(' ', 1)[0],
        version=imageVersions[string_table[0][0][0]],
    )


snmp_section_dnos10_agentinventory = SNMPSection(
    name = "dnos10_agentinventory",
    parse_function=parse_dnos10_agentinventory,
    host_label_function=host_label_dnos_agentinventory,
    fetch = [
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.2.4',
            oids = [
                '0',   # DELLEMC-OS10-CHASSIS-MIB::os10SwModuleCurrentBootSource
            ],
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.2.6.1',
            oids = [
                '1',   # DELLEMC-OS10-CHASSIS-MIB::os10SwModuleIndex
                '2',   # DELLEMC-OS10-CHASSIS-MIB::os10SwModuleImgVers
            ],
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.1.3.1.2',
            oids = [
                '1',   # DELLEMC-OS10-CHASSIS-MIB::os10ChassisType
            ],
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1',
            oids = [
                '2',   # DELLEMC-OS10-CHASSIS-MIB::os10CardType
                '3',   # DELLEMC-OS10-CHASSIS-MIB::os10CardDescription
            ],
        ),
    ],
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.674.11000.5000.100")
)
