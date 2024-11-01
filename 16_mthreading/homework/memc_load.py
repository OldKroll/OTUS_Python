import collections
import glob
import gzip
import logging
import multiprocessing
import os
import sys
from collections import Counter
from functools import partial
from optparse import OptionParser
from pathlib import Path

import appsinstalled_pb2
import memcache

NORMAL_ERR_RATE = 0.01
RETRY_NUMBER = 3
RETRY_TIMEOUT_SECONDS = 1
SOCKET_TIMEOUT_SECONDS = 3

AppsInstalled = collections.namedtuple(
    "AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"]
)


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc_client, appsinstalled, dry=False):
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()

    for _ in range(RETRY_NUMBER):
        try:
            if dry:
                logging.debug(
                    "%s - %s -> %s"
                    % (memc_client.servers, key, str(ua).replace("\n", " "))
                )
            else:
                memc_client.set_multi({key: packed})
            return True
        except Exception as exc:
            logging.exception(
                "Cannot write to memc %s: %s" % (memc_client.servers, exc)
            )
            return False


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def process_line(raw_line, memc_client, dry):
    line = raw_line.decode("utf-8").strip()
    if not line:
        return "NO LINE"
    try:
        appsinstalled = parse_appsinstalled(line)
    except ValueError as e:
        logging.error(f"Cannot parse line: {e}")
        return "ERR"

    result = insert_appsinstalled(memc_client, appsinstalled, dry)
    if not result:
        return "ERR"

    return "OK"


def process_file(fn, device_memc, dry) -> None:
    worker = multiprocessing.current_process()
    logging.info(f"[{worker.name}] Processing {fn}")

    memc_client = memcache.Client(
        device_memc,
        socket_timeout=3,
        dead_retry=RETRY_TIMEOUT_SECONDS,
    )
    with gzip.open(fn) as fd:
        job = partial(process_line, memc_client=memc_client, dry=dry)
        statuses = Counter(map(job, fd))

    ok = statuses["OK"]
    errors = statuses["ERR"]
    processed = ok + errors

    err_rate = float(errors) / processed if processed else 1.0

    if err_rate < NORMAL_ERR_RATE:
        logging.info(
            f"[{worker.name}] [{fn}] Acceptable error rate: {err_rate}."
            f" Successfull load"
        )
    else:
        logging.error(
            f"[{worker.name}] [{fn}] High error rate: "
            f"{err_rate} > {NORMAL_ERR_RATE}. Failed load"
        )

    return fn


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    job = partial(process_file, device_memc=device_memc, dry=options.dry)

    files = sorted(glob.glob(options.pattern), key=lambda file: Path(file).name)

    with multiprocessing.Pool() as pool:
        for processed_file in pool.imap(job, files):
            worker = multiprocessing.current_process()
            logging.info(f"[{worker.name}] Renaming {processed_file}")
            dot_rename(processed_file)


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="./data/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO if not opts.dry else logging.DEBUG,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
