#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from typing import Dict

from pchat.core.commons import log_lvl, log_str
from pchat.core.logger import get_logger

logger = get_logger(log_lvl, log_str, __name__)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Pychat cypher",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '1.0.0'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-c", "--client", action="store_true")
        parser.add_argument("-s", "--server", action="store_true")
        parser.add_argument("-i", "--interface", action="store_true")
        parser.add_argument("-u", "--user-name", type=str, default="pc1")
        parser.add_argument("-r", "--recipient", type=str, default="pc2")
        parser.add_argument("--server-host", type=str)
        parser.add_argument("--server-port", type=int)
        parser.add_argument("--client-host", type=str)
        parser.add_argument("--client-port", type=int)
        params: Dict = vars(parser.parse_args())

        if params['client']:
            logger.debug("Client mode")
            if params['user_name'] == "user":
                logger.error("Please provide a user name")
                sys.exit(1)

        if params['server']:
            logger.debug("Host mode")
            run_server(params)

        if params['interface']:
            logger.debug("User interface mode")
            run_client(params)
        else:
            logger.debug("No mode selected")

    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
        sys.exit(0)
