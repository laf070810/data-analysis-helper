# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import numpy as np

from src.data_analysis_helper.plot import histplot


def test_histplot():
    # 生成示例数据
    np.random.seed(42)
    data1 = np.random.normal(0, 1, 1000)
    data2 = np.random.normal(0.5, 1, 1500)
    weights1 = np.random.uniform(0.5, 1.5, 1000)
    weights2 = np.random.uniform(0.5, 2, 1500)

    histplot(data1, bins=50, xlabel="test")
    histplot(data1, bins=50, xlabel="test", weights=weights1)
    histplot(data2, bins=100, xlabel="test", unit="MeV", weights=weights2)
