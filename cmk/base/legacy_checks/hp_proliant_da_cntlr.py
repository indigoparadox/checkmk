#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info

from cmk.agent_based.v2 import SNMPTree
from cmk.agent_based.v2.type_defs import StringTable
from cmk.plugins.lib.hp_proliant import DETECT

hp_proliant_da_cntlr_cond_map = {
    "1": (3, "other"),
    "2": (0, "ok"),
    "3": (1, "degraded"),
    "4": (2, "failed"),
}

hp_proliant_da_cntlr_role_map = {
    "1": "other",
    "2": "notDuplexed",
    "3": "active",
    "4": "backup",
}


hp_proliant_da_cntlr_state_map = {
    "1": (3, "other"),
    "2": (0, "ok"),
    "3": (2, "generalFailure"),
    "4": (2, "cableProblem"),
    "5": (2, "poweredOff"),
}


def parse_hp_proliant_da_cntlr(string_table: StringTable) -> StringTable:
    return string_table


def inventory_hp_proliant_da_cntlr(info):
    if info:
        return [(line[0], None) for line in info]
    return []


def check_hp_proliant_da_cntlr(item, params, info):
    for line in info:
        index, model, slot, cond, role, b_status, b_cond, serial = line
        if index == item:
            sum_state = 0
            output = []

            for val, label, map_ in [
                (cond, "Condition", hp_proliant_da_cntlr_cond_map),
                (b_cond, "Board-Condition", hp_proliant_da_cntlr_cond_map),
                (b_status, "Board-Status", hp_proliant_da_cntlr_state_map),
            ]:
                this_state = map_[val][0]
                state_txt = ""
                if this_state == 1:
                    state_txt = " (!)"
                elif this_state == 2:
                    state_txt = " (!!)"
                sum_state = max(sum_state, this_state)
                output.append(f"{label}: {map_[val][1]}{state_txt}")

            output.append(
                "(Role: {}, Model: {}, Slot: {}, Serial: {})".format(
                    hp_proliant_da_cntlr_role_map.get(role, "unknown"), model, slot, serial
                )
            )

            return (sum_state, ", ".join(output))
    return (3, "Controller not found in snmp data")


check_info["hp_proliant_da_cntlr"] = LegacyCheckDefinition(
    parse_function=parse_hp_proliant_da_cntlr,
    detect=DETECT,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.232.3.2.2.1.1",
        oids=["1", "2", "5", "6", "9", "10", "12", "15"],
    ),
    service_name="HW Controller %s",
    discovery_function=inventory_hp_proliant_da_cntlr,
    check_function=check_hp_proliant_da_cntlr,
)
