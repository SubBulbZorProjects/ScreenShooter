"""Disk usage function"""

import shutil


def main(path):
    """Get disk usage by specific path"""
    output = {}

    try:
        total, used, free = shutil.disk_usage(path)

        output["Total"] = total
        output["Used"] = used
        output["Free"] = free

    except OSError as error:
        print("Cannot get disk usage: {}".format(error))
        output = False

    return output
