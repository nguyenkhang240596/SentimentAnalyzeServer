import pymongo
import math
import time
from pymongo import MongoClient
# uri = "mongodb://root:123@ds237669.mlab.com:37669/vnlp"
uri = "mongodb://127.0.0.1:27017/VNLP"

db = MongoClient(uri).get_database()

ptcmdCollection = db.PhoTuChiMucDo
wordsCollection = db.vnexpresses
seedWordsColection = db.SeedWords
compoundWordCollection = db.CompoundWord
corpusCollection = db.Corpus

def start():
    start_time = time.time()
    buildSeedWords()
    _time = time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time))
    print("====Done Build Seed Words in", _time,"====")
    buildPhoTuChiMucDo()
    _time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("====Done Build Pho Tu Chi Muc Do", _time,"====")
    buildCompoundWord()
    _time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("====Done Build Compound Word", _time,"====")
    buildCorpus()
    _time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("====Done Build Corpus", _time,"====")
    createIndexMongoDb()
    _time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("====Done All", _time,"====")

def buildSeedWords():
    # pin
    arrPositiveSeedWords = {}
    arrNegativeSeedWords = {}

    arrPositiveSeedWords["pin"] = ["cao", "trâu", "ngon", "tốt", "tiết kiệm", "mạnh", "khỏe", "khủng", "bền", "lớn",
                                   "ổn"]
    arrNegativeSeedWords["pin"] = ["thấp", "ngốn", "nóng", "kém", "yếu", "hao", "tốn", "xì", "phồng", "nổ", "cháy nổ"
        , "phù", "thốn", "lỗi", "nhanh hết"]

    arrPositiveSeedWords["ram"] = ["cao", "nhiều", "khủng"]
    arrNegativeSeedWords["ram"] = ["thấp", "ít"]

    arrPositiveSeedWords["cấu hình"] = ["ok", "okay", "khủng", "ổn"]
    arrNegativeSeedWords["cấu hình"] = ["thấp", "nản", "yếu"]

    arrPositiveSeedWords["màn hình"] = ["thời thượng", "sang trọng", "đẹp", "to", "bự", "lớn", "tốt"]
    arrNegativeSeedWords["màn hình"] = ["xấu", "kém", "nhỏ", "chói"]

    arrPositiveSeedWords["thiết kế"] = ["thời thượng", "sang trọng", "đẹp", "ổn", "mới", "sắc xảo", "công phu",
                                        "đổi mới"]
    arrNegativeSeedWords["thiết kế"] = ["xấu", "kém", "thô thiển", "cũ rích"]
    # exception [ "đẹp mê li", "

    arrPositiveSeedWords["kiểu dáng"] = ["đẹp", "ổn", "mới", "sắc xảo", "công phu", "đổi mới"]
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
    # exception [ "" ]

    arrPositiveSeedWords["sản xuất"] = ["công phu", "tỉ mỉ"]
    arrNegativeSeedWords["sản xuất"] = ["kém"]
    # exception [ "" ]

    seedWordsColection.drop()
    for feature in arrPositiveSeedWords:
        for word in arrPositiveSeedWords[feature]:
            seedWordsColection.update_one({"feature": feature, "synonyms": [], "content": word, "score": 1},
                                          {"$set": {"content": word, "score": 1}}, upsert=True)

    for feature in arrNegativeSeedWords:
        for word in arrNegativeSeedWords[feature]:
            seedWordsColection.update_one({"feature": feature, "synonyms": [], "content": word, "score": -1},
                                          {"$set": {"content": word, "score": -1}}, upsert=True)

def buildPhoTuChiMucDo():
    # Them pho tu chi muc do
    ptcmdCollection.drop()

    ptcmd = {}
    ptcmd[2] = ["siêu", "cực kỳ", "cực kì", "cực", "vô cùng", "kinh khủng", "hoàn toàn", "kinh hồn", "nhất"]
    ptcmd[1] = ["rất", "quá", "thật", "càng", "thật sự"]
    ptcmd[0] = ["không", "chẳng", "chả", "không được", "chả được", "chẳng được"]
    ptcmd[-1] = ["khá", "tạm", "tương đối", "hơn"]
    ptcmd[-2] = ["hơi", "cũng"]

    for score in ptcmd:
        for word in ptcmd[score]:
            # print("{} {}".format(word, score))
            ptcmdCollection.insert_one({"content": word, "score": score})

def buildCompoundWord():
    # Thêm phía trước seedwords
    compoundWordCollection.drop()
    # prefix, chèn các phó từ chỉ mức độ vào trước seedwords
    seedWords = seedWordsColection.find()
    for seedWord in seedWords:
        ptcmdWords = ptcmdCollection.find()
        for ptcmd in ptcmdWords:
            content = ptcmd["content"] + " " + seedWord["content"]
            # old version
            # emotionalValue = ptcmd["score"] * seedWord["score"]
            emotionalValue = ptcmd["score"]
            feature = seedWord["feature"]
            synonyms = seedWord["synonyms"]
            #         if ptcmd["content"] in "cực kỳ, cực kì, cực, vô cùng, rất, quá, thật":
            compoundWordCollection.insert_one(
                {"content": content, "feature": feature, "score": seedWord["score"], "synonyms": synonyms,
                 "emotionalValue": emotionalValue})
    # chèn các phó từ chỉ mức độ vào sau seedwords
    seedWords = seedWordsColection.find()
    for seedWord in seedWords:
        ptcmdWords = ptcmdCollection.find()
        for ptcmd in ptcmdWords:
            content = seedWord["content"] + " " + ptcmd["content"]
            feature = seedWord["feature"]
            synonyms = seedWord["synonyms"]
            if (ptcmd["score"] == 0):
                emotionalValue = ptcmd["score"]
            else:
                # Trung bình của 2 số nguyên liên tiếp là 0.5
                emotionalValue = ptcmd["score"] - 0.5
                #         if ptcmd["content"] in "cực kỳ, cực kì, cực, vô cùng, rất, quá, thật":
            compoundWordCollection.insert_one(
                {"content": content, "feature": feature, "score": seedWord["score"], "synonyms": synonyms,
                 "emotionalValue": emotionalValue})


def buildCorpus():
    corpusCollection.drop()
    alpha = [0.1]  # , 0.15, 0.2]
    # get Seed Words
    # b(1 + log2(1 + na))
    def calT(n, a):
        return 1 + math.log2((1 + n * a))

    for a in alpha:
        compoundWords = compoundWordCollection.find()
        seedWords = seedWordsColection.find()

        # chèn chính từ seedword vào với emotional value là 1
        for w in seedWords:
            corpusCollection.insert_one({"alpha": a, "weight": w["score"], "content": w["content"],
                                         "feature": w["feature"], "synonyms": w["synonyms"]})
        # tính giá trị cho các từ ghép
        for w in compoundWords:
            # score là giá trị của seedword
            # emotional là giá trị của phó từ chỉ mức độ
            # weight là giá trị cuối cùng, cho biết mức độ đánh giá
            weight = calT(w["emotionalValue"], a) * w["score"]
            # weight = calT(math.fabs(w["emotionalValue"]), a) * w["score"]
            corpusCollection.insert_one({"alpha": a, "weight": weight, "content": w["content"],
                                         "feature": w["feature"], "synonyms": w["synonyms"]})

def createIndexMongoDb():
    corpusCollection.create_index([('feature', pymongo.ASCENDING)])
    corpusCollection.create_index([('content', pymongo.ASCENDING)])
    corpusCollection.create_index([('content', pymongo.ASCENDING), ('feature', pymongo.ASCENDING)])


start()


