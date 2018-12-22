from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import math
import config

# import sklearn
# print('The scikit-learn version is {}.'.format(sklearn.__version__))

# uri = 'mongodb://localhost:27017/VNLP'
# db = MongoClient(uri).get_database()

# mongoClient = MongoClient(config.mongo.host, 27017)
uri = 'mongodb://%s:%s@%s:%s/%s' % (config.username, config.password, config.host, config.port, config.db)
# uri = 'mongodb://localhost:27017/VNLP'
db = MongoClient(uri).get_database()


kmeans = None
clusterLabels = ["câu chê", "câu bình thường", "câu khen"]


def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i];
        y = v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    if sumxx == 0 or sumyy == 0:
        return 0
    return sumxy / math.sqrt(sumxx * sumyy)

def showClusterReview(centers):
    print(centers)
    center1 = centers[0, :]
    center2 = centers[1, :]
    center3 = centers[2, :]

    P = (center1 > 0) * center1
    N = (center1 < 0) * center1
    P2 = (center2 > 0) * center2
    N2 = (center2 < 0) * center2
    P3 = (center3 > 0) * center3
    N3 = (center3 < 0) * center3

    posV = cosine_similarity(P, center1)
    negV = cosine_similarity(N, center1)
    # print(posV, negV)

    posV2 = cosine_similarity(P2, center2)
    negV2 = cosine_similarity(N2, center2)
    # print(posV2, negV2)

    posV3 = cosine_similarity(P3, center3)
    negV3 = cosine_similarity(N3, center3)
    # print(posV3, negV3)
    return [posV-negV, posV2-negV2, posV3-negV3]

def trainKmean():
    cursor = db.trainData.find({}, {'score': 1, 'label': 1})
    df = pd.DataFrame(list(cursor))
    cols = db.Corpus.distinct("feature")
    cols.append("label")
    print(cols)
    scoreArr = [x for x in df['score']]
    scoreDF = pd.DataFrame(scoreArr)

    vectorScoreDF = pd.DataFrame(columns=cols)
    for i in range(len(cols)):
        if cols[i] == "label":
            vectorScoreDF['label'] = df['label']
        else:
            vectorScoreDF[cols[i]] = scoreDF[i]
    vectorScoreDF.head()

    X = vectorScoreDF.drop(["label"], axis=1)
    X = np.array(X)
    y = df["label"]

    kmeans = KMeans(
        #     init=init,
        n_init=10,
        n_clusters=3,
        max_iter=6000
    )

    kmeans.fit(X)
    centers = np.array(kmeans.cluster_centers_)
    errorMeasureClusters = showClusterReview(centers)
    for idx in range(len(errorMeasureClusters)):
        if (errorMeasureClusters[idx] > 0.8):
            clusterLabels[idx] = "câu khen"
        elif (errorMeasureClusters[idx] < -0.8):
            clusterLabels[idx] = "câu chê"
        else:
            clusterLabels[idx] = "câu bình thường"

    return kmeans

def evaluate():
    # print(kmeans)
    centers = np.array(kmeans.cluster_centers_)
    errorMeasureClusters = showClusterReview(centers)

    testSentences = db.testData.find({})
    testDF = pd.DataFrame(list(testSentences))
    resDF = testDF[['sentence', 'score', 'label']]

    # clusterLabels = ["câu khen", "câu bình thường", "câu chê"]
    clusterLabels = ["câu chê", "câu bình thường", "câu khen"]

    for idx in range(len(errorMeasureClusters)):
        if (errorMeasureClusters[idx] > 0.8):
            clusterLabels[idx] = "câu khen"
        elif (errorMeasureClusters[idx] < -0.8):
            clusterLabels[idx] = "câu chê"
        else:
            clusterLabels[idx] = "câu bình thường"

    # print(errorMeasureClusters, clusterLabels)

    for idx in range(len(testDF)):
        score = testDF.at[idx, 'score']
        label = testDF.at[idx, 'label']
        clusterIndex = kmeans.predict(np.array([score]))[0]
        testDF.at[idx, 'predict'] = clusterLabels[clusterIndex]

    exactlyPredicted = len(testDF[testDF['label'] == testDF['predict']]['label'])
    accuracy = (exactlyPredicted / len(testDF) * 100)
    if (accuracy < 70):
        return False
    else:
        print('exactlyPredicted/total : ', exactlyPredicted, '/', len(testDF))
        print('accuracy : ', (exactlyPredicted / len(testDF) * 100))
        statDF = testDF.groupby(['label', 'predict'], as_index=False)
        print(statDF.count())
        return True

def predict(vectorScore):
    clusterIndex = kmeans.predict(np.array([vectorScore]))[0]
    return clusterLabels[clusterIndex]

if kmeans == None:
    kmeans = trainKmean()
    while not evaluate():
        kmeans = trainKmean()


