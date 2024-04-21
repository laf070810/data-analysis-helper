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

    def print_all_results(self) -> None:
        for i, fitresult in enumerate(
            sorted(self.fitresults, key=lambda x: x.minNll())
        ):
            print(f"\n********** printing fit result {i} **********\n")
            print(f"NLL: {fitresult.minNll()}")
            print(f"edm: {fitresult.edm()}")
            print()
            fitresult.Print("V")
            print(f"\n********** finished printing fit result {i} **********\n")

    def get_best_result(self) -> ROOT.RooFitResult:
        return sorted(self.fitresults, key=lambda x: x.minNll())[0]
