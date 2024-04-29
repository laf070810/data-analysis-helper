# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT
from src.data_analysis_helper import RepeatedFit


def test_repeatedfit():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -5, 5)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 5)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(pdf, [mean, sigma], 10, random_seed=0)
    repeated_fit.do_repeated_fit(data)

    repeated_fit.print_all_results()
    repeated_fit.print_succeeded_results()
    repeated_fit.print_best_result()
    result_best = repeated_fit.get_best_result()

    assert len(repeated_fit.fitresults) == 10
    assert len(repeated_fit.get_succeeded_results()) == 10
    assert result_best is not None
    assert round(result_best.floatParsFinal().find("mean").getVal(), 1) == 0.0
    assert round(result_best.floatParsFinal().find("sigma").getVal(), 1) == 1.0
