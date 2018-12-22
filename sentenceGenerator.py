from pymongo import MongoClient
import random
import sentimentAnalyze

uri = 'mongodb://localhost:27017/VNLP'
db = MongoClient(uri).get_database()

# generateSentenceDb = db.generated_sentence_v2_1
# generateSentenceDb.delete_many({})

subjects = [
    "chiếc", "điện thoại", "máy điện thoại", "mẫu điện thoại",
    "hãng điện thoại"
]

phones = [
    "xiaomi", "iphone", "huawei", "samsung",
    "nokia", "Bphone"
]

ptcmdArr = {}
ptcmdArr[2] = ["siêu", "cực kỳ", "cực kì", "cực", "vô cùng", "kinh khủng", "hoàn toàn", "kinh hồn"]
ptcmdArr[1] = ["rất", "quá", "thật", "càng"]
ptcmdArr[0] = ["không", "chẳng", "chả", "không được", "chả được", "chẳng được"]
ptcmdArr[-1] = ["khá", "tạm", "tương đối", "hơn"]
ptcmdArr[-2] = ["hơi", "cũng"]

arrPositiveSeedWords = {}
arrNegativeSeedWords = {}

arrPositiveSeedWords["pin"] = ["cao", "trâu", "ngon", "tốt", "tiết kiệm", "mạnh", "khỏe", "khủng", "bền", "lớn",
                               "ổn"]
arrNegativeSeedWords["pin"] = ["thấp", "ngốn", "nóng", "kém", "yếu", "hao", "tốn", "xì", "phồng", "nổ", "cháy nổ"
                               ,"phù", "thốn", "lỗi" , "nhanh hết"]

arrPositiveSeedWords["ram"] = ["cao", "nhiều", "khủng"]
arrNegativeSeedWords["ram"] = ["thấp", "ít"]

arrPositiveSeedWords["cấu hình"] = ["ok", "okay", "khủng", "ổn"]
arrNegativeSeedWords["cấu hình"] = ["thấp", "nản", "yếu"]

arrPositiveSeedWords["màn hình"] = ["thời thượng", "sang trọng", "đẹp", "to", "bự", "lớn", "tốt"]
arrNegativeSeedWords["màn hình"] = ["xấu", "kém", "nhỏ", "chói"]

arrPositiveSeedWords["thiết kế"] = ["thời thượng", "sang trọng", "đẹp", "ổn", "mới", "sắc xảo", "công phu", "đổi mới"]
arrNegativeSeedWords["thiết kế"] = ["xấu", "kém", "thô thiển", "cũ rích"]
# exception [ "đẹp mê li", "


arrPositiveSeedWords["kiểu dáng"] = [ "đẹp", "ổn", "mới", "sắc xảo", "công phu", "đổi mới"]
arrNegativeSeedWords["kiểu dáng"] = ["xấu", "kém", "thô thiển", "cũ rích"]


arrPositiveSeedWords["giá"] = ["rẻ", "phù hợp", "mềm", "tốt", "okay", "nhẹ nhàng", "hợp lý", "ngọt", "ngon", "đáng",
                               "phải chăng", "xứng đáng"]
# exception [ "đáng đồng tiền bát gạo"

arrNegativeSeedWords["giá"] = ["cao", "chát", "đắt", "mắc"]
# exception [ "giá vừa phải", "giá trên trời", "giá cũng chỉ bằng nửa", "giá cũng chỉ bằng một nửa", "giá tận ..."
# "giá trên mây"

# arrPositiveSeedWords["độ phân giải"] = ["cao"]
# arrNegativeSeedWords["độ phân giải"] = ["thấp"]
# # #exception [ "" ]

arrPositiveSeedWords["ứng dụng"] = ["khủng", "nhiều", "đồ sộ"]
arrNegativeSeedWords["ứng dụng"] = ["ít", "khiêm tốn"]
# # #exception [ "" ]

arrPositiveSeedWords["camera"] = ["bá", "bá đạo", "vượt trội", "ấn tượng", "xịn", "tốt", "khá", "đẹp"]
arrNegativeSeedWords["camera"] = ["xấu", "tệ", "rung lắc", "sida"]
# # #exception [ "" ]

arrPositiveSeedWords["giao diện"] = ["đẹp"]
arrNegativeSeedWords["giao diện"] = ["rườm rà", "xấu"]
# # #exception [ "" ]

arrPositiveSeedWords["cảm ứng"] = ["nhạy", "nhanh"]
arrNegativeSeedWords["cảm ứng"] = ["đơ đứng", "chậm"]
# #exception [ "" ]

# arrPositiveSeedWords["tốc độ"] = ["nhanh"]
# arrNegativeSeedWords["tốc độ"] = ["chậm"]
# #exception [ "" ]
#
# arrPositiveSeedWords["hiệu năng"] = ["tốt"]
# arrNegativeSeedWords["hiệu năng"] = ["tệ"]
# #exception [ "" ]

arrPositiveSeedWords["chip"] = ["nhanh", "mát"]
arrNegativeSeedWords["chip"] = ["chậm", "nóng"]
#exception [ "" ]

arrPositiveSeedWords["sản xuất"] = ["công phu", "tỉ mỉ"]
arrNegativeSeedWords["sản xuất"] = ["kém"]
#exception [ "" ]

def generatePostiveFeatureAndPTCMD(type):
    ptcmdList = ptcmdArr[2]

    if type == "neural":
        # 10% generated 1, 70% generated 2
        # percentGeneratePTCMD = random.randint(1,3)
        # if (percentGeneratePTCMD == 1):
        #     ptcmdList = ptcmdArr[-1]
        # if (percentGeneratePTCMD == 2):
        #     ptcmdList = ptcmdArr[0]
        # if (percentGeneratePTCMD == 3):
        #     ptcmdList = ptcmdArr[1]
        ptcmdList = ptcmdArr[0]

    feature = random.choice(list(arrPositiveSeedWords.keys()))
    ptcmd = random.choice(ptcmdList)
    content = random.choice(list(arrPositiveSeedWords[feature]))
    # return '{} {} {}'.format(feature, ptcmd, content)
    return [feature, ptcmd, content]

def generateNegativeFeatureAndPTCMD(type):
    ptcmdList = ptcmdArr[2]

    if type == "neural":
        # 10% generated 1, 70% generated 2
        # percentGeneratePTCMD = random.randint(1,3)
        # if (percentGeneratePTCMD == 1):
        #     ptcmdList = ptcmdArr[-1]
        # if (percentGeneratePTCMD == 2):
        #     ptcmdList = ptcmdArr[0]
        # if (percentGeneratePTCMD == 3):
        #     ptcmdList = ptcmdArr[1]
        ptcmdList = ptcmdArr[0]

    feature = random.choice(list(arrNegativeSeedWords.keys()))
    ptcmd = random.choice(ptcmdList)
    content = random.choice(list(arrNegativeSeedWords[feature]))
    # return '{} {} {}'.format(feature, ptcmd, content)
    return [feature, ptcmd, content]


def generateSentence(type):
    maxFeature = 3
    posFeatures = random.randint(0, min(maxFeature, len(arrPositiveSeedWords.keys())) )
    negFeatures = min(maxFeature - posFeatures, len(arrNegativeSeedWords.keys()))
    if type == "neural":
        posFeatures = 1
        negFeatures = 1
    subject = random.choice(list(subjects))
    mobileName = random.choice(list(phones))
    # print("pos feature : ", posFeatures, "neg feature : ", negFeatures)

    #feature da~ sinh
    generatedFeature = []

    arrFeatureAndPTCMD = []
    while (posFeatures > 0):
        [feature, ptcmd, seedWord] = generatePostiveFeatureAndPTCMD(type)
        if feature not in generatedFeature:
            generatedFeature.append(feature) # them vao mang~ luu nhung thuoc tinh da dc sinh
            generatedSentence = '{} {} {}'.format(feature, ptcmd, seedWord)
            arrFeatureAndPTCMD.append(generatedSentence)
            posFeatures -= 1

    while (negFeatures > 0):
        [feature, ptcmd, seedWord] = generateNegativeFeatureAndPTCMD(type)
        if feature not in generatedFeature:
            generatedFeature.append(feature) # them vao mang~ luu nhung thuoc tinh da dc sinh
            generatedSentence = '{} {} {}'.format(feature, ptcmd, seedWord)
            arrFeatureAndPTCMD.append(generatedSentence)
            negFeatures -= 1

    #     nối các thuột tính để tạo ra câu
    # print(arrFeatureAndPTCMD)
    sentence = ",".join([str(x) for x in arrFeatureAndPTCMD])
    sentence = "{} {} {}".format(subject, mobileName, sentence)

    return sentence



def generateByType(type):
    # sentence = ""
    obj = {}
    while(True):
        sentence = generateSentence(type)
        obj = sentimentAnalyze.sentimentAnalysisExecute(sentence)
        score = sum(obj['score'])
        # print(obj['score'], sum(obj['score']))
        if type == "success":
            if score > 0:
                break
        elif type == "failure":
            if score < 0:
                break
        elif type == "neural":
            if score == 0:
                break


    print(type, score)
    return obj

def generator(db, amountOfSentence, type):
    idx = 0
    while idx < amountOfSentence:
        obj = generateByType(type)
        obj['label'] = obj['predict']
        del obj['predict']
        db.insert(obj)
        idx += 1

#train generator
def trainDataGenerator():
    trainDB = db.trainData2
    trainDB.delete_many({})
    generator(trainDB, 2000, "success")
    generator(trainDB, 2000, "failure")
    generator(trainDB, 2000, "neural")

#test generator
def testDataGenerator():
    testDB = db.testData
    testDB.delete_many({})
    generator(testDB, 100, "success")
    generator(testDB, 100, "failure")
    generator(testDB, 100, "neural")

trainDataGenerator()
# testDataGenerator()

# for s in seq:
#     print(s)

# for s in seq:
#     obj = {}
#     obj["content"] = s
#     generateSentenceDb.insert_one(obj)
#     # print(obj)