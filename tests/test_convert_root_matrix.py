# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import numpy as np
import ROOT

from src.data_analysis_helper.root import convert_root_matrix


def test_convert_root_matrix():
    nrows = 3
    ncols = 10
    matrix = ROOT.TMatrixD(nrows, ncols)
    for i in range(nrows):
        for j in range(ncols):
            matrix[i, j] = i + j
    mat = convert_root_matrix(matrix, dtype=np.float64)
    for i in range(nrows):
        for j in range(ncols):
            assert mat[i, j] == i + j
