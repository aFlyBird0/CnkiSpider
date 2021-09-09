# 知网爬虫（专利、论文、成果）

## 整体介绍

[Scrapy知网爬虫（一）整体理论篇 | Bird's Blog](https://bird.blog.tcualhp.cn/2021/07/Scrapy%E7%9F%A5%E7%BD%91%E7%88%AC%E8%99%AB%EF%BC%88%E4%B8%80%EF%BC%89%E6%95%B4%E4%BD%93%E7%90%86%E8%AE%BA%E7%AF%87/)

## 开发记录
### 数据库说明
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