# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import subprocess
from collections.abc import Callable

import ROOT


def print_func(string="", end="\n"):
    if end is None:
        end = ""
    subprocess.run(f'echo -n "{string}{end}"', shell=True)


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

    def get_succeeded_results(self) -> list[ROOT.RooFitResult]:
        return [fitresult for fitresult in self.fitresults if fitresult.status() == 0]

    def get_best_result(self) -> ROOT.RooFitResult | None:
        succeeded_results = self.get_succeeded_results()
        if len(succeeded_results) > 0:
            return sorted(succeeded_results, key=lambda x: x.minNll())[0]
        else:
            return None

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
    fitresult: ROOT.RooFitResult, *, threshold: float = 0.05
) -> list:
    params_at_limit = []
    for variable in fitresult.floatParsFinal():
        width = variable.getMax() - variable.getMin()
        if ((variable.getVal() - variable.getMin()) / width < threshold) or (
            (variable.getMax() - variable.getVal()) / width < threshold
        ):
            params_at_limit.append(variable)
    return params_at_limit


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
