# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import numpy as np
from scipy.stats import ks_2samp

from src.data_analysis_helper.stats import kstest


def test_kstest():
    # 生成示例数据
    np.random.seed(42)
    data1 = np.random.normal(0, 1, 100)
    data2 = np.random.normal(0.5, 1, 150)
    weights1 = np.random.uniform(0.5, 1.5, 100)
    weights2 = np.random.uniform(0.5, 2, 150)

    # 执行加权KS检验
    ks_stat_weighted, p_value_weighted = kstest(
        data1, data2, weights1, weights2, n_permutations=1000
    )
    print("\nKS检验结果（带权重）:")
    print(f"KS统计量: {ks_stat_weighted}")
    print(f"P值: {p_value_weighted}")

    # 执行无加权KS检验
    ks_stat, p_value = kstest(data1, data2)
    print("\nKS检验结果（忽略权重）:")
    print(f"KS统计量: {ks_stat}")
    print(f"P值: {p_value}")
    assert p_value < 0.01
    assert abs(ks_stat_weighted - ks_stat) > 0.01

    # 对比标准KS检验（忽略权重）
    result_std = ks_2samp(data1, data2)
    print("\n标准KS检验结果（忽略权重）:")
    print(f"KS统计量: {result_std.statistic}")
    print(f"P值: {result_std.pvalue}")
    assert round(ks_stat, 2) == round(result_std.statistic, 2)
