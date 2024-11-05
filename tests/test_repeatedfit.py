# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT

from src.data_analysis_helper.root import RepeatedFit


def assert_rds_column_no_duplication(rds: ROOT.RooDataSet):
    for parameter in rds.get():
        parameter_sample = rds.to_numpy()[parameter.GetName()]
        assert len(parameter_sample) == len(set(parameter_sample))


def test_repeatedfit():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    repeated_fit.print_all_results()
    repeated_fit.print_succeeded_results()
    repeated_fit.print_best_result()
    result_best = repeated_fit.get_best_result()

    assert_rds_column_no_duplication(repeated_fit.parameter_samples)
    assert len(repeated_fit.fitresults) == 10
    assert len(repeated_fit.get_succeeded_results()) == 10
    assert result_best is not None
    assert round(result_best.floatParsFinal().find("mean").getVal(), 1) == 0.0
    assert round(result_best.floatParsFinal().find("sigma").getVal(), 1) == 1.0


def test_repeatedfit_explicit_paramlist():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -5, 5)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 5)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 50000)
    repeated_fit = RepeatedFit(
        model=pdf, data=data, parameter_list=[mean, sigma], num_fits=10, random_seed=0
    )
    repeated_fit.do_repeated_fit()

    repeated_fit.print_all_results()
    repeated_fit.print_succeeded_results()
    repeated_fit.print_best_result()
    result_best = repeated_fit.get_best_result()

    assert_rds_column_no_duplication(repeated_fit.parameter_samples)
    assert len(repeated_fit.fitresults) == 10
    assert len(repeated_fit.get_succeeded_results()) == 10
    assert result_best is not None
    assert round(result_best.floatParsFinal().find("mean").getVal(), 1) == 0.0
    assert round(result_best.floatParsFinal().find("sigma").getVal(), 1) == 1.0


def test_repeatedfit_manyparams():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    means = [ROOT.RooRealVar(f"mean{i}", f"mean{i}", 0, -1, 1) for i in range(100)]
    mean = ROOT.RooFormulaVar(
        "mean",
        "mean",
        " + ".join([f"mean{i}" for i in range(100)]),
        means,
    )
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 5)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 100)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    assert_rds_column_no_duplication(repeated_fit.parameter_samples)


def test_repeatedfit_custom_print_func():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10, print_func=print)
    repeated_fit.do_repeated_fit()

    repeated_fit.print_all_results()
    repeated_fit.print_succeeded_results()
    repeated_fit.print_best_result()
    result_best = repeated_fit.get_best_result()

    assert_rds_column_no_duplication(repeated_fit.parameter_samples)
    assert len(repeated_fit.fitresults) == 10
    assert len(repeated_fit.get_succeeded_results()) == 10
    assert result_best is not None
    assert round(result_best.floatParsFinal().find("mean").getVal(), 1) == 0.0
    assert round(result_best.floatParsFinal().find("sigma").getVal(), 1) == 1.0


def test_repeatedfit_print_observables_and_parameters():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)

    sigma.setConstant(True)

    repeated_fit.print_observables()
    repeated_fit.print_float_parameters()
    repeated_fit.print_const_parameters("V")


def test_repeatedfit_allowed_statuses():
    x = ROOT.RooRealVar("x", "x", -5, 5)
    mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
    sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
    pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    data = pdf.generate(x, 100)

    mean.setRange(50, 51)  # make the fit fail
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=10)
    repeated_fit.do_repeated_fit()

    repeated_fit.print_all_results()
    repeated_fit.print_succeeded_results()
    repeated_fit.print_best_result()
    result_best_allallowed = repeated_fit.get_best_result(allowed_statuses="all")

    assert_rds_column_no_duplication(repeated_fit.parameter_samples)
    assert len(repeated_fit.fitresults) == 10
    assert len(repeated_fit.get_succeeded_results()) < 10
    assert len(repeated_fit.get_succeeded_results(allowed_statuses=[0, 2, 302])) == 10
    assert len(repeated_fit.get_succeeded_results(allowed_statuses="all")) == 10
    assert result_best_allallowed is not None
