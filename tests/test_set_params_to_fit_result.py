# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT

from src.data_analysis_helper.root import RepeatedFit, set_params_to_fit_result


def test_set_params_to_fit_result():
    def import_model(workspace):
        x = ROOT.RooRealVar("x", "x", -5, 5)
        mean = ROOT.RooRealVar("mean", "mean", 0, -3, 3)
        sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.5, 3)
        pdf = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

        workspace.Import(pdf)

    workspace = ROOT.RooWorkspace("w", "w")
    import_model(workspace)

    x = workspace.var("x")
    pdf = workspace.pdf("gauss")

    data = pdf.generate(x, 10000)
    repeated_fit = RepeatedFit(model=pdf, data=data, num_fits=1)
    repeated_fit.do_repeated_fit()

    result_best = repeated_fit.get_best_result()
    assert result_best is not None

    workspace2 = ROOT.RooWorkspace("w2", "w2")
    import_model(workspace2)

    assert (
        workspace2.var("mean").getVal()
        != result_best.floatParsFinal().find("mean").getVal()
    )
    assert (
        workspace2.var("mean").getError()
        != result_best.floatParsFinal().find("mean").getError()
    )
    assert (
        workspace2.var("sigma").getVal()
        != result_best.floatParsFinal().find("sigma").getVal()
    )
    assert (
        workspace2.var("sigma").getError()
        != result_best.floatParsFinal().find("sigma").getError()
    )

    set_params_to_fit_result(workspace2.allVars(), result_best)

    assert (
        workspace2.var("mean").getVal()
        == result_best.floatParsFinal().find("mean").getVal()
    )
    assert (
        workspace2.var("mean").getError()
        == result_best.floatParsFinal().find("mean").getError()
    )
    assert (
        workspace2.var("sigma").getVal()
        == result_best.floatParsFinal().find("sigma").getVal()
    )
    assert (
        workspace2.var("sigma").getError()
        == result_best.floatParsFinal().find("sigma").getError()
    )

    workspace3 = ROOT.RooWorkspace("w3", "w3")
    import_model(workspace3)
    pdf = workspace3.pdf("gauss")

    assert (
        pdf.getVariables().find("mean").getVal()
        != result_best.floatParsFinal().find("mean").getVal()
    )
    assert (
        pdf.getVariables().find("mean").getError()
        != result_best.floatParsFinal().find("mean").getError()
    )
    assert (
        pdf.getVariables().find("sigma").getVal()
        != result_best.floatParsFinal().find("sigma").getVal()
    )
    assert (
        pdf.getVariables().find("sigma").getError()
        != result_best.floatParsFinal().find("sigma").getError()
    )

    set_params_to_fit_result(
        workspace3.allVars(), result_best, set_error=False, verbose=True
    )

    assert (
        pdf.getVariables().find("mean").getVal()
        == result_best.floatParsFinal().find("mean").getVal()
    )
    assert (
        pdf.getVariables().find("mean").getError()
        != result_best.floatParsFinal().find("mean").getError()
    )
    assert (
        pdf.getVariables().find("sigma").getVal()
        == result_best.floatParsFinal().find("sigma").getVal()
    )
    assert (
        pdf.getVariables().find("sigma").getError()
        != result_best.floatParsFinal().find("sigma").getError()
    )
