from time import sleep
from copy import deepcopy
from analyser import Analyser
from executor import execute
from monitor import Monitor
from knowledge import load_pickle
from keras.models import load_model
from time import sleep

ML_ADAPT_PROACTIVE_MODE = 'MULTIVARIATE'
WORKLOAD = 'nasa'

print(WORKLOAD, ML_ADAPT_PROACTIVE_MODE)

time = '1m'
offset = ''

METRICS = {

    'pods': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'sum(kube_deployment_status_replicas{namespace="$n", deployment=~"$s.*"}' + offset + ') by ('
                 'deployment)',
        'time_series': []
    },

    'conn-pool_jdbc_TradeDataSource': {
        'current': 0,
        'desired': 0,
        'models': {},
        'query': 'avg(avg_over_time(vendor_connectionpool_managedConnections{pod=~"$s.*", name!~".*POD.*,", '
                 'datasource="jdbc_TradeDataSource"}[1m]' + offset + '))',
        'time_series': []
    },

    'conn-pool_jms_TradeStreamerTCF': {
        'current': 0,
        'desired': 0,
        'models': {},
        'query': 'avg(avg_over_time(vendor_connectionpool_managedConnections{pod=~"$s.*", name!~".*POD.*,", '
                 'datasource="jms_TradeStreamerTCF"}[1m]' + offset + '))',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.8,
        'max': 10,
        'models': {},
        'query': 'sum(rate(container_cpu_usage_seconds_total{image!="", namespace="$n", '
                 'pod=~"$s.*"}[5m]' + offset + ')) / '
                                               'sum(kube_pod_container_resource_requests{namespace="$n", pod=~"$s.*", '
                                               'resource="cpu"}' + offset + ')',
        'time_series': []
    },

    'heap': {
        'current': 0,
        'models': {},
        'query': 'sum(avg_over_time(base_memory_maxHeap_bytes{pod=~"$s.*"}[1m]' + offset + '))',
        'time_series': []
    },

    'jvm_total_scavenge': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="scavenge"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_total_global': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="global"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_scavenge': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_seconds{name="scavenge"}[1m]' + offset + ')) / sum(deriv(base_gc_time_seconds{'
                                                                             'name="scavenge"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_global': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_seconds{name="global"}[1m]' + offset + ')) / sum(deriv('
                                                                           'base_gc_time_seconds{name="global"}[1m]' + offset + ')))',
        'time_series': []
    },

    'memory': {
        'current': 0,
        'models': {},
        'query': 'sum(max_over_time(container_memory_working_set_bytes{id=~".*kubepods.*", namespace="$n",'
                 'pod=~"$s-.*", name!~".*POD.*", container=""}[5m]' + offset + '))',
        'time_series': []
    },

    'rt': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': '(sum by (app) (rate(vendor_servlet_responseTime_total_seconds{pod=~"$s.*", '
                 'servlet!~"com_ibm_ws_microprofile.*"}[1m]' + offset + ') / rate(vendor_servlet_request_total{pod=~"$s.*", '
                                                                        'servlet!~"com_ibm_ws_microprofile.*"}[1m]' + offset + ') > 0))',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'sum(rate(vendor_servlet_request_total{pod=~"$s.*", servlet!~"com_ibm_ws_microprofile.*|.*Trade.*"}[1m]' + offset + '))',
        'time_series': []
    },

    'thread_pool': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'avg(avg_over_time(vendor_threadpool_activeThreads{pod=~"$s.*", name!~".*POD.*"}[1m]' + offset + '))',
        'time_series': []
    },

}

if WORKLOAD == 'alibaba2':
    models = ['svr', 'svr', 'svr', 'mlp', 'mlp', 'mlp']
elif WORKLOAD == 'alibaba3':
    models = ['svr', 'mlp', 'svr', 'svr', 'svr', 'mlp']
elif WORKLOAD == 'worldcup98':
    models = ['rf']
elif WORKLOAD == 'nasa':
    models = ['svr']
elif WORKLOAD == 'alibaba7':
    models = ['mlp']
elif WORKLOAD == 'clarknet':
    models = ['rf']

deploys = {
    'daytrader-service': {'queries': deepcopy(METRICS), 'namespace': 'daytrader',
                'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                'stabilization': {'scale': -1},
                'adaptation_command': '',
                'models': {
                    'UNIVARIATE': load_pickle('Daytrader/UNIVARIATE/daytrader-service/' + WORKLOAD + '/daytrader-service' + models[0] + '20'),
                    'MPS': [load_pickle(
                        'Daytrader/MPS/daytrader-service/' + WORKLOAD + '/daytrader-service' + models[0] + 'bagging' + str(i) + '20')
                        for i
                        in range(0, 99)],
                    'MULTIVARIATE': load_pickle('Daytrader/MULTIVARIATE/daytrader-service/' + WORKLOAD + '/daytrader-service')
                }},
}

microservices = ['daytrader-service']

if ML_ADAPT_PROACTIVE_MODE == 'UNIVARIATE':
    for microservice in microservices:
        del deploys[microservice]['models']['MPS']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['conn-pool_jdbc_TradeDataSource']
        del deploys[microservice]['queries']['conn-pool_jms_TradeStreamerTCF']
        del deploys[microservice]['queries']['heap']
        del deploys[microservice]['queries']['jvm_total_scavenge']
        del deploys[microservice]['queries']['jvm_total_global']
        del deploys[microservice]['queries']['jvm_seconds_scavenge']
        del deploys[microservice]['queries']['jvm_seconds_global']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']
        del deploys[microservice]['queries']['thread_pool']

elif ML_ADAPT_PROACTIVE_MODE == 'MPS':
    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['conn-pool_jdbc_TradeDataSource']
        del deploys[microservice]['queries']['conn-pool_jms_TradeStreamerTCF']
        del deploys[microservice]['queries']['heap']
        del deploys[microservice]['queries']['jvm_total_scavenge']
        del deploys[microservice]['queries']['jvm_total_global']
        del deploys[microservice]['queries']['jvm_seconds_scavenge']
        del deploys[microservice]['queries']['jvm_seconds_global']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']
        del deploys[microservice]['queries']['thread_pool']

elif ML_ADAPT_PROACTIVE_MODE == 'MULTIVARIATE':

    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['models']['MPS']
        deploys[microservice]['models']['MULTIVARIATE']['model'] = load_model(
            deploys[microservice]['models']['MULTIVARIATE']['model'])

monitor = Monitor('http://10.66.66.53:30000/prometheus/', end_time='now', start_time='19m', step='60')
#monitor = Monitor('http://172.20.16.232/prometheus/', end_time='now', start_time='19m', step='60')
analyser = Analyser()

sleep(180)

i = 0
while True:
    if i < 34:
        print('O software está operando reativamente!')
        monitor.monitor(deploys, 'reactive')
        analyser.reactive(deploys)

    else:
        print('O software está operando proativamente! ' + ML_ADAPT_PROACTIVE_MODE)
        monitor.monitor(deploys, 'proactive')
        analyser.proactive(deploys, ML_ADAPT_PROACTIVE_MODE)

    execute(deploys)
    sleep(30)

    i = i + 1
