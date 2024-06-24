#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# dnos_cpu - Dell Networking OS Memory Check for Checkmk
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
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessMemFree.0 = INTEGER: 530656 KBytes
# DNOS-SWITCHING-MIB::agentSwitchCpuProcessMemAvailable.0 = INTEGER: 1014320 KBytes


from typing import Optional

from cmk.agent_based.v2 import (
    exists,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
)
from cmk.plugins.lib.memory import SectionMemUsed


def parse_dnos_mem(string_table: StringTable) -> Optional[SectionMemUsed]:
    if not string_table:
        return None
    section: SectionMemUsed = dict(
        MemFree=int(string_table[0][0]) * 1024,
        MemTotal=int(string_table[0][1]) * 1024,
    )
    return section


snmp_section_dnos_mem = SimpleSNMPSection(
    name = "dnos_mem",
    parse_function=parse_dnos_mem,
    parsed_section_name="mem_used",
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.4',
        oids = [
            '1',  # DNOS-SWITCHING-MIB::agentSwitchCpuProcessMemFree
            '2',  # DNOS-SWITCHING-MIB::agentSwitchCpuProcessMemAvailable
        ],
    ),
    detect=exists(".1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.4.1.0"),
)
