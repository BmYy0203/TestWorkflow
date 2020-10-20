import json

import airflow
from airflow import AirflowException
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from operators.data_compare_operator import DataCompareOperator
from protos_gen.config_pb2 import RunnerConfig, TestcaseConfig, Site
from operators.android_runner_operator import AndroidRunnerOperator
from operators.android_release_operator import AndroidReleaseOperator
from sqlalchemy import Column, PickleType
from utils import default_conf

def initRunnerConfig(conf):
    # 市场权限
    CffLevel_tmp = conf.get('CffLevel')
    if CffLevel_tmp is not None:
        print('Get Param CffLevel:', CffLevel_tmp)
    else:
        CffLevel_tmp = "1"
        print('Not Get Param CffLevel:', CffLevel_tmp)
    DceLevel_tmp = conf.get('DceLevel')
    if DceLevel_tmp is not None:
        print('Get Param DceLevel:', DceLevel_tmp)
    else:
        DceLevel_tmp = "2"
        print('Not Get Param DceLevel:', DceLevel_tmp)
    CzceLevel_tmp = conf.get('CzceLevel')
    if CzceLevel_tmp is not None:
        print('Get Param CzceLevel:', CzceLevel_tmp)
    else:
        CzceLevel_tmp = "2"
        print('Not Get Param CzceLevel:', CzceLevel_tmp)
    FeLevel_tmp = conf.get('FeLevel')
    if FeLevel_tmp is not None:
        print('Get Param FeLevel:', FeLevel_tmp)
    else:
        FeLevel_tmp = "2"
        print('Not Get Param FeLevel:', FeLevel_tmp)
    GILevel_tmp = conf.get('GILevel')
    if GILevel_tmp is not None:
        print('Get Param GILevel:', GILevel_tmp)
    else:
        GILevel_tmp = "2"
        print('Not Get Param GILevel:', GILevel_tmp)
    ShfeLevel_tmp = conf.get('ShfeLevel')
    if ShfeLevel_tmp is not None:
        print('Get Param ShfeLevel:', ShfeLevel_tmp)
    else:
        ShfeLevel_tmp = "2"
        print('Not Get Param ShfeLevel:', ShfeLevel_tmp)
    IneLevel_tmp = conf.get('IneLevel')
    if IneLevel_tmp is not None:
        print('Get Param IneLevel:', IneLevel_tmp)
    else:
        IneLevel_tmp = "2"
        print('Not Get Param IneLevel:', IneLevel_tmp)
        
    Level_tmp = conf.get('Level')
    if Level_tmp is not None:
        print('Get Param Level:', Level_tmp)
    else:
        Level_tmp = "2"
        print('Not Get Param Level:', Level_tmp)
    HKPerms_tmp = conf.get('HKPerms')
    if HKPerms_tmp is not None:
        HKPerms_tmp = list(HKPerms_tmp)
        print('Get Param HKPerms:', HKPerms_tmp)
    else:
        HKPerms_tmp=["hk10"]
        print('Not Get Param HKPerms:', HKPerms_tmp)
    collectionName_tmp = conf.get('collectionName')
    if collectionName_tmp is not None:
        print('Get Param collectionName:', collectionName_tmp)
    else:
        collectionName_tmp = "test_result"
        print('Not Get Param collectionName:', collectionName_tmp)
    #roundIntervalSec_tmp=3    
    roundIntervalSec_tmp = conf.get('roundIntervalSec')
    if roundIntervalSec_tmp is not None:
        roundIntervalSec_tmp = int(roundIntervalSec_tmp)
        print('Get Param roundIntervalSec:', roundIntervalSec_tmp)
    else:
        roundIntervalSec_tmp = 3
        print('Not Get Param roundIntervalSec:', roundIntervalSec_tmp)

    AirflowMethod = conf.get('AirflowMethod')
    if AirflowMethod is not None:
        AirflowMethod = list(AirflowMethod)
        print('Get Param AirflowMethod:',AirflowMethod)
    else:
        AirflowMethod=[
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
                    ]
                }
            ]
        print('Not Get Param AirflowMethod:',AirflowMethod)
    server=conf.get('server')
    if server is not None:
        server=list(server)
        print('Get Param server:', server)
    else:
        server=[
                    {
                        'serverSites1':[
                            ["sh", "http://114.80.155.134:22016"],
                            ["tcpsh", "http://114.80.155.134:22017"],
                            ["shl2", "http://114.80.155.62:22016"],
                        ]
                    },
                    {  
                        'serverSites2':[
                            ["sh", "http://114.80.155.134:22016"],
                            ["tcpsh", "http://114.80.155.134:22017"],
                            ["shl2", "http://114.80.155.62:22016"],
                        ]
                    }
                ]
        print('Not Get Param server:', server)
    serverSites1=[]
    serverSites2=[]
    for i in range(2):
        if i==0:
            serverSites1.extend(list(server[0].get('serverSites1')))
        if i==1:
            serverSites2.extend(list(server[1].get('serverSites2')))
            if len(serverSites2) == 0:
                serverSites2.extend(serverSites1)

    runner_conf_list = []
    for i in range(2):
        runner_conf = RunnerConfig()

        runner_conf.sdkConfig.appKeyIOS = 'VVW0Fno7BEZt1a/y6KLM36uj9qcjw7CAHDwWZKDlWDs='
        runner_conf.sdkConfig.appKeyAndroid = 'J6IPlk5AEU+2/Yi59rfYnsFQtdtOgAo9GAzysx8ciOM='
        runner_conf.sdkConfig.marketPerm.Level = Level_tmp
        runner_conf.sdkConfig.marketPerm.HKPerms.extend(HKPerms_tmp)
        # mongoDB位置，存储的数据库位置
        runner_conf.storeConfig.mongoUri = "mongodb://221.228.66.83:30617"
        runner_conf.storeConfig.dbName = "stockSdkTest"
        runner_conf.storeConfig.collectionName = collectionName_tmp        
        if i == 0:
            # 各个环境的站点配置
            for i in serverSites1:
                i = list(i)
                runner_conf.sdkConfig.serverSites[i[0]].CopyFrom(Site(ips=i[1:]))
            print('Get Param serverSites1:', serverSites1)
        else:
            # 生产站点
            for i in serverSites2:
                i = list(i)
                runner_conf.sdkConfig.serverSites[i[0]].CopyFrom(Site(ips=i[1:]))
            print('Get Param serverSites2:', serverSites2)
        # 测试样例
        # case_list = []
        for case in AirflowMethod:
            case_conf = TestcaseConfig()
            case_conf.continueWhenFailed = True
            case_conf.roundIntervalSec = roundIntervalSec_tmp
            testcaseID = case.get('testcaseID')
            paramStrs = case.get('paramStrs')
            if testcaseID is not None:
                case_conf.testcaseID = testcaseID
                print('Get Param testcaseID:', testcaseID)
            else:
                case_conf.testcaseID = 'L2TICKDETAILV2_1'
                print('Not Get Param testcaseID:', testcaseID)
            if paramStrs is not None:
                paramStrs_update = []
                for i in paramStrs:
                    paramStrs_update.append(json.dumps(i))
                case_conf.paramStrs.extend(paramStrs_update)
                print('Get Param paramStrs:', paramStrs_update)
            else:
                case_conf.paramStrs.extend([])
                print('Not Get Param paramStrs:', paramStrs)
            runner_conf.casesConfig.extend([case_conf])
        # print('i,case_list.length is ', case_list.__len__())
        runner_conf_list.append(runner_conf)
    return runner_conf_list

with DAG(
        dag_id='android_compare3',  # 测试计划名称
        default_args={
            'owner': 'jsj',
            'start_date': airflow.utils.dates.days_ago(0)
        },
        schedule_interval='@once',
) as dag:
    # conf = dag.get_dagrun(execution_date=dag.latest_execution_date).conf
    # if conf is None:
    #     conf  = default_conf

    conf={
			'collectionName': 'compare_result',  
			'Level': '2',
			'HKPerms': ['hk10'],			
			'roundIntervalSec': 3,                             
			'tag':[
					['release-20200103-0.0.3','53fcc717d954e01d88bc9bd70eaab9ac9a0acb67'],
					['release-20200103-0.0.3','53fcc717d954e01d88bc9bd70eaab9ac9a0acb67']
				],
			'AirflowMethod':[
								{
									'testcaseID': 'L2TICKDETAILV2_1', 
									'paramStrs': [
									{
											'CODE': '000100.sz',
											'SUBTYPE': '1001'
											}								
									]
								}
							],
			'server':[
						{
							'serverSites1': [
								["sh","http://114.80.155.134:22016"],
								["tcpsh","http://114.80.155.134:22017"],
								["shl2","http://114.80.155.62:22016"],
								["tcpshl2","http://114.80.155.62:22017"],
								
							]
						},
						{
							'serverSites2': [  
								["sh","http://117.184.225.151:22016"],
								["sz","http://117.184.225.151:22016"],
								["bj","http://117.184.225.151:22016"],
								
							]
						}
					],			
			'run_times':'1',
			'quote_detail':'1',	
			'plan_type':'1'  			
    }

    start_task = DummyOperator(
        task_id='run_this_first',
        queue='worker'
    )

    release_ok = DummyOperator(
        task_id='release_ok',
        queue='worker'
    )

    run_this_last = DummyOperator(
        task_id='run_this_last',
        queue='worker'
    )

    runner_conf_list = initRunnerConfig(conf)

    task_id_to_cmp_list = ['android_cmp_a', 'android_cmp_b']
    # sdk版本配置
    tag = conf.get('tag')
    if tag is not None:
        tag = list(tag)
        print('Get Param tag:',tag)
    else:
        tag=[['release-20200103-0.0.3', '53fcc717d954e01d88bc9bd70eaab9ac9a0acb67']]
        print('Not Get Param tag:',tag)
    if len(tag) == 1:
        tag_id_1 = tag[0][0]
        tag_id_2 = tag[0][0]
        tag_sha_1 = tag[0][1]
        tag_sha_2 = tag[0][1]
    else:
        tag_id_1 = tag[0][0]
        tag_id_2 = tag[1][0]
        tag_sha_1 = tag[0][1]
        tag_sha_2 = tag[1][1]
    #run_times_tmp=1
    run_times_tmp=conf.get('run_times')
    if run_times_tmp is not None:
        run_times_tmp=int(run_times_tmp)
        print('Get Param run_times:',run_times_tmp)
    else:
        run_times_tmp=1
        print('Not Get Param run_times',run_times_tmp)
        
    #quote_detail_tmp=1
    quote_detail_tmp=conf.get('quote_detail')
    if quote_detail_tmp is not None:
        quote_detail_tmp=int(quote_detail_tmp)
        print('Get Param quote_detail:',quote_detail_tmp)
    else:
        quote_detail_tmp=1
        print('Not Get Param quote_detail:',quote_detail_tmp)

    #tcp_times=1
    tcp_times_tmp=conf.get('tcp_times')
    if tcp_times_tmp is not None:
        tcp_times_tmp=int(tcp_times_tmp)
        print('Get Param tcp_times:',tcp_times_tmp)
    else:
        tcp_times_tmp=1
        print('Not Get Param tcp_times:',tcp_times_tmp)

    android_release_a = AndroidReleaseOperator(
        task_id='android_release_a',
        provide_context=False,
        repo_name='stocksdktest/AndroidTestRunner',
        tag_id=tag_id_1,
        tag_sha=tag_sha_1,
        runner_conf=runner_conf_list[0],
        release_xcom_key = "android_release_a"
    )
    android_release_b = AndroidReleaseOperator(
        task_id='android_release_b',
        provide_context=False,
        repo_name='stocksdktest/AndroidTestRunner',
        tag_id=tag_id_2,
        tag_sha=tag_sha_2,
        runner_conf=runner_conf_list[1],
        release_xcom_key = "android_release_b"
    )

    android_a = AndroidRunnerOperator(
        task_id=task_id_to_cmp_list[0],
        provide_context=False,
        apk_id='com.chi.ssetest',
        apk_version=tag_id_1,
        config_file=True,
        runner_conf=runner_conf_list[0],
        tcp_times=tcp_times_tmp,
        run_times=run_times_tmp,
        release_xcom_key = "android_release_a"
    )

    android_b = AndroidRunnerOperator(
        task_id=task_id_to_cmp_list[1],
        provide_context=False,
        apk_id='com.chi.ssetest',
        apk_version=tag_id_2,
        config_file=True,
        runner_conf=runner_conf_list[1],
        tcp_times=tcp_times_tmp,
        run_times=run_times_tmp,
        release_xcom_key = "android_release_b"
    )

    runner_conf_cmp = runner_conf_list[0]

    android_cmp = DataCompareOperator(
        task_id='data_compare',
        task_id_list=task_id_to_cmp_list,
        retries=3,
        provide_context=False,
        runner_conf=runner_conf_cmp,
        run_times=run_times_tmp,
        quote_detail=quote_detail_tmp,
        dag=dag
    )
    start_task >> [android_release_a, android_release_b] >> release_ok >> [android_a,android_b] >> android_cmp >> run_this_last

if __name__ == "__main__":
    dag.cli()