from time import sleep
from copy import deepcopy
from analyser import Analyser
from executor import execute
from monitor import Monitor
from knowledge import load_pickle
from keras.models import load_model

ML_ADAPT_PROACTIVE_MODE = 'MPS'
ML_ADAPT_GENERATION_APPROACH = 'homogeneous'

WORKLOAD = 'clarknet'

time = '1m'
offset = ''

METRICS = {
    'pods': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'sum(kube_deployment_spec_replicas{namespace="$n", deployment=~"$s.*"}) by ('
                 'deployment)',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.8,
        'max': 10,
        'models': {},
        'query': 'sum(rate(container_cpu_usage_seconds_total{image!="", namespace="$n", '
                 'pod=~"$s.*"}[5m]' + offset + ')) / '
                                               'sum(kube_pod_container_resource_requests{namespace="$n", pod=~"$s.*", resource="cpu"}' + offset + ')',
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
        'desired': 0.8,
        'models': {},
        'query': '((histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter="destination", '
                 'destination_workload_namespace=~"$n", destination_workload=~"$s.*"}[1m]' + offset + ')) by '
                                                                                                      '(le, destination_workload))) / 1000)',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'round(sum(irate(istio_requests_total{reporter="destination", destination_workload=~"$s.*"}[1m]' + offset + ')) by ('
                                                                                                                             'destination_workload), 0.001)',
        'time_series': []
    }
}

if WORKLOAD == 'alibaba2':
    models = ['mlp', 'svr', 'mlp', 'svr', 'mlp', 'mlp']
elif WORKLOAD == 'alibaba3':
    models = ['mlp', 'svr', 'mlp', 'svr', 'svr', 'svr']
elif WORKLOAD == 'worldcup98':
    models = ['mlp', 'svr', 'mlp', 'svr', 'mlp', 'svr']
elif WORKLOAD == 'nasa':
    models = ['mlp', 'mlp', 'svr', 'svr', 'mlp', 'mlp']
elif WORKLOAD == 'alibaba7':
    models = ['mlp', 'mlp', 'svr', 'svr', 'mlp', 'mlp']
elif WORKLOAD == 'clarknet':
    models = ['mlp', 'mlp', 'mlp', 'mlp', 'svr', 'mlp']

deploys = {
    'cartservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                    'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                    'stabilization': {'scale': -1},
                    'adaptation_command': '',
                    'models': {
                        'UNIVARIATE': load_pickle('OB/UNIVARIATE/cartservice/' + WORKLOAD + '/cartservice' + models[0] + '20'),
                        'MPS': [load_pickle(
                            'OB/MPS/cartservice/' + WORKLOAD + '/cartservice' + models[0] + 'bagging' + str(i) + '20')
                            for i
                            in range(0, 99)],
                        'MULTIVARIATE': load_pickle('OB/MULTIVARIATE/cartservice/' + WORKLOAD + '/cartservice')
                    }},

    'checkoutservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'models': {'UNIVARIATE': load_pickle(
                            'OB/UNIVARIATE/checkoutservice/' + WORKLOAD + '/checkoutservice' + models[1] + '20'),
                            'MPS': [load_pickle(
                                'OB/MPS/checkoutservice/' + WORKLOAD + '/checkoutservice' + models[1] + 'bagging'
                                + str(i) + '20') for i in range(0, 99)],
                            'MULTIVARIATE': load_pickle(
                                'OB/MULTIVARIATE/checkoutservice/' + WORKLOAD + '/checkoutservice')
                        }
                        },

    'currencyservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'models': {
                            'UNIVARIATE': load_pickle(
                                'OB/UNIVARIATE/currencyservice/' + WORKLOAD + '/currencyservice' + models[2] + '20'),
                            'MPS': [
                                load_pickle(
                                    'OB/MPS/currencyservice/' + WORKLOAD + '/currencyservice' + models[2] + 'bagging'
                                    + str(i) + '20') for i in range(0, 99)],
                            'MULTIVARIATE': load_pickle(
                                'OB/MULTIVARIATE/currencyservice/' + WORKLOAD + '/currencyservice')
                        }},

    'frontend': {'queries': deepcopy(METRICS), 'namespace': 'default',
                 'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                 'stabilization': {'scale': -1},
                 'adaptation_command': '',
                 'models': {'UNIVARIATE': load_pickle('OB/UNIVARIATE/frontend/' + WORKLOAD + '/frontend' + models[3] + '20'),
                            'MPS': [
                                load_pickle('OB/MPS/frontend/' + WORKLOAD + '/frontend' + models[3] + 'bagging'
                                            + str(i) + '20') for i in range(0, 99)],
                            'MULTIVARIATE': load_pickle('OB/MULTIVARIATE/frontend/' + WORKLOAD + '/frontend')
                            }},

    'productcatalogservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'models': {'UNIVARIATE': load_pickle(
                                  'OB/UNIVARIATE/productcatalogservice/' + WORKLOAD + '/productcatalogservice' + models[
                                      4] + '20'),
                                  'MPS': [load_pickle(
                                      'OB/MPS/productcatalogservice/' + WORKLOAD + '/productcatalogservice' + models[
                                          4] + 'bagging'
                                      + str(i) + '20') for i in range(0, 99)],
                                  'MULTIVARIATE': load_pickle(
                                      'OB/MULTIVARIATE/productcatalogservice/' + WORKLOAD + '/productcatalogservice')
                              }},

    'recommendationservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'models': {'UNIVARIATE': load_pickle(
                                  'OB/UNIVARIATE/recommendationservice/' + WORKLOAD + '/recommendationservice' + models[
                                      5] + '20'),
                                  'MPS': [load_pickle(
                                      'OB/MPS/recommendationservice/' + WORKLOAD + '/recommendationservice' + models[
                                          5] + 'bagging'
                                      + str(i) + '20') for i in range(0, 99)],
                                  'MULTIVARIATE': load_pickle(
                                      'OB/MULTIVARIATE/recommendationservice/' + WORKLOAD + '/recommendationservice')
                              }},
}

#microservices = ['cartservice', 'checkoutservice', 'currencyservice', 'frontend', 'productcatalogservice', 'recommendationservice']

microservices = ['cartservice', 'currencyservice', 'frontend', 'productcatalogservice', 'recommendationservice']

if ML_ADAPT_PROACTIVE_MODE == 'UNIVARIATE':
    for microservice in microservices:
        del deploys[microservice]['models']['MPS']
        del deploys[microservice]['models']['MULTIVARIATE']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']

elif ML_ADAPT_PROACTIVE_MODE == 'MPS':
    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['models']['MULTIVARIATE']
        del deploys[microservice]['queries']['pods']
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
analyser = Analyser()

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
