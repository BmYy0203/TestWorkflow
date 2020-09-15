# SDKAutoTest 中 Airflow和管理平台前端的对接文档



## 1. 综述

管理平台通过Airflow的[RESTful API](https://airflow.apache.org/docs/stable/rest-api-ref)，将测试参数传至Airflow端的某个测试计划（DAG，即模板的python脚本）中，脚本解析传入的参数并由此配置测试环境、创建RunnerConfig并实例化各个Operator，驱动测试计划执行。

基本流程是：

1. 管理平台选择测试计划类型，配置市场权限，站点信息，测试用例参数等内容，通过RESTful API传给Airflow
2. Airflow中对应的DAG接收到参数`conf`，通过解析参数，配置RunnerConfig以及ReleaseOperator, RunnerOperator和CompareOperator等Operator的参数。
3. Airflow启动该参数下的一次执行。

具体可见[ios_compare2的一次执行](http://221.228.66.83:30690/admin/airflow/log?task_id=ios_cmp_b&dag_id=ios_compare2&execution_date=2020-09-14T01%3A57%3A57%2B00%3A00&format=json)的日志文件。日志里实际上打印出了接收到了所有参数内容。



## 2. 测试计划模板

目前测试计划模板有如下几种类型（先看通用测试计划模板v1.0.docx）

实际应用时前端便是执行如下命令

```bash
curl -X POST \
  http://<AirflowIP:Port>/api/experimental/dags/<DAG_ID>/dag_runs \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{"conf": <Your Config>  }'
```

样例如下

```json
'conf': {
            'collectionName': 'Test_Android_quote_20200316',
            'Level': '2',
            'CffLevel':'1',
            'DceLevel':'2',
            'CzceLevel':'2',
            'FeLevel':'2',
            'GILevel':'2',
            'ShfeLevel':'2',
            'IneLevel':'2',
            'HKPerms': ['hk10'],
            'roundIntervalSec': '3',
            'tag': [['release-20200103-0.0.3', '53fcc717d954e01d88bc9bd70eaab9ac9a0acb67']],
            'run_times': '1',
            'quote_detail': '1',
            "AirflowMethod": [
                {
                    'testcaseID': 'L2TICKDETAILV2_1',
                    'paramStrs': [
                        {
                            'CODE': '000100.sz',
                            'SUBTYPE': '1001'
                        },
                        {
                            'CODE': '000078.sz',
                            'SUBTYPE': '1001'
                        },
                        {
                            'CODE': '002429.sz',
                            'SUBTYPE': '1001'
                        }
                    ]}
            ],
            'server': [
                {
                    'serverSites1': [
                        ["sh", "http://114.80.155.134:22016","tcp://114.80.155.134:22017"],
                        ["tcpsh", "http://114.80.155.134:22017"],
                    ]
                },
                {
                    'serverSites2': [
                        ["sh", "http://114.80.155.134:22016"],
                        ["shl2", "http://114.80.155.62:22016"],
                    ]
                }
            ]
}
```



## 3. 模板与测试方法

测试计划的模板位于`TestWorkflow/templates`

对应的测试函数位于`TestWorkflow/unnittest/templates`

测试函数实际上是通过封装的`AirflowRestClient`（位于`TestWorkflow/plugins/utils/restful_client.py`）将标准参数传递给Airflow上某个模板并观察执行结果。



## 4. 注意事项与常见问题

- 模板要放在`/dags/`目录下才会被Airflow的Scheduler扫描到
- 模板第一次执行或者传参出错时，需要用真正的参数而非传入的参数去执行，否则会提示找不到这个DAG
  - 其实这个传参的方法是有些“糟糕的方法”。根据Airflow的机制，Scheduler是去扫描任务的，在扫描的过程中就会检查python文件是否符合规范。然而由于python的无类型以及各种看起来很方便的性质，导致一个变量可能是空值，未运行时也根本不知道它是list,dict还是什么东西。因此第一次执行时得告诉airflow这里究竟应该是什么。所以第一次要用真正的参数去手动执行。
  - 糟糕的第二点就是，既然能骗过Airflow的调度器，这说明airflow本身是有一套缓存的，而如果使用者错误地传入了异常的参数，会导致每次检查缓存时都异常，此时不仅看不到日志，而且也无法使用API去触发执行，因为此时Airflow已经找不到，或者无法识别这个DAG了。所以传参出错时要用真正的参数去手动执行。



## TODO

优先级从上到下由高到低

- [ ] 修复VSCode在线编辑器中`/dags`有关参数未定义即引用的serverSites1的bug

  - [ ] android_compare.py
  - [ ] android_compare1.py
  - [ ] android_compare2.py

- [ ] 根据`templates/ios_sort.py`修复VSCode在线编辑器中`/dags/ios_sort.py`被设置为固定参数的bug

- [ ] 修复模板中多个releaseOperator时xcom_release_key的对应关系

- [ ] 尝试把各个模板中的`initRunnerConfig`重构整合，提高复用性和可维护性

  - 关于注意事项提到的问题，这里我个人觉得可以参考[这个](https://github.com/brianfrankcooper/YCSB/blob/master/core/src/main/java/site/ycsb/workloads/CoreWorkload.java/#L394:L418)的写法，把默认值分开。参数没有提供就用默认值。如果是错误参数，就捕获异常，并且设计一套机制使得Scheduler依然可以检测到这个任务，并告知使用者该次传参出了问题。

  