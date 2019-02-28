#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import psutil
import re


class SysMetrics(object):
    def __init__(self):
        self.data = dict()
        self.data['asset_type'] = 'server'

    def collector(self):
        """
        资产信息采集，适用于docker
        :return:
        """
        self.get_os_info()
        self.get_hostname()
        self.get_cpu_info()
        self.get_ram_info()
        self.get_network_info()
        self.get_storage_info()

    def get_hostname(self):
        hostname_file = '/etc/hostname'
        with open(hostname_file, 'r') as f:
            hostname = f.read().strip()
        # data = {
        #     "name": hostname,
        # }
        # return {"hostname": data}
        self.data["hostname"] = hostname

    def get_os_info(self):
        """
        获取操作系统信息
        :return:
        """
        centos7_release = '/etc/centos-release'
        redhat_release = '/etc/redhat-release'
        ubuntu_release = '/etc/os-release'
        if os.path.isfile(centos7_release):
            file = centos7_release
        elif os.path.isfile(redhat_release):
            file = redhat_release
        elif os.path.isfile(ubuntu_release):
            file = ubuntu_release
        else:
            file = ''
        with open(file, 'r') as f:
            os_release = f.readlines()
        if file != ubuntu_release:

            release_list = os_release[0].split()
            if len(os_release) > 4:
                release = release_list[:1]

            else:
                release = release_list[0]
            distribution = release_list[-2]
        else:
            release = 'Ubuntu'
            distribution = os_release.split('=')[1].split()[0]

        data_dic = {
            "os_distribution": distribution,
            "os_release": release,
            "os_type": "Linux",
        }
        # return {"os": data_dic}
        self.data["os"] = data_dic

    def get_cpu_info(self):
        """
        获取cpu信息
        :return:
        """
        cpu_count = 0
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.readlines()
        for line in cpu_info:
            if line.startswith('model name'):
                cpu_model = line.split(': ')[1].strip()
                cpu_count += 1

            elif line.startswith('cpu cores'):
                cpu_core_count = line.split(': ')[1].strip()
            elif line.startswith('vendor_id'):
                cpu_vendor = line.split(': ')[1].strip()
            else:
                pass

        data = {
            "cpu_count": cpu_count,
            "cpu_core_count": int(cpu_core_count),
            "cpu_model": cpu_model
        }

        # return {"cpu": data}
        self.data["cpu"] = data

    def get_ram_info(self):
        """
        获取内存信息
        :return:
        """
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.readlines()
        ram_data = {'mem_capacity': int(mem_info[0].split()[-2]) / 1024 ** 2}

        # return ram_data
        self.data["ram"] = ram_data

    def get_network_info(self):
        """
        获取网卡信息
        :return:
        """
        nic_list = []
        # nic_dict = {}
        network_info = psutil.net_if_addrs()
        for nic_name, nic_conf in network_info.items():
            if nic_name != 'lo':
                if len(nic_conf) > 1:
                    nic_addr = nic_conf[0][1]
                    nic_mask = nic_conf[0][2]
                    nic_mac = nic_conf[1][1]
                    nic_list.append({"ip_addr": nic_addr, "name": nic_name, "mac": nic_mac, "net_mask": nic_mask})
                    # nic_dict[nic_addr] = {"name": nic_name, "mac": nic_mac, "net_mask": nic_mask}
        # return {"network": nic_dict}
        # self.data["network"] = nic_dict
        self.data["network"] = nic_list

    def get_storage_info(self):
        """
        获取存储信息。
        :return:
        """
        # disk_dict = {}
        disk_list = []
        disk_infos = psutil.disk_partitions(all=True)
        for disk_info in disk_infos:
            device_name = disk_info[0]
            device_mount = disk_info[1]
            device_fstype = disk_info[2]

            re_name = re.match(r'w\+fs', device_name)
            re_mount = re.match(r'^/(data+|)$', device_mount)
            if not re_name and re_mount:
                print(device_name, device_mount, device_fstype)
                # disk_dict[device_name] = {"mout_point": device_mount, "fs_type": device_fstype}
                disk_list.append({"disk_name": device_name, "mout_point": device_mount, "fs_type": device_fstype})
        # self.data["storage"] = disk_dict
        self.data["storage"] = disk_list


if __name__ == "__main__":
    # 收集信息功能测试
    metric_cllector = SysMetrics()
    metric_cllector.collector()
    print(metric_cllector.data)
