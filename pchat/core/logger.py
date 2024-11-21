#!/usr/src/env python
# -*- coding: utf-8 -*-
import logging
import coloredlogs

from pchat.core.commons import log_lvl, log_str

def get_logger(log_level: str, log_format: str, name: str = None) -> logging.Logger:
    res = logging.getLogger(__name__) if name is None else logging.getLogger(name)
    coloredlogs.install(level=log_level.upper(), fmt=log_format)
    return res

if __name__ == '__main__':
    get_logger(log_lvl, log_str)
