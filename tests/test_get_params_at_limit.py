# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT

from src.data_analysis_helper.root import RepeatedFit, get_params_at_limit


def test_get_params_at_limit_one_param_at_limit():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 4, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    lists_params_at_limit = [
        get_params_at_limit(fitresult) for fitresult in repeated_fit.fitresults
    ]
    for list_params_at_limit in lists_params_at_limit:
        assert len(list_params_at_limit) == 1


def test_get_params_at_limit_two_params_at_limit():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", -4, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 4, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    lists_params_at_limit = [
        get_params_at_limit(fitresult, width="limits", threshold=0.05)
        for fitresult in repeated_fit.fitresults
    ]
    for list_params_at_limit in lists_params_at_limit:
        assert len(list_params_at_limit) == 2


def test_get_params_at_limit_within_limit():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    lists_params_at_limit = [
        get_params_at_limit(fitresult, width=1, threshold=0.1)
        for fitresult in repeated_fit.fitresults
    ]
    for list_params_at_limit in lists_params_at_limit:
        assert len(list_params_at_limit) == 0


def test_get_params_at_limit_one_param_at_limit_custom_width():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 4, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    lists_params_at_limit = [
        get_params_at_limit(fitresult, width=(0.1, 0.1), threshold=0.3)
        for fitresult in repeated_fit.fitresults
    ]
    for list_params_at_limit in lists_params_at_limit:
        assert len(list_params_at_limit) == 1
