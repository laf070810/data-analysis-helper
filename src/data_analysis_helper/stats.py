# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT


def kstest(data1, data2, weights1=None, weights2=None, n_permutations=1000):
    """
    可带权重的KS检验

    参数:
    data1, data2: 样本数据数组
    weights1, weights2: 对应权重数组
    n_permutations: 置换检验的次数

    返回:
    ks_statistic: KS统计量
    p_value: 估计的p值
    """
    import numpy as np

    def ks_test_statistic(data1, data2, weights1, weights2):
        # 计算加权ECDF
        def weighted_ecdf(data, weights):
            sorted_idx = np.argsort(data)
            sorted_data = data[sorted_idx]
            sorted_weights = weights[sorted_idx]
            cum_weights = np.cumsum(sorted_weights)
            return sorted_data, cum_weights / cum_weights[-1]

        # 计算原始KS统计量
        d1, ecdf1 = weighted_ecdf(data1, weights1)
        d2, ecdf2 = weighted_ecdf(data2, weights2)
        all_values = np.concatenate([d1, d2])
        cdf1 = np.interp(all_values, d1, ecdf1, left=0, right=1)
        cdf2 = np.interp(all_values, d2, ecdf2, left=0, right=1)
        ks_statistic = np.max(np.abs(cdf1 - cdf2))

        return ks_statistic

    if weights1 is None:
        weights1 = np.ones(len(data1))
    if weights2 is None:
        weights2 = np.ones(len(data2))

    ks_statistic = ks_test_statistic(data1, data2, weights1, weights2)

    # 置换检验估计p值
    combined_data = np.concatenate([data1, data2])
    combined_weights = np.concatenate([weights1, weights2])
    n1 = len(data1)
    count = 0

    for _ in range(n_permutations):
        # 打乱标签
        perm_idx = np.random.permutation(len(combined_data))
        perm_data = combined_data[perm_idx]
        perm_weights = combined_weights[perm_idx]

        # 分割为两组
        perm_data1 = perm_data[:n1]
        perm_weights1 = perm_weights[:n1]
        perm_data2 = perm_data[n1:]
        perm_weights2 = perm_weights[n1:]

        # 计算置换后的KS统计量
        perm_ks = ks_test_statistic(
            perm_data1, perm_data2, perm_weights1, perm_weights2
        )

        if perm_ks >= ks_statistic:
            count += 1

    p_value = (count + 1) / (n_permutations + 1)  # 避免p=0

    return ks_statistic, p_value
