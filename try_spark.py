from pyspark import SparkContext
from pyspark.mllib.tree import RandomForest
from pyspark.mllib.regression import LabeledPoint
import numpy as np

sc = SparkContext()

def to_float(arr):
    '''
    Used to unitedly convert RDD item fields' data types
    '''
    result = []
    for item in arr:
        result.append(float(item))
    return result

def experiment(to_learn_file):
    '''
    Input: .csv file with the first column being integer labels ranging from 0 to (#lables -1), the rest being float-numbered features
    Output: accuracy of experiment
    '''
    # Read and format labels and features
    to_learn = sc.textFile(to_learn_file).map(lambda item: item.split(' ')).map(to_float).map(lambda item: LabeledPoint(item[0], item[1:])).cache()
    # Split into train and test RDDs in the 5-fold cross validation manner
    (train, test) = to_learn.randomSplit([0.8, 0.2])
    # Train random forest model
    model = RandomForest.trainClassifier(train,numClasses=6,categoricalFeaturesInfo={},numTrees=3,featureSubsetStrategy="auto",impurity='gini',maxDepth=30, maxBins=32)
    # make predictions and calculate RMSE
    predictions = model.predict(test.map(lambda x: x.features))
    labelsAndPredictions = test.map(lambda lp: lp.label).zip(predictions)
    return labelsAndPredictions.filter(lambda (v, p): v != p).count() / float(test.count())


if __name__ == '__main__':
    acc = []
    for i in range(2003, 2015):
        acc_group = []
        for j in range(10):
            acc_group.append(experiment('to_learn_' + str(i) + '.csv'))
        acc.append(acc_group)
    # save accuracy matrix to file
    np.savetxt('spark_results.txt', np.array(acc), delimiter=',')
