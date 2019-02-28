from django.db import models


class Asset(models.Model):
    asset_type_choice = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
        ('securitydevice', '安全设备'),
        ('IDC', '机房'),
        ('software', '软件资产'),
    )

    asset_status = (
        (0, '在线'),
        (1, '下线'),
        (2, '未知'),
        (3, '故障'),
        (4, '备用'),
    )

    type = models.SmallIntegerField(choices=asset_type_choice, default='server', verbose_name="资产类型")
    name = models.TextField(verbose_name="资产名称", unique=True, max_length=64)
    sn = models.TextField(verbose_name="资产编号", null=True, blank=True, default=None, max_length=64)
    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, on_delete=models.SET_NULL, default=None)
    model = models.TextField(null=True, blank=True, verbose_name='资产型号', default=None, max_length=64)
    ip_addr = models.TextField(null=True, blank=True, verbose_name="资产管理IP", default=None, max_length=64)
    mac_addr = models.TextField(null=True, blank=True, verbose_name="资产MAC地址", default=None, max_length=64)
    location = models.TextField(null=True, blank=True, verbose_name="所在机房", default=None, max_length=64)
    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name='设备状态')
    expire_date = models.DateField(null=True, blank=True, verbose_name='过保日期', default=None)
    memo = models.TextField(null=True, blank=True, verbose_name='备注', default=None, max_length=256)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='批准日期')
    m_time = models.DateTimeField(auto_now=True, verbose_name='更新日期')

    def __str__(self):
        return '<%s>  %s' % (self.get_type_display(), self.name)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"
        ordering = ['expire_date']


class Server(models.Model):
    """服务器设备"""
    virtual_type_choice = (
        ('docker', '容器'),
        ('vhost', '虚拟机'),
        ('hardware', '物理机'),
    )

    created_by_choice = (
        ('auto', '自动添加'),
        ('manual', '手工录入'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # 非常关键的一对一关联！
    created_by = models.CharField(choices=created_by_choice, max_length=32, default='auto', verbose_name="添加方式")

    virtual_type = models.SmallIntegerField(choices=virtual_type_choice, verbose_name="主机类型", default='vhost')
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server',
                                  blank=True, null=True, verbose_name="宿主机", on_delete=models.SET_NULL, default='localhost')  # 虚拟机专用字段
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name='服务器型号', default=None)

    def __str__(self):
        return '%s' % self.asset.name

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"


class SecurityDevice(models.Model):
    """安全设备"""
    sub_asset_type_choice = (
        (0, '防火墙'),
        (1, '入侵检测设备'),
        (2, '网关'),
        (4, '审计系统'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="安全设备类型")

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + " id:%s" % self.id

    class Meta:
        verbose_name = '安全设备'
        verbose_name_plural = "安全设备"


class StorageDevice(models.Model):
    """存储设备"""
    sub_asset_type_choice = (
        (0, '磁盘阵列'),
        (1, 'Nas存储'),
        (2, '阿里云OSS'),
        (4, 'aws存储对象'),
        (5, '本地存储'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="存储设备类型")
    total_volume = models.BigIntegerField(verbose_name="存储总量",default=50)
    available_volume = models.BigIntegerField(verbose_name="存储可用容量", default=50)
    fs_type = models.TextField(verbose_name="文件系统", default='ext4', max_length=128)
    mount_point = models.TextField(verbose_name="挂载点", default='/', max_length=128)

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + " id:%s" % self.id

    class Meta:
        verbose_name = '存储设备'
        verbose_name_plural = "存储设备"


class NetworkDevice(models.Model):
    """网络设备"""
    sub_asset_type_choice = (
        (0, '路由器'),
        (1, '交换机'),
        (2, '负载均衡'),
        (4, 'VPN设备'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="网络设备类型")

    vlan_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="VLanIP", default=None)
    intranet_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="内网IP", default=None)

    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="网络设备型号", default='HUAWEI S5200')
    firmware = models.CharField(max_length=128, blank=True, null=True, verbose_name="设备固件版本", default=None)
    port_num = models.SmallIntegerField(null=True, blank=True, verbose_name="端口个数", default=20)
    device_detail = models.TextField(null=True, blank=True, verbose_name="详细配置", default=None, max_length=128)

    def __str__(self):
        return '%s--%s--%s <ip:%s>' % (self.asset.name, self.get_sub_asset_type_display(), self.model, self.intranet_ip)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"


class Software(models.Model):
    """
    只保存付费购买的软件
    """
    sub_asset_type_choice = (
        (0, '操作系统'),
        (1, '办公\开发软件'),
        (2, '业务软件'),
        (3, '安全审计软件'),
        (4, '杀毒软件')
    )

    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="软件类型")
    license_num = models.IntegerField(default=1, verbose_name="授权数量")
    version = models.CharField(max_length=64, unique=True, help_text='例如: CentOS release 6.7 (Final)',
                               verbose_name='软件/系统版本', default=None)

    def __str__(self):
        return '%s--%s' % (self.get_sub_asset_type_display(), self.version)

    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = "软件/系统"


class IDC(models.Model):
    """机房"""
    name = models.CharField(max_length=64, unique=True, verbose_name="机房名称")
    area = models.CharField(max_length=64, unique=True, verbose_name="可用区", default='IDC')
    memo = models.CharField(max_length=128, blank=True, null=True, verbose_name='备注', default='备注')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"


class Manufacturer(models.Model):
    """厂商"""

    name = models.CharField('厂商名称', max_length=64, unique=True)
    telephone = models.CharField('支持电话', max_length=30, blank=True, null=True, default=None)
    memo = models.CharField('备注', max_length=128, blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = "厂商"


class OS(models.Model):
    """os 配置"""
    server = models.OneToOneField('Asset', on_delete=models.CASCADE)
    os_model = models.CharField(max_length=64, verbose_name="操作系统类型", default='Linux')
    os_release = models.CharField(max_length=64, verbose_name="操作系统发行版", default='centos')
    os_version = models.CharField(max_length=128, blank=True, null=True, verbose_name='操作系统版本', default='7.3')
    hostname = models.CharField(max_length=128, blank=True, null=True, verbose_name='主机名', default='localhost')

    def __str__(self):
        return self.server.name + ":   " + self.hostname + ":   " + self.os_release + ' ' + self.os_version

    class Meta:
        verbose_name = 'OS'
        verbose_name_plural = "OS"


class CPU(models.Model):
    """cpu 配置"""
    server = models.OneToOneField('Asset', on_delete=models.CASCADE)
    cpu_model = models.CharField(max_length=64, verbose_name="CPU型号", default='Intel(R) Core(TM) i5-7360U CPU @ 2.30GHz')
    cpu_num = models.IntegerField(verbose_name="CPU个数", default=2)
    cpu_cores = models.IntegerField(blank=True, null=True, verbose_name='CPU核数', default=2)

    def __str__(self):
        # return self.server.name + ":   " + self.cpu_model
        return self.server.name + ":   " + str(self.cpu_num) + ":   " + str(self.cpu_cores)

    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = "CPU"


class Mem(models.Model):
    """内存配置"""
    server = models.ForeignKey('Asset', on_delete=models.CASCADE)
    mem_sn = models.CharField('SN号', max_length=128, blank=True, null=True)
    mem_model = models.CharField('内存型号', max_length=128, blank=True, null=True)
    mem_manufacturer = models.CharField('内存制造商', max_length=128, blank=True, null=True)
    mem_slot = models.IntegerField('插槽', blank=True, null=True, default=0)
    mem_capacity = models.IntegerField('内存容量(单位：MB)', default=2048)

    def __str__(self):
        # return '%s: %s: %s: %s' % (self.server.name, self.model, self.slot, self.capacity)
        return self.server.name + ":   " + str(self.mem_capacity)

    class Meta:
        verbose_name = '内存'
        verbose_name_plural = "内存"
        unique_together = ('server', 'mem_slot')  # 同一资产下的内存，根据插槽的不同，必须唯一


class Disk(models.Model):
    """本地存储配置"""
    server = models.ForeignKey('Asset', on_delete=models.CASCADE)
    disk_sn = models.CharField('硬盘SN号', max_length=128, blank=True, null=True, default=None)
    disk_slot = models.IntegerField('所在插槽位', blank=True, null=True, default=None)
    disk_model = models.CharField('磁盘型号', max_length=128, blank=True, null=True, default=None)
    disk_manufacturer = models.CharField('磁盘制造商', max_length=128, blank=True, null=True, default=None)
    disk_name = models.CharField('磁盘名称', max_length=128, unique=True, default='/dev/sda')
    disk_mount = models.CharField(max_length=256, verbose_name="挂载点", default='/')
    disk_fstype = models.CharField(max_length=256, verbose_name="挂载点", default='overlay')
    disk_capacity = models.BigIntegerField(verbose_name="硬盘容量(单位：GB)", default=50)

    def __str__(self):
        return '%s:  %s:  %s:  %sGB' % (self.server.name, self.disk_name, self.disk_mount, self.disk_capacity)

    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = "硬盘"
        unique_together = ('server', 'disk_name', 'disk_mount')


class Adapter(models.Model):
    """外设组件，如HBA卡、网卡"""

    server = models.ForeignKey('Asset', on_delete=models.CASCADE)  # 注意要用外键
    name = models.CharField('外设名称', max_length=64, blank=True, null=True, default='eth0')
    model = models.CharField('外设型号', max_length=128, blank=True, null=True, default=None)
    mac = models.CharField('MAC地址', max_length=64, default=None)  # 虚拟机有可能会出现同样的mac地址
    ip_addr = models.GenericIPAddressField('IP地址', default=None)
    net_mask = models.CharField('掩码', max_length=64, blank=True, null=True, default='255.255.255.0')
    bonding = models.CharField('绑定地址', max_length=64, blank=True, null=True, default=None)

    def __str__(self):
        return '%s: %s:  %s:  %s' % (self.server.name, self.ip_addr, self.net_mask, self.mac)

    class Meta:
        verbose_name = '外设'
        verbose_name_plural = "外设"
        unique_together = ('server', 'ip_addr', 'mac')  # 资产、型号和mac必须联合唯一。防止虚拟机中的特殊情况发生错误。


class User(models.Model):
    work_id = models.TextField(verbose_name='工号', max_length=128)
    Email = models.EmailField(verbose_name='公司邮箱')
    expire_date = models.DateField(verbose_name='过期日期')


class EventLog(models.Model):
    """
    日志.
    在关联对象被删除的时候，不能一并删除，需保留日志。
    因此，on_delete=models.SET_NULL
    """

    name = models.CharField('事件名称', max_length=128)
    event_type_choice = (
        (0, '其它'),
        (1, '硬件变更'),
        (2, '新增配件'),
        (3, '设备下线'),
        (4, '设备上线'),
        (5, '定期维护'),
        (6, '业务上线\更新\变更'),
    )
    asset = models.ForeignKey('Asset', blank=True, null=True, on_delete=models.SET_NULL)  # 当资产审批成功时有这项数据
    new_asset = models.ForeignKey('NewAssetApprovalZone', blank=True, null=True, on_delete=models.SET_NULL)  # 当资产审批失败时有这项数据
    event_type = models.SmallIntegerField('事件类型', choices=event_type_choice, default=4)
    component = models.CharField('事件子项', max_length=256, blank=True, null=True, default=None)
    detail = models.TextField('事件详情', default=None, max_length=128)
    date = models.DateTimeField('事件时间', auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name='事件执行人', on_delete=models.SET_NULL)  # 自动更新资产数据时没有执行人
    memo = models.TextField('备注', blank=True, null=True ,default=None, max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '事件纪录'
        verbose_name_plural = "事件纪录"


class NewAssetApprovalZone(models.Model):
    """新资产待审批区"""
    #  id = models.AutoField('资产编号')
    sn = models.CharField('资产SN号', max_length=128, blank=True, null=True, unique=False, default=None)  # 此字段必填
    name = models.CharField('资产名称', max_length=128, unique=True, default='待审批')  # 此字段必填
    asset_type_choice = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
        ('securitydevice', '安全设备'),
        ('IDC', '机房'),
        ('software', '软件资产'),
    )
    asset_status = (
        (0, '在线'),
        (1, '下线'),
        (2, '未知'),
        (3, '故障'),
        (4, '备用'),
    )
    asset_type = models.CharField(choices=asset_type_choice, default='server', max_length=64, blank=True, null=True,
                                  verbose_name='资产类型')

    manufacturer = models.CharField(max_length=128, blank=True, null=True, verbose_name='生产厂商')
    model = models.CharField(max_length=128, blank=True, null=True, verbose_name='型号')
    location = models.TextField(null=True, blank=True, verbose_name="所在机房", max_length=128)
    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name='设备状态')
    ram = models.OneToOneField('Mem', on_delete=models.SET, blank=True, null=True)
    # ram_size = models.PositiveIntegerField(blank=True, null=True, verbose_name='内存大小')
    cpu = models.OneToOneField('CPU', on_delete=models.SET, blank=True, null=True)
    # cpu_model = models.CharField(max_length=128, blank=True, null=True, verbose_name='CPU型号')
    # cpu_count = models.PositiveSmallIntegerField(blank=True, null=True)
    # cpu_core_count = models.PositiveSmallIntegerField(blank=True, null=True)
    os = models.ManyToManyField('OS', blank=True, default=OS)
    # os_distribution = models.CharField(max_length=64, blank=True, null=True)
    # os_type = models.CharField(max_length=64, blank=True, null=True)
    # os_release = models.CharField(max_length=64, blank=True, null=True)
    network = models.ManyToManyField('Adapter', blank=True, default=Adapter)
    # network_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="网卡名称")
    # network_ip = models.CharField(max_length=256, blank=True, null=True, verbose_name="网卡IP地址")
    # network_mac = models.CharField(max_length=64, blank=True, null=True, verbose_name="网卡MAC地址")
    # network_mask = models.CharField(max_length=64, blank=True, null=True, verbose_name="网卡掩码")
    disk = models.ManyToManyField('StorageDevice', blank=True, default=StorageDevice)
    # disk_mount = models.CharField(max_length=256, blank=True, null=True, verbose_name="挂载点")
    # disk_fstype = models.CharField(max_length=256, blank=True, null=True, verbose_name="文件系统类型")
    # disk_capacity = models.CharField(max_length=64, blank=True, null=True, verbose_name="硬盘容量(单位：GB)")

    data = models.TextField('资产数据', max_length=256)  # 此字段必填

    c_time = models.DateTimeField('汇报日期', auto_now_add=True)
    m_time = models.DateTimeField('数据更新日期', auto_now=True)
    approved = models.BooleanField('是否批准', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = "新上线待批准资产"
        ordering = ['-c_time']


