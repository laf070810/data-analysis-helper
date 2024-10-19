# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT


def get_invariant_mass_expression(
    prefix: list[str],
    *,
    suffix_PxPyPzE: str | list[str] = "PXPYPZPE",
    suffix: str = "",
    squared: bool = False,
) -> str:
    if suffix_PxPyPzE == "PXPYPZPE":
        suffix_PxPyPzE = ["_PX", "_PY", "_PZ", "_PE"]
    elif suffix_PxPyPzE == "PXPYPZE":
        suffix_PxPyPzE = ["_PX", "_PY", "_PZ", "_E"]
    elif suffix_PxPyPzE == "TRUEP":
        suffix_PxPyPzE = ["_TRUEP_X", "_TRUEP_Y", "_TRUEP_Z", "_TRUEP_E"]

    sum_of_E = f'({" + ".join([pre + suffix_PxPyPzE[3] + suffix for pre in prefix])})'
    sum_of_PX = f'({" + ".join([pre + suffix_PxPyPzE[0] + suffix for pre in prefix])})'
    sum_of_PY = f'({" + ".join([pre + suffix_PxPyPzE[1] + suffix for pre in prefix])})'
    sum_of_PZ = f'({" + ".join([pre + suffix_PxPyPzE[2] + suffix for pre in prefix])})'

    if squared:
        return f"({sum_of_E} * {sum_of_E} - {sum_of_PX} * {sum_of_PX} - {sum_of_PY} * {sum_of_PY} - {sum_of_PZ} * {sum_of_PZ})"
    else:
        return f"sqrt({sum_of_E} * {sum_of_E} - {sum_of_PX} * {sum_of_PX} - {sum_of_PY} * {sum_of_PY} - {sum_of_PZ} * {sum_of_PZ})"


def get_pe_expression(
    prefix: str,
    *,
    mass_hypothesis: float | str | None = None,
    suffix_PxPyPzM: str | list[str] = "PXPYPZM",
    suffix: str = "",
) -> str:
    if suffix_PxPyPzM == "PXPYPZM":
        suffix_PxPyPzM_list = ["_PX", "_PY", "_PZ", "_M"]
    elif suffix_PxPyPzM == "TRUEP":
        suffix_PxPyPzM_list = ["_TRUEP_X", "_TRUEP_Y", "_TRUEP_Z", "_M"]
    else:
        suffix_PxPyPzM_list = suffix_PxPyPzM
    if mass_hypothesis is not None:
        return f"sqrt(pow({prefix}{suffix_PxPyPzM_list[0]}{suffix}, 2) + pow({prefix}{suffix_PxPyPzM_list[1]}{suffix}, 2) + pow({prefix}{suffix_PxPyPzM_list[2]}{suffix}, 2) + {mass_hypothesis} * {mass_hypothesis})"
    else:
        return f"sqrt(pow({prefix}{suffix_PxPyPzM_list[0]}{suffix}, 2) + pow({prefix}{suffix_PxPyPzM_list[1]}{suffix}, 2) + pow({prefix}{suffix_PxPyPzM_list[2]}{suffix}, 2) + pow({prefix}{suffix_PxPyPzM_list[3]}{suffix}, 2))"


def get_p_expression(
    prefix: str, *, suffix_PxPyPz: str | list[str] = "PXPYPZ", suffix: str = ""
) -> str:
    if suffix_PxPyPz == "PXPYPZ":
        suffix_PxPyPz_list = ["_PX", "_PY", "_PZ"]
    elif suffix_PxPyPz == "TRUEP":
        suffix_PxPyPz_list = ["_TRUEP_X", "_TRUEP_Y", "_TRUEP_Z"]
    else:
        suffix_PxPyPz_list = suffix_PxPyPz
    return f"sqrt(pow({prefix}{suffix_PxPyPz_list[0]}{suffix}, 2) + pow({prefix}{suffix_PxPyPz_list[1]}{suffix}, 2) + pow({prefix}{suffix_PxPyPz_list[2]}{suffix}, 2))"


def get_clone_rejection_expression(prefixes: list[str], threshold: float | str) -> str:
    expressions = []
    for i in range(len(prefixes)):
        for j in range(i + 1, len(prefixes)):
            p1 = f"sqrt({prefixes[i]}_PX * {prefixes[i]}_PX + {prefixes[i]}_PY * {prefixes[i]}_PY + {prefixes[i]}_PZ * {prefixes[i]}_PZ)"
            p2 = f"sqrt({prefixes[j]}_PX * {prefixes[j]}_PX + {prefixes[j]}_PY * {prefixes[j]}_PY + {prefixes[j]}_PZ * {prefixes[j]}_PZ)"
            angle = f"acos(({prefixes[i]}_PX * {prefixes[j]}_PX + {prefixes[i]}_PY * {prefixes[j]}_PY + {prefixes[i]}_PZ * {prefixes[j]}_PZ) / {p1} / {p2})"
            expressions.append(f"(abs({angle}) > {threshold})")
    return " && ".join(expressions)
