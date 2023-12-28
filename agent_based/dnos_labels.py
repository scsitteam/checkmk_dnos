#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# dnos_labels - Dell Networking OS Host labels
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
# DNOS-SWITCHING-MIB::agentInventoryMachineModel.0 = STRING: "N1124T-ON"
# DNOS-SWITCHING-MIB::agentInventorySoftwareVersion.0 = STRING: "6.7.1.17"


from cmk.base.plugins.agent_based.agent_based_api.v1 import exists, register, SNMPTree, HostLabel
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable, HostLabelGenerator


def parse_dnos_agentinventory(string_table: StringTable) -> dict:
    return dict(
        model=string_table[0][0],
        version=string_table[0][1],
    )


def host_label_dnos_agentinventory(section: dict) -> HostLabelGenerator:
    yield HostLabel("dnos/model", section['model'])
    yield HostLabel("dnos/version", section['version'])
    yield HostLabel("dnos/major", section['version'].split('.')[0])


register.snmp_section(
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
    detect=exists(".1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.1.3.0"),
)
