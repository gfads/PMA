from datetime import datetime


class Analyser:
    stabilization_window_time: int = 300
    stabilization: bool = True
    quarantine: bool = True
    ratio: float = None
    score: float = None
    replicas: int = None
    replica_conflict: str = 'only'

    def __init__(self, replica_conflict: str = 'only', stabilization=True, stabilization_window_time: int = 300):
        self.replica_conflict = replica_conflict
        self.stabilization = stabilization
        self.stabilization_window_time = stabilization_window_time

    def __set_ratio__(self, ratio):
        self.ratio = ratio

    def __set_score__(self, score):
        self.score = score

    def reactive(self, deploys):
        for dname, deploy in deploys.items():
            query = deploy['queries']['cpu']

            self.calculate_ratio(query['current'], query['desired'])
            self.calculate_pod_needed_by_metric(deploy['replicas']['current'])
            query['replicas'] = self.replicas

            print(f'{dname} in {(datetime.now()).strftime("%H:%M:%S")} {query["current"]: .2f}')

            self.calculate_pod_needed(deploy)

            if deploy['adaptation_command'] != '':
                self.assessment_of_the_possibility_of_adaptation(deploy)
                self.can_adapt(deploy)

    def multivariate(self, deploys):

        for dname, deploy in deploys.items():
            if deploy['replicas']['needed'] == -1:
                self.calculate_ratio(deploy['queries']['cpu']['current'], deploy['queries']['cpu']['desired'])
                self.calculate_pod_needed_by_metric(deploy['replicas']['current'])
                deploy['queries']['cpu']['replicas'] = self.replicas

                print(f'{dname} in {(datetime.now()).strftime("%H:%M:%S")} {deploy["queries"]["cpu"]["current"]: .2f}')

                self.calculate_pod_needed(deploy)
            else:
                if abs(deploy['replicas']['current'] - deploy['replicas']['needed']) >= 0.8:
                    deploy['replicas']['needed'] = round(deploy['replicas']['needed'])

                    deploy['adaptation_command'] = 'scale'
                else:
                    deploy['replicas']['needed'] = round(deploy['replicas']['needed'])

                print(f'Predicted {deploy["replicas"]["needed"]} Pods to {dname} needed in the next minute!')

            if deploy['adaptation_command'] != '':
                self.assessment_of_the_possibility_of_adaptation(deploy)
                self.can_adapt(deploy)

    def proactive(self, deploys, proactive_mode):
        from forecaster import predict_ds, predict_cfa, predict_multivariate

        if proactive_mode == 'UNIVARIATE':
            predict_cfa(deploys)

            self.reactive(deploys)
        elif proactive_mode == 'MPS':
            predict_ds(deploys)

            self.reactive(deploys)
        elif proactive_mode == 'MULTIVARIATE':
            predict_multivariate(deploys)

            self.multivariate(deploys)

    def can_adapt(self, deploy):
        replicas_min = deploy['replicas']['min']
        replicas_max = deploy['replicas']['max']
        replicas_needed = deploy['replicas']['needed']
        replicas_current = deploy['replicas']['current']

        # Se a quantidade de réplicas pedida é menor que o mínimo!  or (replicas_current == replicas_min):
        if replicas_needed < replicas_min:
            deploy['adaptation_command'] = ''

        # Se o número pedido é igual o atual.
        if replicas_current == replicas_needed:
            deploy['adaptation_command'] = ''

        if replicas_needed > replicas_max and replicas_current == replicas_max:
            deploy['adaptation_command'] = ''

        if replicas_needed > replicas_max and replicas_current != replicas_max:
            deploy['replicas']['needed'] = replicas_max

    def calculate_ratio(self, current, desired):
        self.__set_ratio__(current / desired)

    def calculate_score(self, queries):
        throughput = queries['throughput']['current']
        response_time = queries['response_time']['current']
        cpu = queries['cpu']['current']
        memory = queries['memory']['current']

        self.__set_score__(((1 / (1 + response_time)) * (throughput / (cpu + memory))))

    def calculate_pod_needed_by_metric(self, current_pods):
        from math import ceil

        if not 0.9 <= self.ratio <= 1.1:
            self.replicas = ceil(current_pods * self.ratio) if ceil(current_pods * self.ratio) != 0 else current_pods
        else:
            self.replicas = current_pods

    def calculate_pod_needed(self, deploy):
        if self.replica_conflict == 'only':
            self.only(deploy)

    def only(self, deploy):
        if deploy['replicas']['current'] == self.replicas:
            deploy['adaptation_command'] = ''
            return

        deploy['replicas']['needed'] = self.replicas
        deploy['adaptation_command'] = 'scale'

    def assessment_of_the_possibility_of_adaptation(self, deploy):
        if self.stabilization:
            self.check_stabilization(deploy)

    def check_stabilization(self, deploy):
        from time import time

        if deploy['stabilization'][deploy['adaptation_command']] != -1:
            current_stabilization_time = time() - deploy['stabilization'][deploy['adaptation_command']]

            if current_stabilization_time >= self.stabilization_window_time:
                deploy['stabilization'][deploy['adaptation_command']] = -1
            else:
                deploy['adaptation_command'] = ''
