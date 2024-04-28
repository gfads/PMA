from time import sleep
from copy import deepcopy
from analyser import Analyser
from executor import execute
from monitor import Monitor
from knowledge import load_pickle
from keras.models import load_model

ML_ADAPT_PROACTIVE_MODE = 'MULTIVARIATE'

WORKLOAD = 'alibaba2'

time = '1m'
offset = ''

METRICS = {
    'pods': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'sum(kube_deployment_status_replicas{namespace="$n", deployment=~"$s.*"}) by ('
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
                                               'sum(kube_pod_container_resource_requests{namespace="$n", pod=~"$s.*", '
                                               'resource="cpu"}' + offset + ')',
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
    models = ['svr', 'svr', 'svr', 'mlp', 'mlp', 'mlp']
elif WORKLOAD == 'alibaba3':
    models = ['svr', 'mlp', 'svr', 'svr', 'svr', 'mlp']
elif WORKLOAD == 'worldcup98':
    models = ['svr', 'mlp', 'mlp', 'mlp', 'mlp', 'mlp']
elif WORKLOAD == 'nasa':
    models = ['mlp', 'svr', 'svr', 'svr', 'mlp', 'mlp']
elif WORKLOAD == 'alibaba7':
    models = ['rf', 'svr', 'mlp', 'mlp', 'svr', 'mlp']
elif WORKLOAD == 'clarknet':
    models = ['rf', 'svr', 'mlp', 'mlp', 'svr', 'mlp']

deploys = {
    'cars-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                    'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                    'stabilization': {'scale': -1},
                    'adaptation_command': '',
                    'models': {
                        'UNIVARIATE': load_pickle('Travels/UNIVARIATE/cars-v1/' + WORKLOAD + '/cars-v1' + models[0] + '20'),
                        'MPS': [load_pickle(
                            'Travels/MPS/cars-v1/' + WORKLOAD + '/cars-v1' + models[0] + 'bagging' + str(i) + '20')
                            for i
                            in range(0, 99)],
                        'MULTIVARIATE': load_pickle('Travels/MULTIVARIATE/cars-v1/' + WORKLOAD + '/cars-v1')
                    }},

    'discounts-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'models': {'UNIVARIATE': load_pickle(
                            'Travels/UNIVARIATE/discounts-v1/' + WORKLOAD + '/discounts-v1' + models[1] + '20'),
                            'MPS': [load_pickle(
                                'Travels/MPS/discounts-v1/' + WORKLOAD + '/discounts-v1' + models[1] + 'bagging'
                                + str(i) + '20') for i in range(0, 99)],
                            }
                        },

    'flights-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'models': {
                            'UNIVARIATE': load_pickle(
                                'Travels/UNIVARIATE/flights-v1/' + WORKLOAD + '/flights-v1' + models[2] + '20'),
                            'MPS': [
                                load_pickle(
                                    'Travels/MPS/flights-v1/' + WORKLOAD + '/flights-v1' + models[2] + 'bagging'
                                    + str(i) + '20') for i in range(0, 99)],
                            'MULTIVARIATE': load_pickle(
                                'Travels/MULTIVARIATE/flights-v1/' + WORKLOAD + '/flights-v1')
                        }},

    'hotels-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                 'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                 'stabilization': {'scale': -1},
                 'adaptation_command': '',
                 'models': {'UNIVARIATE': load_pickle('Travels/UNIVARIATE/hotels-v1/' + WORKLOAD + '/hotels-v1' + models[3] + '20'),
                            'MPS': [
                                load_pickle('Travels/MPS/hotels-v1/' + WORKLOAD + '/hotels-v1' + models[3] + 'bagging'
                                            + str(i) + '20') for i in range(0, 99)],
                            'MULTIVARIATE': load_pickle('Travels/MULTIVARIATE/hotels-v1/' + WORKLOAD + '/hotels-v1')
                            }},

    'insurances-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'models': {'UNIVARIATE': load_pickle(
                                  'Travels/UNIVARIATE/insurances-v1/' + WORKLOAD + '/insurances-v1' + models[
                                      4] + '20'),
                                  'MPS': [load_pickle(
                                      'Travels/MPS/insurances-v1/' + WORKLOAD + '/insurances-v1' + models[
                                          4] + 'bagging'
                                      + str(i) + '20') for i in range(0, 99)],
                                  'MULTIVARIATE': load_pickle(
                                      'Travels/MULTIVARIATE/insurances-v1/' + WORKLOAD + '/insurances-v1')
                              }},

    'travels-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'models': {'UNIVARIATE': load_pickle(
                                  'Travels/UNIVARIATE/travels-v1/' + WORKLOAD + '/travels-v1' + models[
                                      5] + '20'),
                                  'MPS': [load_pickle(
                                      'Travels/MPS/travels-v1/' + WORKLOAD + '/travels-v1' + models[
                                          5] + 'bagging'
                                      + str(i) + '20') for i in range(0, 99)],
                                  'MULTIVARIATE': load_pickle(
                                      'Travels/MULTIVARIATE/travels-v1/' + WORKLOAD + '/travels-v1')
                              }},
}

microservices = ['cars-v1', 'discounts-v1', 'flights-v1', 'hotels-v1', 'insurances-v1', 'travels-v1']

if ML_ADAPT_PROACTIVE_MODE == 'UNIVARIATE':
    for microservice in microservices:
        del deploys[microservice]['models']['MPS']
        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']

elif ML_ADAPT_PROACTIVE_MODE == 'MPS':
    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']

        if microservice not in ['discounts-v1']:
            del deploys[microservice]['models']['MULTIVARIATE']

        del deploys[microservice]['queries']['pods']
        del deploys[microservice]['queries']['memory']
        del deploys[microservice]['queries']['rt']
        del deploys[microservice]['queries']['tp']

elif ML_ADAPT_PROACTIVE_MODE == 'MULTIVARIATE':

    microservices = ['cars-v1', 'flights-v1', 'hotels-v1', 'insurances-v1', 'travels-v1']

    for microservice in microservices:
        del deploys[microservice]['models']['UNIVARIATE']
        del deploys[microservice]['models']['MPS']
        deploys[microservice]['models']['MULTIVARIATE']['model'] = load_model(
            deploys[microservice]['models']['MULTIVARIATE']['model'])

    del deploys['discounts-v1']

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
