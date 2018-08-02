from pymongo import MongoClient
import numpy as np
import pandas as pd
import utils as ut
import config

# mongoClient = MongoClient(config.mongo.host, 27017)
uri = 'mongodb://%s:%s@%s:%s/%s' % (config.username, config.password, config.host, config.port, config.db)
# uri = 'mongodb://localhost:27017/VNLP'
db = MongoClient(uri).get_database()

# client = MongoClient('localhost', 27017)
# db = client.VNLP
corpusCollection = db.Corpus
dbFeatures = db.Corpus.distinct("feature")
# columns = dbFeatures


# valuable word means that the word have a specific value in the sentence
def findValuableWordsOfFeature(text, feature):
    Terms = []
    EmotionalValues = []
    w = ut.WordOfText(text)
    start = 0
    stop = len(w)
    isStop = False
    while (isStop == False and stop >= 0):
        term = preFix = ""
        for index in range(start, stop):
            term += w[index] + " "
        for index in range(0, start):
            preFix += w[index] + " "

        #         preprocessing text
        term = term.strip()
        preFix = preFix.strip()

        if (len(term.split(" ")) < 5):
            foundTerm = corpusCollection.find_one({"content": term, "feature": feature})
        else:
            foundTerm = None
        if (foundTerm != None):
            Terms.append(term)
            EmotionalValues.append(foundTerm["weight"])
            if (start == 0):
                isStop = True
            else:
                stop = start-1
                start = 0
        else:
            if (start == stop):
                stop -= 1
                start = 0
            else:
                start += 1
            if stop < 1:
                isStop = True
    return [EmotionalValues, Terms]

def findFeatureInSentence(text):
    features = []
    maxWordLength = 3
    _length = 1
    wordsInSentence = ut.WordOfText(text)  # split sentence into words
    while (_length <= maxWordLength):
        pos = 0
        #         _length - 1 la so tu + them
        while (pos + (_length - 1) < len(wordsInSentence)):
            count = 0
            temp = ""
            while (count < _length and pos + count < len(wordsInSentence)):
                if temp == "":
                    temp = wordsInSentence[pos + count]
                else:
                    temp += " " + wordsInSentence[pos + count]
                #                 print(pos, count, len(wordsInSentence))
                count += 1

            #             print(pos, count, len(wordsInSentence), ";" + temp + ";", dbFeatures)

            if temp in dbFeatures:
                features.append(temp)
            pos += 1
        _length += 1

    # distinct feature
    res = list(set(features))
    return res


def seperateSentenceByFeatures(sentence):
    import re
    features = "|".join(["({})".format(x) for x in dbFeatures])
    #get all index of features in sentence
    idx = [m.start() for m in re.finditer(features, sentence)]

    #get content for debug
    content = [m.group() for m in re.finditer(features, sentence)]

    res = []
    if len(idx) > 1:
        for i, _from in enumerate(idx):
            if i+1 == len(idx):
                to = len(sentence)
            else:
                to = idx[i+1]-1
            if i == 0:
                _from = 0
            res.append(sentence[_from:to])

            # res.append(sentence[:val - 1])
            # sentence = sentence[val:]
    else:
        res.append(sentence)
    return res


def analyzingSentence(sentence):
    vectorSentimentValues = pd.DataFrame(columns=dbFeatures)
    arrWords = {}
    arrWords["content"] = {}
    arrWords["score"] = {}
    vectorSentimentValues.loc[0] = [0] * len(dbFeatures)
    #loop1 : seperate sentence by delimiters : "."
    for _sentence1 in ut.separate(sentence):
        #loop2 : seperate sentence1 by feature
        for _sentence2 in seperateSentenceByFeatures(_sentence1):
            #find the feature in sentence2 which is a small part of sentence 1
            features = findFeatureInSentence(_sentence2)
            if len(features) == 1:
                #take the feature from list features
                _feature = features[0]
                #find in corpus that contains relative words to feature
                # content includes words which is relative features
                # It actually helps to debug
                wordsValue = findValuableWordsOfFeature(_sentence2, _feature)[0]
                content = findValuableWordsOfFeature(_sentence2, _feature)[1]
                #final Value Of relavant words to the feature
                finalValue = 0
                if len(wordsValue) == 1:
                    #take value of word
                    finalValue = wordsValue[0]
                elif len(wordsValue) > 1:
                    #sum all value of words if we have more than one word
                    finalValue = sum(wordsValue[0:len(wordsValue)])
                arrWords["content"][_feature] = content
                arrWords["score"][_feature] = wordsValue
                vectorSentimentValues[_feature] += finalValue
                # content includes words which is relative features
                # It actually helps to debug
                # content includes words which is relative features
                # It actually helps to debug
            # elif len(features) > 1:
            #     feature = "|".join([x for x in dbFeatures])
            #
            #     print("Not supported yet! \t ", len(features), "\n", sentence)

    return [vectorSentimentValues, arrWords]


def predictSentence(sentence, vectorSentimentValues):
    # xây dựng vector biễu diễn trọng số cảm xúc
    inp = vectorSentimentValues.values.reshape((15,))
    G = inp
    P = (G > 0) * G # < 0 to take positive words
    N = (G < 0) * G # > ) to take negative words

    # print(G, P, N)
    if (np.count_nonzero(G) == 0):
        return "câu chưa biết"
    elif (np.count_nonzero(P) == 0):
        return "câu chê"
    elif (np.count_nonzero(N) == 0):
        return "câu khen"
    else:
        positiveCos = ut.cosine_similarity(P, G)
        negativeCos = ut.cosine_similarity(N, G)
        if positiveCos > negativeCos:
            return "câu khen"
        elif positiveCos == negativeCos:
            return "câu bình thường"
        else:
            return "câu chê"


def sentimentAnalysisExecute(sentence):
    obj = {}
    sentence = ut.formatText(sentence)
    # res = analyzingSentence(sentence)
    [vectorSentimentValues, arrWords] = analyzingSentence(sentence)
    semtinentOfSentence = predictSentence(sentence, vectorSentimentValues)

    obj["sentence"] = sentence
    obj["score"] = vectorSentimentValues.values[0,:].tolist()
    obj["predict"] = semtinentOfSentence
    obj["corpus"] = arrWords
    return obj


pd.set_option('display.max_columns', 500)
# sentence = "Ai thích sang chanh thì Táo, tôi thì ĐT màn hình xấu, cam đẹp, pin khá trâu, cấu hình vừa phải, nhưng giá quá mắc"


from tqdm import tqdm
def processing(sentence, commentId):
    sentimentDb = db.Web_Comment_Analyzed
    print("handling sentence : ", sentence)
    obj = sentimentAnalysisExecute(sentence)
    obj['commentId'] = commentId
    print(obj)
    sentimentDb.insert(obj)
    return obj['predict']

# def start():
#     database = db.vnexpresses
#     sentimentDb = db.sentiment_analysis
#     sentimentDb.drop()
#
#     sentence = "ĐT màn hình hơi xấu, camera đẹp, pin khá trâu, nói chung là khá okay"
#     result = sentimentAnalysisExecute(sentence)
#     print(result)
#     print("câu :", result["sentence"])
#     print("predict value :", result["predict"])
#     print("giá trị của các từ trong từ điển: \n", result["corpus"]["score"])
#     print("các từ trong từ điển: \n", result["corpus"]["content"])
#
#     # queryData = database.find({}).distinct("content")
#     # print(len(queryData))
#     # for record in tqdm(queryData):
#     #     # if "Đâu đâu cũng iphone với các loại điệ" in record:
#     #     # print("handling", record)
#     #     obj = sentimentAnalysisExecute(record)
#     #     # print(obj)
#     #     sentimentDb.insert(obj)
#
#
#     #debug1
#     # record = "Ai thích sang chanh thì Táo, tôi thì ĐT màn hình xấu, camera đẹp, pin khá trâu, cấu hình vừa phải, nhưng giá quá mắc"
#     # record = "cấu hình so với 1 em điện thoại nắp gập thế này là ổn rồi  bị cái pin hơi thốn cơ mà màn hình cũng chỉ là qvga nên chắc thoải mái  và nữa là pin cũng tháo rời được mà nên có thể thay thế luôn được  mình không"
#
#     # sentimentAnalysisExecute(record)
#
# start()