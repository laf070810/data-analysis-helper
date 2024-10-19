# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

from src.data_analysis_helper.expr import (
    get_clone_rejection_expression,
    get_invariant_mass_expression,
    get_p_expression,
    get_pe_expression,
)


def test_get_invariant_mass_expression():
    from math import sqrt

    assert eval(
        get_invariant_mass_expression(["pip", "pim"]),
        {
            "pip_PX": 1,
            "pip_PY": 2,
            "pip_PZ": 3,
            "pip_PE": 4,
            "pim_PX": 1,
            "pim_PY": 2,
            "pim_PZ": 3,
            "pim_PE": 4,
            "sqrt": sqrt,
        },
    ) == sqrt(8)


def test_pe_expression():
    from math import sqrt

    assert eval(
        get_pe_expression("pi", mass_hypothesis=4),
        {
            "pi_PX": 1,
            "pi_PY": 2,
            "pi_PZ": 3,
            "sqrt": sqrt,
        },
    ) == sqrt(30)
    assert eval(
        get_pe_expression("pi"),
        {
            "pi_PX": 1,
            "pi_PY": 2,
            "pi_PZ": 3,
            "pi_M": 4,
            "sqrt": sqrt,
        },
    ) == sqrt(30)


def test_get_p_expression():
    from math import sqrt

    assert eval(
        get_p_expression("pi"),
        {
            "pi_PX": 1,
            "pi_PY": 2,
            "pi_PZ": 3,
            "sqrt": sqrt,
        },
    ) == sqrt(14)
