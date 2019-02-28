#!/usr/bin/env python
# -*- coding:utf-8 -*-

from logbook import Logger
from logbook import TimedRotatingFileHandler
import json
import sys

from assets import models


class NewAssets(object):
    def __init__(self, data):
        self.logger = self.get_logger()
        self.data = data

    @staticmethod
    def get_logger():
        log_name = sys.argv[0].split('/')[-1][:-4]
        handler = TimedRotatingFileHandler('../logs/' + log_name + '.log')
        # handler = TimedRotatingFileHandler('../logs/' + __name__ + '.log')
        handler.push_application()
        return Logger(name=log_name, level=11)

    def add_to_new_assets_zone(self):
        cpu_info = self.data["cpu"]
        os_info = self.data["os"]
        ram_info = self.data["ram"]
        network_info = self.data["network"]
        disk_info = self.data["storage"]
        defaults = {
            "name": self.data.get["hostname"],
            'data': json.dumps(self.data),
            'asset_type': self.data.get('asset_type'),
            'manufacturer': self.data.get('manufacturer'),
            'model': self.data.get('model'),
            "ram": ram_info,
            # 'ram_size': self.data.get('ram_size'),
            'hostname': self.data.get('hostname'),
            "cpu": cpu_info,
            # 'cpu_model': cpu_info.get('cpu_model'),
            # 'cpu_count': cpu_info.get('cpu_count'),
            # 'cpu_core_count': cpu_info.get('cpu_core_count'),
            # 'os_distribution': os_info.get('os_distribution'),
            # 'os_release': os_info.get('os_release'),
            # 'os_type': os_info.get('os_type'),
            "os": os_info,
            "network": network_info,
            "storage": disk_info

        }
        models.NewAssetApprovalZone.objects.update_or_create(name=self.data['name'], defaults=defaults)

        return '资产已经加入或更新待审批区！'



