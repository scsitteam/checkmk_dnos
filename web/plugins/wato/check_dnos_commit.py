# -*- encoding: utf-8; py-indent-offset: 4 -*-
##
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

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
)
from cmk.gui.plugins.wato import (
    rulespec_registry,
    IndividualOrStoredPassword,
    HostRulespec,
)
try:
    from cmk.gui.plugins.wato.active_checks import RulespecGroupActiveChecks
except Exception:
    from cmk.gui.plugins.wato.active_checks.common import RulespecGroupActiveChecks


def _valuespec_active_checks_dnos_commit():
    return Dictionary(
        title = "Check DellOS Config Commit",
        help = "Check if a Dell OS6 Device has commited its config.",
        elements = [
            (
                'host',
                TextAscii(
                    title = _("Host"),
                    allow_empty = False
                ),
            ),
            (
                'user',
                TextAscii(
                    title = _("Username"),
                    allow_empty = False
                ),
            ),
            (
                'password',
                IndividualOrStoredPassword(
                    title = _("Password"),
                    allow_empty = False
                ),
            ),
        ],
        required_keys=['user', 'password'],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupActiveChecks,
        match_type='all',
        name='active_checks:dnos_commit',
        valuespec=_valuespec_active_checks_dnos_commit,
    ))
