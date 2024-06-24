# -*- encoding: utf-8; py-indent-offset: 4 -*-
##
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

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    migrate_to_password,
    Password,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import ActiveCheck, Topic


def _form_active_checks_dnos_commit():
    return Dictionary(
        elements={
            'host': DictElement(
                parameter_form=String(
                    title=Title('Host'),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    macro_support=True,
                ),
                required=False,
            ),
            'user': DictElement(
                parameter_form=String(
                    title=Title('Username'),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
                required=True,
            ),
            'password': DictElement(
                parameter_form=Password(
                    title=Title('Password'),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
        }
    )


rule_spec_dnos_commit = ActiveCheck(
    title=Title('Check DellOS Config Commit'),
    help_text=Help('Check if a Dell OS6 Device has commited its config.'),
    topic=Topic.NETWORKING,
    name='dnos_commit',
    parameter_form=_form_active_checks_dnos_commit,
)
