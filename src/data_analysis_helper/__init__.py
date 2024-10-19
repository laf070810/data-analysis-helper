# SPDX-FileCopyrightText: 2024-present Anfeng Li <anfeng.li@cern.ch>
#
# SPDX-License-Identifier: MIT

import subprocess


def print_func(string="", end="\n"):
    if end is None:
        end = ""
    subprocess.run(f'echo -n "{string}{end}"', shell=True)
