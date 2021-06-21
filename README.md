# 知网爬虫（专利、论文、成果）

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
* settings_distribute.py 分发模式内网配置
* settings_distribute_142out.py 分发模式外网配置