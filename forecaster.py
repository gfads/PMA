from typing import List


def predict_multivariate(deploys):
    from numpy import array, newaxis, repeat
    from pandas import DataFrame

    for dname, deploy in deploys.items():
        pk = deploy['models']['MULTIVARIATE']
        scaler = pk['scaler']
        best_model = pk['model']

        input_data = {}

        for name, query in deploy['queries'].items():
            input_data[name] = query['time_series']
            #print(name, len(query['time_series']))

        try:
            df = DataFrame.from_dict(input_data).fillna(0)
            input_data_normalized = scaler.transform(df)
            pred = best_model.predict(array(input_data_normalized[newaxis, :, :]), verbose=0)
            pred_unormalized = scaler.inverse_transform(repeat(pred, len(input_data.keys()), axis=-1))[:, 0]
            number_of_pods = pred_unormalized[0]

            if number_of_pods != number_of_pods:
                deploy['replicas']['needed'] = -1
            else:
                deploy['replicas']['needed'] = number_of_pods

        except Exception as error:
            print("An exception occurred:", error)  #
            deploy['replicas']['needed'] = -1
            pass


def predict_univariate(deploys):
    from knowledge import denormalise_data, normalise_data
    for dname, deploy in deploys.items():

        pk = deploy['models']['UNIVARIATE']
        scaler = pk['scaler']
        lags = pk['lag']

        best_model = pk['model']

        for name, query in deploy['queries'].items():
            try:
                query['n_time_series'] = normalise_data(scaler, query['time_series'])
                pred = best_model.predict(query['n_time_series'][lags[0: -1]].reshape(1, -1))
                query['current'] = denormalise_data(scaler, pred)[0][0]
            except:
                print('pass')


def predict_ds(deploys):
    from knowledge import denormalise_data, normalise_data
    for dname, deploy in deploys.items():

        first_model = next(iter(deploy['models']['MPS']))
        scaler = first_model['scaler']
        training_set = first_model['training_sample']

        for name, query in deploy['queries'].items():
            try:
                query['n_time_series'] = normalise_data(scaler, query['time_series'])
                roc = definition_of_roc(query['n_time_series'], training_set[:, 0:-1])
                best_model, lags = ds(roc, deploy['models']['MPS'])
                pred = best_model.predict(query['n_time_series'][lags[0: -1]].reshape(1, -1))
                query['current'] = denormalise_data(scaler, pred)[0][0]
            except Exception as error:
                print(error)
                print('pass')


def ds(roc, models):
    from sklearn.metrics import mean_squared_error
    from numpy import Inf

    best_score = Inf
    best_model = None
    best_lags = None

    for model in models:
        modelo = model['model']
        lags = model['lag']

        predicted = modelo.predict(roc[:, lags[0:-1]])
        actual = roc[:, -1]

        score = mean_squared_error(actual, predicted, squared=False)

        if score < best_score:
            best_score = score
            best_model = modelo
            best_lags = lags

    return best_model, best_lags


def definition_of_roc(testing_set, training_set):
    from numpy import array
    unordered_roc = calculates_distance_between_a_test_pattern_and_the_training_set(testing_set, training_set)

    return array(collect_the_competence_region(unordered_roc, training_set))


def collect_the_competence_region(distance_cr, training_set):
    roc_size = 10

    indices_patterns = range(0, len(training_set))
    distance_cr, indices_patterns = zip(*sorted(zip(distance_cr, indices_patterns)))
    indices_patterns_l = list(indices_patterns)

    return training_set[indices_patterns_l[0:roc_size]]


def calculates_distance_between_a_test_pattern_and_the_training_set(test_pattern, training_set):
    from scipy.spatial.distance import euclidean

    competence_region: List[float] = []
    for training_pattern in training_set:
        test_pattern = test_pattern.flatten()
        # print(test_pattern.shape, training_pattern[0:-1].shape)
        d = euclidean(test_pattern[0: -1], training_pattern[0:-1])
        competence_region.append(d)

    return competence_region
