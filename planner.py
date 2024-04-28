class Planner:
    stabilization_window_time: int = 300

    def planner(self, deploys):
        from math import ceil

        for _, deploy in deploys.items():
            for name, query in deploy['queries'].items():
                print(name, query['ratio'])
                ratio = query['ratio']

                if not 0.9 <= ratio <= 1.1:
                    print(query)
                    query['replicas'] = ceil(deploy['replicas']['current'] * ratio)
                    deploy['adaptation_command'] = 'scale'

                if deploy['adaptation_command'] != '':
                    self.assessment_of_the_possibility_of_adaptation(deploy)
                    self.can_adapt(deploy)


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





"""
def planner(deployments):
    from math import ceil

    for d in deployments:
        for key, dt_metric in deployments[d]['metrics'].items():
            ratio = deployments[d][key + '_ratio']

            if not 0.9 <= ratio <= 1.1:
                deployments[d][key + 'replicas_needed'] = ceil(deployments[d]['replicas']['current'] * ratio)
                deployments[d][key + 'adapt'] = True
            else:
                deployments[d][key + 'adapt'] = False

        deployments[d][key + 'replicas_needed'] = better_two(deployments[d])

        # deployments[d]['replicas']['needed'] = ceil(deployments[d]['replicas']['current'] * ratio)
        # print(key, ratio, deployments[d]['replicas']['needed'])
        # print(d, deployments[d]['replicas']['needed'], workload_ratio)
        # is_it_blocked_by_quarantine(deployments[d])

        # print('Is ' + d + ' blocked by quarantine? ' + str(is_it_blocked_by_quarantine(deployments[d])))
        
        """