# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

from collections.abc import Callable, Iterable
from typing import Literal

import ROOT

from . import print_func


class RepeatedFit:
    def __init__(
        self,
        *,
        model: ROOT.RooAbsPdf,
        data: ROOT.RooDataSet,
        num_fits: int,
        parameter_list: ROOT.RooArgSet | list[ROOT.RooAbsArg] | list[str] | None = None,
        allow_fixed_params: bool = False,
        random_seed: int | None = None,
        print_func: Callable = print_func,
    ):
        self.model: ROOT.RooAbsPdf = model
        self.data: ROOT.RooDataSet = data
        self.num_fits: int = num_fits
        self.print_func = print_func

        if parameter_list is None:
            self.parameter_list: list[ROOT.RooAbsArg] = [
                parameter
                for parameter in model.getParameters(data)
                if (not parameter.isConstant()) or allow_fixed_params
            ]
        else:
            self.parameter_list: list[ROOT.RooAbsArg] = [
                # match just by name
                model.getParameters(data).find(parameter)
                for parameter in parameter_list
                # IMPORTANT: filter fixed parameters, which can be overridden by allow_fixed_params
                if (not model.getParameters(data).find(parameter).isConstant())
                or allow_fixed_params
            ]

        if random_seed is not None:
            ROOT.RooRandom.randomGenerator().SetSeed(random_seed)
        else:
            ROOT.RooRandom.randomGenerator().SetSeed()

        self.parameter_samples: ROOT.RooDataSet = ROOT.RooUniform(
            "uniform", "uniform", self.parameter_list[0]
        ).generate(self.parameter_list[0], num_fits)
        for parameter in self.parameter_list[1:]:
            self.parameter_samples.merge(
                ROOT.RooUniform("uniform", "uniform", parameter).generate(
                    parameter, num_fits
                )
            )

    def do_repeated_fit(self, **fit_options) -> None:
        fit_options["Save"] = True
        self.fitresults: list[ROOT.RooFitResult] = []
        for index in range(self.num_fits):
            self.print_func(f"\n\n---------- begin of fit {index} ----------\n")
            if index > 0:  # use original initial values when index == 0
                for parameter in self.parameter_samples.get(index):
                    self.model.getParameters(self.data).find(parameter).setVal(
                        parameter.getVal()
                    )
            self.fitresults.append(self.model.fitTo(self.data, **fit_options))
            self.print_func(f"\n---------- end of fit {index} ----------\n\n")

    def get_succeeded_results(
        self, *, allowed_statuses: list[int] | Literal["all"] = [0]
    ) -> list[ROOT.RooFitResult]:
        if allowed_statuses == "all":
            return self.fitresults
        else:
            return [
                fitresult
                for fitresult in self.fitresults
                if fitresult.status() in allowed_statuses
            ]

    def get_best_result(
        self, *, allowed_statuses: list[int] | Literal["all"] = [0]
    ) -> ROOT.RooFitResult | None:
        succeeded_results = self.get_succeeded_results(
            allowed_statuses=allowed_statuses
        )
        if len(succeeded_results) > 0:
            return sorted(succeeded_results, key=lambda x: x.minNll())[0]
        else:
            return None

    def print_observables(self, *args, **kwargs) -> None:
        for variable in self.model.getObservables(self.data):
            variable.Print(*args, **kwargs)

    def print_float_parameters(self, *args, **kwargs) -> None:
        for variable in self.model.getParameters(self.data):
            if not variable.isConstant():
                variable.Print(*args, **kwargs)

    def print_const_parameters(self, *args, **kwargs) -> None:
        for variable in self.model.getParameters(self.data):
            if variable.isConstant():
                variable.Print(*args, **kwargs)

    def print_all_results(self) -> None:
        self.print_func(f"\n********** printing all fit results **********\n")
        for i, fitresult in enumerate(self.fitresults):
            self.print_func(f"\n********** printing fit result {i} **********\n")
            self.print_func(f"NLL: {fitresult.minNll()}")
            self.print_func(f"edm: {fitresult.edm()}")
            self.print_func()
            fitresult.Print("V")
            self.print_func(
                f"\n********** finished printing fit result {i} **********\n"
            )

    def print_succeeded_results(self) -> None:
        self.print_func(f"\n********** printing succeeded fit results **********\n")
        for fitresult in self.get_succeeded_results():
            index = self.fitresults.index(fitresult)
            self.print_func(f"\n********** printing fit result {index} **********\n")
            self.print_func(f"NLL: {fitresult.minNll()}")
            self.print_func(f"edm: {fitresult.edm()}")
            self.print_func()
            fitresult.Print("V")
            self.print_func(
                f"\n********** finished printing fit result {index} **********\n"
            )

    def print_best_result(self) -> None:
        self.print_func(f"\n********** printing the best fit result **********\n")
        fitresult = self.get_best_result()
        if fitresult is not None:
            index = self.fitresults.index(fitresult)
            self.print_func(f"\nThe best fit result is result {index}. \n")
            self.print_func(f"\n********** printing fit result {index} **********\n")
            self.print_func(f"NLL: {fitresult.minNll()}")
            self.print_func(f"edm: {fitresult.edm()}")
            self.print_func()
            fitresult.Print("V")
            self.print_func(
                f"\n********** finished printing fit result {index} **********\n"
            )
        else:
            self.print_func("\nNone of the fits has status 0. \n")


def get_params_at_limit(
    fitresult: ROOT.RooFitResult,
    *,
    width: float | tuple[float, float] | Literal["limits", "error"] = "error",
    threshold: float = 3,
) -> list:
    params_at_limit = []
    for variable in fitresult.floatParsFinal():
        if width == "limits":
            width_low = variable.getMax() - variable.getMin()
            width_high = width_low
        elif width == "error":
            width_low = -variable.getErrorLo()
            width_high = variable.getErrorHi()
        elif isinstance(width, tuple):
            width_low = width[0]
            width_high = width[1]
        else:
            width_low = width
            width_high = width_low
        if ((variable.getVal() - variable.getMin()) / width_low < threshold) or (
            (variable.getMax() - variable.getVal()) / width_high < threshold
        ):
            params_at_limit.append(variable)
    return params_at_limit


def set_params_to_fit_result(
    params: Iterable[ROOT.RooAbsArg],
    fitresult: ROOT.RooFitResult,
    set_error: bool = True,
    verbose: bool = False,
):
    for param in params:
        if (
            fitresult.floatParsFinal().find(param) != None
        ):  # "is not None" doesn't work here
            print(f"setting {param.GetName()} to floatParsFinal value of fit result")
            param.setVal(fitresult.floatParsFinal().find(param).getVal())
            if set_error:
                print(
                    f"setting {param.GetName()} to floatParsFinal error of fit result"
                )
                param.setError(fitresult.floatParsFinal().find(param).getError())
        elif fitresult.constPars().find(param) != None:
            print(f"setting {param.GetName()} to constPars value of fit result")
            param.setVal(fitresult.constPars().find(param).getVal())
        else:
            if verbose:
                print(f"{param.GetName()} not found in fit result")
