from time import sleep
from copy import deepcopy
from analyser import Analyser
from executor import execute
from monitor import Monitor
from knowledge import load_pickle
from keras.models import load_model
from time import sleep

ML_ADAPT_PROACTIVE_MODE = 'UNIVARIATE'
WORKLOAD = 'worldcup98'

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

    'cpu': {
        'current': 0,
        'desired': 0.5,
        'models': {},
        'query': '(sum(rate(container_cpu_usage_seconds_total{image!="", namespace="$n", pod=~"$s.*"}[5m]' + offset + ')) / '
                                                                                                                      'sum(kube_pod_container_resource_requests{namespace="$n", pod=~"$s.*", resource="cpu"}' + offset + '))',
        'time_series': []
    },

    'heap': {
        'current': 0,
        'models': {},
        'query': '(sum(avg_over_time(base_memory_usedHeap_bytes{pod=~"$s.*"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_total_MarkSweepCompact': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="MarkSweepCompact"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_total_Copy': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="Copy"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_Copy': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_total_seconds{name="Copy"}[1m]' + offset + ')) / sum(deriv('
                                                                                    'base_gc_time_total_seconds{name="Copy"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_MarkSweepCompact': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_total_seconds{name="MarkSweepCompact"}[1m]' + offset + ')) / sum(deriv('
                                                                                                'base_gc_time_total_seconds{name="MarkSweepCompact"}[1m]' + offset + ')))',
        'time_series': []
    },

    'memory': {
        'current': 0,
        'models': {},
        'query': 'sum(max_over_time(container_memory_working_set_bytes{id=~".*kubepods.*", namespace="$n",'
                 'pod=~"$s-.*", name!~".*POD.*", container=""}[1m]' + offset + '))',
        'time_series': []
    },

    'rt': {
        'current': 0,
        'models': {},
        'query': 'avg(deriv(base_REST_request_elapsedTime_seconds{pod=~"$s.*",name!~".*POD.*", '
                 'class="com.acme.crud.FruitResource"}[1m]' + offset + '))',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'models': {},
        'query': 'sum(rate(base_REST_request_total{pod=~"$s.*",name!~".*POD.*",'
                 'class="com.acme.crud.FruitResource"}[1m]' + offset + '))',
        'time_series': []
    },
}

if WORKLOAD == 'alibaba3':
    models = ['svr']
elif WORKLOAD == 'worldcup98':
    models = ['mlp']
elif WORKLOAD == 'nasa':
    models = ['mlp']
elif WORKLOAD == 'alibaba7':
    models = ['mlp']
elif WORKLOAD == 'clarknet':
    models = ['rf']

deploys = {
    'quarkus-service': {'queries': deepcopy(METRICS), 'namespace': 'quarkus',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'models': {
                            'UNIVARIATE': load_pickle(
                                'Quarkus/UNIVARIATE/quarkus-service/' + WORKLOAD + '/quarkus-service' + models[0] + '20'),
                            'MPS': [load_pickle(
                                'Quarkus/MPS/quarkus-service/' + WORKLOAD + '/quarkus-service' + models[
                                    0] + 'bagging' + str(i) + '20')
                                for i
                                in range(0, 99)],
                            'MULTIVARIATE': load_pickle(
                                'Quarkus/MULTIVARIATE/quarkus-service/' + WORKLOAD + '/quarkus-service')
                        }},
}

microservices = ['quarkus-service']

if ML_ADAPT_PROACTIVE_MODE == 'UNIVARIATE':
    for microservice in microservices:
        del deploys[microservice]['models']['MPS']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['heap']
        del deploys[microservice]['queries']['jvm_total_MarkSweepCompact']
        del deploys[microservice]['queries']['jvm_total_Copy']
        del deploys[microservice]['queries']['jvm_seconds_Copy']
        del deploys[microservice]['queries']['jvm_seconds_MarkSweepCompact']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']

elif ML_ADAPT_PROACTIVE_MODE == 'MPS':
    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['heap']
        del deploys[microservice]['queries']['jvm_total_MarkSweepCompact']
        del deploys[microservice]['queries']['jvm_total_Copy']
        del deploys[microservice]['queries']['jvm_seconds_Copy']
        del deploys[microservice]['queries']['jvm_seconds_MarkSweepCompact']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']

elif ML_ADAPT_PROACTIVE_MODE == 'MULTIVARIATE':

    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['models']['MPS']
        deploys[microservice]['models']['MULTIVARIATE']['model'] = load_model(
            deploys[microservice]['models']['MULTIVARIATE']['model'])

monitor = Monitor('http://10.66.66.53:30000/prometheus/', end_time='now', start_time='19m', step='60')
# monitor = Monitor('http://172.20.16.232/prometheus/', end_time='now', start_time='19m', step='60')
analyser = Analyser()

sleep(180)

i = 0
while True:
    if i < 34:
        print('O software está operando reativamente!')
        monitor.monitor(deploys, 'reactive')
        analyser.reactive(deploys)

    else:
        print('O software está operando proativamente! ' + WORKLOAD + ' ' + ML_ADAPT_PROACTIVE_MODE)
        monitor.monitor(deploys, 'proactive')
        analyser.proactive(deploys, ML_ADAPT_PROACTIVE_MODE)

    execute(deploys)
    sleep(30)

    i = i + 1
