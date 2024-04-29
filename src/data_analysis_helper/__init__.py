# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT


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
    ):
        self.model: ROOT.RooAbsPdf = model
        self.data: ROOT.RooDataSet = data
        self.num_fits: int = num_fits

        if parameter_list is None:
            self.parameter_list: ROOT.RooArgSet = ROOT.RooArgSet(
                [
                    parameter
                    for parameter in model.getParameters(data)
                    if (not parameter.isConstant()) or allow_fixed_params
                ]
            )
        else:
            self.parameter_list: ROOT.RooArgSet = ROOT.RooArgSet(
                [
                    # match just by name
                    model.getParameters(data).find(parameter)
                    for parameter in parameter_list
                    # IMPORTANT: filter fixed parameters, which can be overridden by allow_fixed_params
                    if (not model.getParameters(data).find(parameter).isConstant())
                    or allow_fixed_params
                ]
            )
        if self.parameter_list.size() > 31:
            raise Exception("RooUniform does not allow >31 parameters. ")

        if random_seed is not None:
            ROOT.RooRandom.randomGenerator().SetSeed(random_seed)
        else:
            ROOT.RooRandom.randomGenerator().SetSeed()

        self.parameter_samples: ROOT.RooDataSet = ROOT.RooUniform(
            "uniform", "uniform", self.parameter_list
        ).generate(self.parameter_list, num_fits)

    def do_repeated_fit(self, **fit_options) -> None:
        fit_options["Save"] = True
        self.fitresults: list[ROOT.RooFitResult] = []
        for index in range(self.num_fits):
            print(f"\n\n---------- begin of fit {index} ----------\n")
            if index > 0:  # use original initial values when index == 0
                for parameter in self.parameter_samples.get(index):
                    self.model.getParameters(self.data).find(parameter).setVal(
                        parameter.getVal()
                    )
            self.fitresults.append(self.model.fitTo(self.data, **fit_options))
            print(f"\n---------- end of fit {index} ----------\n\n")

    def get_succeeded_results(self) -> list[ROOT.RooFitResult]:
        return [fitresult for fitresult in self.fitresults if fitresult.status() == 0]

    def get_best_result(self) -> ROOT.RooFitResult | None:
        succeeded_results = self.get_succeeded_results()
        if len(succeeded_results) > 0:
            return sorted(succeeded_results, key=lambda x: x.minNll())[0]
        else:
            return None

    def print_all_results(self) -> None:
        print(f"\n********** printing all fit results **********\n")
        for i, fitresult in enumerate(self.fitresults):
            print(f"\n********** printing fit result {i} **********\n")
            print(f"NLL: {fitresult.minNll()}")
            print(f"edm: {fitresult.edm()}")
            print()
            fitresult.Print("V")
            print(f"\n********** finished printing fit result {i} **********\n")

    def print_succeeded_results(self) -> None:
        print(f"\n********** printing succeeded fit results **********\n")
        for fitresult in self.get_succeeded_results():
            index = self.fitresults.index(fitresult)
            print(f"\n********** printing fit result {index} **********\n")
            print(f"NLL: {fitresult.minNll()}")
            print(f"edm: {fitresult.edm()}")
            print()
            fitresult.Print("V")
            print(f"\n********** finished printing fit result {index} **********\n")

    def print_best_result(self) -> None:
        print(f"\n********** printing the best fit result **********\n")
        fitresult = self.get_best_result()
        if fitresult is not None:
            index = self.fitresults.index(fitresult)
            print(f"\nThe best fit result is result {index}. \n")
            print(f"\n********** printing fit result {index} **********\n")
            print(f"NLL: {fitresult.minNll()}")
            print(f"edm: {fitresult.edm()}")
            print()
            fitresult.Print("V")
            print(f"\n********** finished printing fit result {index} **********\n")
        else:
            print("\nNone of the fits has status 0. \n")
