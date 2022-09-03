# 知网爬虫（专利、论文、成果）

## 〇、归档说明

已经开了个新坑，[知网专利爬虫](https://github.com/aFlyBird0/CnkiPatentSpider) 实现更简单，代码更易读。功能可能稍逊色些，但更不容易出错，更可控。

挺久之前写的代码了，再回过来看，感觉写得太烂了。所以修复屎山的最好的办法是——重新写一个。

原先使用了 scrapy，考虑地太理想了。想着各种一键化走完全流程、各种自动化的控制。但犯的最大的错误，一个是代码因为需求迭代太乱了，一个是错误记录应该只读不删，即应该记录下所有的错误的日期和学科分类代码，就算下次重新爬取了错误的内容，也不能删掉，而应该简单打个标签。

新的流程更偏向实践、易维护，以及结合我最近在学的云原生，把最后一步做成真正的分布式的爬虫。

## 一、整体介绍

[Scrapy知网爬虫（一）整体理论篇 | Bird's Blog](https://blog.aflybird.cn/2021/07/Scrapy%E7%9F%A5%E7%BD%91%E7%88%AC%E8%99%AB%EF%BC%88%E4%B8%80%EF%BC%89%E6%95%B4%E4%BD%93%E7%90%86%E8%AE%BA%E7%AF%87/)

## 二、注意
1. 这是21年4月写的爬虫，目前应该处于基本可用的状态。因为业务需求一直在变动，所以写得很乱。有些地方可能需要手动改一下。（居然有人认真看和star，我有空尽量规范、测试一下代码。一年后再看以前自己写的代码，想喷死自己)
2. 专利在2021年5月左右亲测可爬，爬百万千万数据没问题。论文、项目部分可能部分字段的解析没写完，建议先跑跑看，有问题的话修改 `CnkiSpider/spiders/paperAchSpider.py` 中的 `html` 解析部分
3. 注意 `/dataSrc` 下的学科分类代码文件，不全，我只选取了理工科部分
4. 专利：考虑到法律状态会更新，所以建议在用到的时候实时请求知网，故此字段暂未爬取。有空会附上这段爬虫代码。
## 三、运行
前置工作：建立数据库，默认数据库名为 `ZhiWangSpider`，此配置项在 `/CkniSpider/settings` 文件夹下的配置文件中的 `MYSQL_DATABASE` 中。  

### 3.1 服务器运行模式
#### 3.1.1 模式介绍
此模式是部署在服务器上，设定好任务，然后单机跑
#### 3.1.2 如何设定爬取任务
先运行一次项目，程序会自动生成 `status`、`errorCode`、`errorLink` 表（也可在 `/sql` 目录下找到这三个建表文件手动创建）  
程序会报错，提示 " `status` 表中缺少 `type` 为 `patent` （也可能是 `paper`）的数据条，请手动插入"  
这时候，在数据库的 `status` 表中插入一条记录，设置以下几项  
* `type` ：必填。设置为 `patent` 就是爬专利， `paperAch` 是论文和项目
* `curDate`：必填。爬虫任务的起始日期。（爬虫会在运行时将此字段作为当前在爬日期，并不断更新此字段）  
* `endDate`：选填。爬虫任务的结束日期。可不填，默认昨天。
* `curCode`：不建议填。当前爬的学科分类信息，会默认从 A001_1 开始。
* `status`：不填。记录爬虫最后一次获取任务的时间，用来简单显示爬虫运行情况（是正在跑、还是跑完了、还是崩了）
> 注，因为多线程原因，当 `status` 显示为 `finish` 的时候，其实只是把设定的任务读取完毕，可能还没爬完，建议等一会。
#### 3.1.3 配置文件说明
此模式的配置都在 `/CnkiSpider/settings` 文件夹下，包括 redis 数据库号和 mysql 表名
*修改 scrapy.cfg 中的 default 字段即可切换配置*
dev_settings.py、settings.py 都是服务器运行模式，可以改改数据库字段和其他设置

### 3.2 分发模式
#### 3.2.1 模式介绍
此模式是打包成 exe , 可分布式独立运行。
#### 3.2.2 如何设定爬取任务
每个子爬虫的任务是独立的，所以不在 `settings` 文件夹下，在 `/config.cfg` 配置文件中，详见下文  
#### 3.2.3 配置文件说明
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

#### 3.2.4 如何运行：
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
