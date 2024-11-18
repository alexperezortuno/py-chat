#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from typing import Dict

from pchat.core.chat import Chat
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
        parser.add_argument("-c", "--client", type=bool, default=False)
        parser.add_argument("-s", "--server", type=bool, default=False)
        parser.add_argument("-u", "--user-interface", type=bool, default=False)
        parser.add_argument("-n", "--name", type=str, default="user")
        parser.add_argument("-p", "--port", type=int, default="port")
        params: Dict = vars(parser.parse_args())
        chat = Chat()

        if params['client']:
            logger.debug("Client mode")
            chat.run_client(params)
        elif params['server']:
            logger.debug("Host mode")
            chat.run_host(params)
        elif params['user_interface']:
            logger.debug("User interface mode")
            chat.run_user_interface(params)
        else:
            logger.debug("No mode selected")

    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
        sys.exit(0)
