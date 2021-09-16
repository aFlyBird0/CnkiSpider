# 知网爬虫（专利、论文、成果）

## 整体介绍

[Scrapy知网爬虫（一）整体理论篇 | Bird's Blog](https://bird.blog.tcualhp.cn/2021/07/Scrapy%E7%9F%A5%E7%BD%91%E7%88%AC%E8%99%AB%EF%BC%88%E4%B8%80%EF%BC%89%E6%95%B4%E4%BD%93%E7%90%86%E8%AE%BA%E7%AF%87/)

## 注意
1. 专利在2021年5月左右亲测可爬，爬百万千万数据没问题论文、项目部分还没写好，不过二者的基础依赖大多一样，主要就是改 `CnkiSpider/spiders/paperAchSpider.py` 中的 `html` 解析部分  
2. 之前是在分发模式跑的，确保可用；服务器模式一段时间没用了，可能配置需要改一点点，比如中间件的开启关闭，网络请求头一类的，我后面会再测试
3. 注意 `/dataSrc` 下的学科分类代码文件，不全，我只选取了理工科部分
## 运行
前置工作：建立数据库，默认数据库名为 `ZhiWangSpider`，此配置项在 `/CkniSpider/settings` 文件夹下的配置文件中的 `MYSQL_DATABASE` 中。  

### 服务器运行模式
#### 模式介绍
此模式是部署在服务器上，设定好任务，然后单机跑
### 如何设定爬取任务
先运行一次项目，程序会自动生成 `status`、`errorCode`、`errorLink` 表（也可在 `/sql` 目录下找到这三个建表文件手动创建）  
程序会报错，提示 " `status` 表中缺少 `type` 为 `patent` （也可能是 `paper`）的数据条，请手动插入"  
这时候，在数据库的 `status` 表中插入一条记录，设置以下几项  
* `type` ：必填。设置为 `patent` 就是爬专利， `paperAch` 是论文和项目
* `curDate`：必填。爬虫任务的起始日期。（爬虫会在运行时将此字段作为当前在爬日期，并不断更新此字段）  
* `endDate`：选填。爬虫任务的结束日期。可不填，默认昨天。
* `curCode`：不建议填。当前爬的学科分类信息，会默认从 A001_1 开始。
* `status`：不填。记录爬虫最后一次获取任务的时间，用来简单显示爬虫运行情况（是正在跑、还是跑完了、还是崩了）
#### 配置文件说明
此模式的配置都在 `/CnkiSpider/settings` 文件夹下，包括 redis 数据库号和 mysql 表名
*修改 scrapy.cfg 中的 default 字段即可切换配置*
dev_settings.py、settings.py 都是服务器运行模式，可以改改数据库字段和其他设置

### 分发模式
#### 模式介绍
此模式是打包成 exe , 可分布式独立运行。
### 如何设定爬取任务
每个子爬虫的任务是独立的，所以不在 `settings` 文件夹下，在 `/config.cfg` 配置文件中，详见下文  
#### 配置文件说明
此模式，每个子爬虫拥有不同的 redis 数据库号 与 mysql 表名（每个表前缀一样，利用不同的数据库号区分）
例如，子爬虫1连了 redis 数据库号 `1`，对应的 mysql 数据表名是 `errorCode1`、`errorLink1`、`status1`。（分发模式这三个表会自动建）
所以将这个数字配置独立到了 `/config.cfg` 中  

`/config.cfg` 如下：其中， `no` 同时充当了爬虫序号、redis 与 mysql 数据库（表）号，`start` 是子爬虫任务开始日期，`end` 是结束  
```config
[spider]
type=patent
start=2020-07-01
end=2020-07-31
[database]
no=12

```

其他配置文件说明：  
`/CnkiSpider/settings/settins_distribute.py` 是适用于分发模式的配置文件  
*修改 scrapy.cfg 中的 default 字段即可切换配置*  

#### 如何运行：
1. 清除旧的打包文件：删除根目录下的 dist 文件夹
2. 生成spec文件，具体如何利用pycharm生成此文件请自行查阅资料，关键词 "pyinstaller, pycharm, external tools"，我目前使用的打包命令（如果不增加文件仅修改内容可跳过此步，直接使用我已经生成的CnkiSpiderExec.py）
```shell script
-w -i cnki.ico $FileNameWithoutExtension$.py
```
![spec生成: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/1624277583.jpg)
3. 修改 spec 文件。找到 `datas=[]` 那行，改成
```shell script
datas=[('dataSrc','dataSrc'), ('./scrapy.cfg', '.'), ('./config.cfg', '.'), ('CnkiSpider/spiders', 'CnkiSpider/spiders'), ('log','log')],
```
4. 利用 spec 文件生成 exe（打包）,
![利用spec生成exe: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/image-20210621201507728.png)
5. 拷贝在根目录下生成的 dist 文件夹中的 CnkiSpiderExec 文件夹
6. 在拷贝后的 CnkiSpiderExec 文件夹根目录下建立 log 文件夹
7. 修改拷贝的文件夹根目录下的 `config.cfg`，设置爬取类型、开始结束日期、数据库编号（既是redis的数据库号也是mysql的表号）
8. 运行 CnkiSpiderExec.exe

## 开发记录（给我自己看的）
### 数据库说明
** 老数据库已经换密码了，隧道也关了，请把 mysql 与 redis 配置换成自己的 **
* redis
    * 目前是用的10.1.13.142的redis，原本内网访问，搭了个隧道代理，部分配置修改成了外网访问的ip和端口
    * todo 将内网外网配置文件合并，写在配置中，启动的时候进行选择（服务器运行模式无需此功能，因为肯定是用学校的机器跑，只有在分发模式中才需要）
* mysql
    * 目前用的是自己的腾讯云服务器，2022年2月到期。
    * todo 换成实验室的机器上的mysql
### 如何运行
#### 服务器运行模式
配置文件说明（/CnkiSpider/settings文件夹）：  
运行命令（进入项目根目录执行）：
1. 爬取专利
```shell script
nohup python3 -u runPatent.py > runPatent.log 2>&1 &
```
2. 爬取论文（期刊表中的期刊、博硕）、成果
```shell script
nohup python3 -u runPaperAch.py > runPaperAch.log 2>&1 &
```
#### 分发模式（打包成 exe）
配置文件说明（/CnkiSpider/settings文件夹）：  

*注：此模式的redis数据库号和mysql表名都写在config.cfg配置文件中,即每个分发任务拥有单独的redis数据库号和mysql数据表*  
*修改 scrapy.cfg 中的 default 字段即可切换配置*

* settings_distribute.py 分发模式内网配置
* settings_distribute_142out.py 分发模式外网配置

如何运行：
1. 清除旧的打包文件：删除根目录下的 dist 文件夹
2. 生成spec文件，具体如何利用pycharm生成此文件请自行查阅资料，关键词 "pyinstaller, pycharm, external tools"，我目前使用的打包命令（如果不增加文件仅修改内容可跳过此步，直接使用我已经生成的CnkiSpiderExec.py）
```shell script
-w -i cnki.ico $FileNameWithoutExtension$.py
```
![spec生成: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/1624277583.jpg)
3. 修改 spec 文件。找到 `datas=[]` 那行，改成
```shell script
datas=[('dataSrc','dataSrc'), ('./scrapy.cfg', '.'), ('./config.cfg', '.'), ('CnkiSpider/spiders', 'CnkiSpider/spiders'), ('log','log')],
```
4. 利用 spec 文件生成 exe（打包）,
![利用spec生成exe: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/image-20210621201507728.png)
5. 拷贝在根目录下生成的 dist 文件夹中的 CnkiSpiderExec 文件夹
6. 在拷贝后的 CnkiSpiderExec 文件夹根目录下建立 log 文件夹
7. 修改拷贝的文件夹根目录下的 `config.cfg`，设置爬取类型、开始结束日期、数据库编号（既是redis的数据库号也是mysql的表号）
8. 运行 CnkiSpiderExec.exe

## 开发记录（给我自己看的）
### 数据库说明
** 老数据库已经换密码了，隧道也关了，请把 mysql 与 redis 配置换成自己的 **
* redis
    * 目前是用的10.1.13.142的redis，原本内网访问，搭了个隧道代理，部分配置修改成了外网访问的ip和端口
    * todo 将内网外网配置文件合并，写在配置中，启动的时候进行选择（服务器运行模式无需此功能，因为肯定是用学校的机器跑，只有在分发模式中才需要）
* mysql
    * 目前用的是自己的腾讯云服务器，2022年2月到期。
    * todo 换成实验室的机器上的mysql
### 如何运行
#### 服务器运行模式
配置文件说明（/CnkiSpider/settings文件夹）：  

*注：此模式的redis数据库号和mysql表名都写在settings配置文件中*  
*修改 scrapy.cfg 中的 default 字段即可切换配置*
* binjiang_settings.py 主要是外网访问mysql和redis
* dev_settings.py 是之前开发用的配置，redis的数据库号不太一样，内网
* product_settings.py 原设置为上线时的最终运行配置，现在弃用状态
* settings.py 实际上的上线配置  

运行命令（进入项目根目录执行）：
1. 爬取专利
```shell script
nohup python3 -u runPatent.py > runPatent.log 2>&1 &
```
2. 爬取论文（期刊表中的期刊、博硕）、成果
```shell script
nohup python3 -u runPaperAch.py > runPaperAch.log 2>&1 &
```
#### 分发模式（打包）
配置文件说明（/CnkiSpider/settings文件夹）：  

*注：此模式的redis数据库号和mysql表名都写在config.cfg配置文件中,即每个分发任务拥有单独的redis数据库号和mysql数据表*  
*修改 scrapy.cfg 中的 default 字段即可切换配置*

* settings_distribute.py 分发模式内网配置
* settings_distribute_142out.py 分发模式外网配置

如何运行：
1. 清除旧的打包文件：删除根目录下的 dist 文件夹
2. 生成spec文件，具体如何利用pycharm生成此文件请自行查阅资料，关键词 "pyinstaller, pycharm, external tools"，我目前使用的打包命令（如果不增加文件仅修改内容可跳过此步，直接使用我已经生成的CnkiSpiderExec.py）
```shell script
-w -i cnki.ico $FileNameWithoutExtension$.py
```
![spec生成: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/1624277583.jpg)
3. 修改 spec 文件。找到 `datas=[]` 那行，改成
```shell script
datas=[('dataSrc','dataSrc'), ('./scrapy.cfg', '.'), ('./config.cfg', '.'), ('CnkiSpider/spiders', 'CnkiSpider/spiders'), ('log','log')],
```
4. 利用 spec 文件生成 exe（打包）,
![利用spec生成exe: pycharm pyinstaller external tools 配置示意](https://tcualhp-notes.oss-cn-hangzhou.aliyuncs.com/img/image-20210621201507728.png)
5. 拷贝在根目录下生成的 dist 文件夹中的 CnkiSpiderExec 文件夹
6. 在拷贝后的 CnkiSpiderExec 文件夹根目录下建立 log 文件夹
7. 修改拷贝的文件夹根目录下的 `config.cfg`，设置爬取类型、开始结束日期、数据库编号（既是redis的数据库号也是mysql的表号）
8. 运行 CnkiSpiderExec.exe