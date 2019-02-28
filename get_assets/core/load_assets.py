#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import json
from assets import models


class GetAssets(object):
    """
    从prometheus获取资产信息
    """
    def __init__(self, url='http://10.1.16.35:9090/prome/api/v1/query'):
        self.url = url

    def request_prome(self, query):
        res = requests.get(self.url + '?query=' + query)
        res_content = json.loads(res.content)
        if res_content['status'] == 'success':
            datas = res_content['data']
            return datas
        else:
            return

        # http_manager = urllib3.PoolManager()
        # r = http_manager.request('GET', self.url + '?query=' + query)
        # if r.status == 'success':
        #     print(r.data)
        #     return r.data
        # else:
        #     print(r)
        #     return False

    def get_network_device(self):
        query = 'up{job="snmp"}'
        network_devices = []
        query_datas = self.request_prome(query)
        if query_datas:
            for metrics in query_datas['result']:
                host_metric = metrics['metric']
                print(host_metric)
                device_ip = host_metric['instance_ip']
                device_type = host_metric['hosts_group']
                network_device = {"ip_addr": device_ip, "sub_asset_type": device_type}
                network_devices.append(network_device)
        return network_devices

    def get_servers(self):
        server = models.Asset()

        query = 'up{job="nodes"}'
        servers = []
        query_datas = self.request_prome(query)
        if query_datas:
            for metrics in query_datas['result']:
                host_metric = metrics['metric']
                print(host_metric)
                server_ip = host_metric['instance_ip']
                # device_type = host_metric['hosts_group']
                # network_device = {"ip_addr": device_ip, "sub_asset_type": device_type}
                server.name = server_ip
                server.ip_addr = server_ip
                yield server_ip
        # return network_devices

    def get_server_info(self, ip):
        metrics = {
            "os": {
                "os_release": {'node_os': 'name'},
                "os_version": {'node_os': 'version'}
            },
            "cpu": {
                "cpu_mode": {'node_cpu_mode': 'cpu_mode'},
                "cpu_num": {"node_cpu_num", 'value'},
            },
            "mem": {
                "mem_capacity": {"node_memory_MemTotal(_bytes|)": 'value'},
            },
            "storasge": {
                "disk_capacity": {"node_filesystem_size(_bytes|)": 'value'},

            }
        }

        # for metric_type, attribute_info in metrics:
        #     for attribute_name, metric_info in attribute_info:
        #         for metric_name, value in metric_info:
        #             query = '{__name__=~' + metric_name + ', instance_ip=' + ip + '}'
        #             query_datas = self.request_prome(query)
        #             if query_datas:
        #                 for metrics in query_datas['result']:
        #                     if value != 'value':
        #                         host_metric = metrics['metric']
        #                         print(host_metric)
        #                         device_ip = host_metric[value]
        #                         device_type = host_metric['hosts_group']
        #                         network_device = {"ip_addr": device_ip, "sub_asset_type": device_type}
        #                         network_devices.append(network_device)
        #                     else:
        #                         host_metric = metrics['value']
        #
        #             return network_devices




get_assets = GetAssets()
# devices = get_assets.get_network_device()
servers = get_assets.get_servers()



