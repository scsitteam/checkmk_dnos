#!/usr/bin/env python3
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
#

import pytest  # type: ignore[import]
from cmk_addons.plugins.dnos.agent_based import dnos_mem


@pytest.mark.parametrize('string_table, result', [
    ([], None),
    ([['530656', '1014320']], {'MemFree': 543391744, 'MemTotal': 1038663680}),
])
def test_parse_dnos_mem(string_table, result):
    assert dnos_mem.parse_dnos_mem(string_table) == result
