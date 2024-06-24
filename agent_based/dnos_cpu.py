#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# dnos_cpu - Dell Networking OS CPU Load Check for Checkmk
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
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilization.0 = STRING: "    5 Secs (  7.3872%)   60 Secs ( 11.8040%)  300 Secs ( 11.2942%)"
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationFive.0 = Gauge32: 7 percent
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationSixty.0 = Gauge32: 12 percent
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationThreeHundred.0 = Gauge32: 11 percent


from typing import Optional

from cmk.agent_based.v2 import (
    exists,
    SNMPTree,
    StringTable,
    SimpleSNMPSection,
)
from cmk.plugins.lib.cpu import Load, Section


def parse_dnos_cpu(string_table: StringTable) -> Optional[Section]:
    return (
        Section(
            load=Load(
                *(float(sub_table) / 100 for sub_table in string_table[0]),
            ),
            num_cpus=1,
        )
        if string_table
        else None
    )


snmp_section_dnos_cpu = SimpleSNMPSection(
    name = "dnos_cpu",
    parse_function=parse_dnos_cpu,
    parsed_section_name="cpu",
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.4',
        oids = [
            '10',  # DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationFive
            '11',  # DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationSixty
            '12',  # DNOS-SWITCHING-MIB::agentSwitchCpuProcessTotalUtilizationThreeHundred
        ],
    ),
    detect=exists(".1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.4.10.0"),
)
