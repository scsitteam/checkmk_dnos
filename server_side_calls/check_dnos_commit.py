# -*- encoding: utf-8; py-indent-offset: 4 -*-
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

from collections.abc import Iterator

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    ActiveCheckCommand,
    ActiveCheckConfig,
    replace_macros,
    Secret,
)


class Params(BaseModel, frozen=True):
    host: str | None = None
    user: str
    password: Secret


def commands_function(
    params: Params,
    host_config: object,
) -> Iterator[ActiveCheckCommand]:
    command_arguments = []

    if 'host' in params:
        command_arguments += ['--host', params.host]
    else:
        command_arguments += ['--host', replace_macros('$HOSTNAME$', host_config.macros)]

    command_arguments += ['--user', params.user]
    command_arguments += ['--password', params.password.unsafe()]

    yield ActiveCheckCommand(
        service_description='Config Commit',
        command_arguments=command_arguments,
    )


active_check_crl_url = ActiveCheckConfig(
    name='dnos_commit',
    parameter_parser=Params.model_validate,
    commands_function=commands_function,
)
