#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import sys

import requests
from logbook import TimedRotatingFileHandler, Logger

from get_assets.conf import settings
from get_assets.core.assets_info import SysMetrics

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)


class MetricReport(object):
    def __init__(self):
        self.logger = self.get_logger()
        self.cmdb_url = self.get_conf()

    @staticmethod
    def get_logger():
        log_name = sys.argv[0].split('/')[-1][:-4]
        handler = TimedRotatingFileHandler('../logs/' + log_name + '.log')
        handler.push_application()
        return Logger(name=log_name, level=11)

    @staticmethod
    def get_conf():
        cmdb_url = "http://%s:%s/%s" % (settings.cmdb_info['host'], settings.cmdb_info['port'], settings.cmdb_info['url'])
        return cmdb_url

    def get_metrics(self):
        metric_cllector = SysMetrics()
        metric_cllector.collector()
        assets_metrics = metric_cllector.data
        self.logger.info('Assets info: %s' % assets_metrics)
        return assets_metrics

    def send_metrics(self):
        asset_metric_string = json.dumps(self.get_metrics())
        res = requests.post(self.cmdb_url, data={"asset_data": asset_metric_string})
        if res.status_code == 200:
            self.logger.info('Send assets data to cmdb success, metric: %s' % asset_metric_string)
            self.logger.info(res.content.decode('utf-8'))
        else:
            self.logger.error('Send assets data to cmdb failed, metric: %s' % asset_metric_string)
            self.logger.error(res.content.decode('utf-8'))


if __name__ == '__main__':
    metric_report = MetricReport()
    metric_report.send_metrics()


