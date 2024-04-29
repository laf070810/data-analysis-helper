# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import ROOT


class RepeatedFit:
    def __init__(
        self,
        model: ROOT.RooAbsPdf,
        parameter_list,
        times: int,
        *,
        random_seed: int = None,
    ):
        self.model: ROOT.RooAbsPdf = model
        self.parameter_list: ROOT.RooArgSet = ROOT.RooArgSet(
            [
                model.getVariables().find(parameter)
                for parameter in parameter_list
                if not model.getVariables().find(parameter).isConstant()
            ]
        )
        self.times: int = times

        if random_seed:
            ROOT.RooRandom.randomGenerator().SetSeed(random_seed)
        else:
            ROOT.RooRandom.randomGenerator().SetSeed()
        if isinstance(parameter_list, ROOT.RooArgSet):
            self.parameter_samples: ROOT.RooDataSet = ROOT.RooUniform(
                "uniform", "uniform", parameter_list
            ).generate(parameter_list, times)
        else:
            self.parameter_samples: ROOT.RooDataSet = ROOT.RooUniform(
                "uniform", "uniform", self.parameter_list
            ).generate(self.parameter_list, times)

    def do_repeated_fit(self, data: ROOT.RooDataSet, **fit_options) -> None:
        fit_options["Save"] = True
        self.fitresults = []
        for index in range(self.times):
            print(f"\n\n---------- begin of fit {index} ----------\n")
            if index > 0:  # use original initial values when index == 0
                for parameter in self.parameter_samples.get(index):
                    if self.parameter_list.find(parameter):
                        self.parameter_list.find(parameter).setVal(parameter.getValV())
            self.fitresults.append(self.model.fitTo(data, **fit_options))
            print(f"\n---------- end of fit {index} ----------\n\n")

    def get_succeeded_results(self) -> list[ROOT.RooFitResult]:
        return [fitresult for fitresult in self.fitresults if fitresult.status() == 0]

    def get_best_result(self) -> ROOT.RooFitResult:
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

    def print_best_result(self):
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
