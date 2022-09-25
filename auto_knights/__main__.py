# -*- coding=UTF-8 -*-
# pyright: strict
"""arknights automation. """


import argparse
import logging
import logging.handlers
import os
import traceback
import warnings

from . import __version__, app, clients, config, jobs, plugin, version
from .infrastructure.client_device_service import ClientDeviceService
from .infrastructure.logging_log_service import LoggingLogService


def main():
    app.log.text(f"auto_knights: {__version__.VERSION}")
    if config.CHECK_UPDATE:
        version.check_update()
    available_jobs = {
        "public_recruit_tips": jobs.public_recruit_tips,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    parser.add_argument(
        "-p",
        "--plugin",
        nargs="+",
        default=config.PLUGINS,
        help="plugin names to enable",
    )
    parser.add_argument(
        "--adb",
        help="adb connect address like `127.0.0.1:7555`",
        default=config.ADB_ADDRESS,
    )
    args = parser.parse_args()
    job = available_jobs.get(args.job)
    config.ADB_ADDRESS = args.adb

    def _client() -> clients.Client:
        return clients.ADBClient(config.ADB_ADDRESS)

    plugin.reload()
    config.client = _client
    plugins = args.plugin
    for i in plugins:
        plugin.install(i)
    config.apply()

    with app.cleanup:
        
        if not job:
            app.log.text(
                "unknown job: %s\navailable jobs:\n  %s"
                % (args.job, "\n  ".join(available_jobs.keys())),
                level=app.ERROR,
            )
            exit(1)

        c = config.client()
        c.setup()
        app.device = ClientDeviceService(c)
        job()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    app.log = LoggingLogService()

    LOG_PATH = config.LOG_PATH
    if LOG_PATH and LOG_PATH != "-":
        handler = logging.handlers.RotatingFileHandler(
            LOG_PATH, backupCount=3, encoding="utf-8"
        )
        handler.doRollover()
        formatter = logging.Formatter(
            "%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    for i in os.getenv("DEBUG", "").split(","):
        if not i:
            continue
        logging.getLogger(i).setLevel(logging.DEBUG)

    warnings.filterwarnings("once", module="auto_knights(\\..*)?")
    try:
        main()
    except SystemExit:
        raise
    except:
        app.log.text(
            "unexpected exception: %s" % traceback.format_exc(), level=app.ERROR
        )
        exit(1)
