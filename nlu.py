from os import path
import mysql.connector
import os
import sys
import json
import hashlib
import re
from datetime import datetime
from ibm_watson import NaturalLanguageUnderstandingV1, ToneAnalyzerV3
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, \
    RelationsOptions, SemanticRolesOptions, SentimentOptions, CategoriesOptions, SyntaxOptions, SyntaxOptionsTokens, EmotionOptions, ConceptsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

dir = "/nlu_profiling/"

maxtry = 5
mess = ""
agent = ""

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="profiles"
)

# https://www.w3schools.com/python/python_mysql_select.asp
mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM userprofiles")
# myresult = mycursor.fetchall()
# for x in myresult:
#   print(x)


def nluprocess(row):
    id = row['id']
    eng = row['translate']
    text = str(eng)
    authenticator = IAMAuthenticator(
        # '4s7xVwXOhKwKLjM4y9-vasVtpuEr5QmvCc_WQDO-R5mD')
        'vPVyH_y3yJXfpaYGrrsJDRTQ1iDz8RLqEmkVCMU6TkSk')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator)
    natural_language_understanding.set_service_url(
        # 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/85a62114-d5a4-43c5-9946-3ae7747b7fe5')
        'https://api.kr-seo.natural-language-understanding.watson.cloud.ibm.com/instances/08d2ddb8-ea63-4e22-af5c-8f3ef90b2a32')
    print("nlu")
    response = natural_language_understanding.analyze(
        text=text,
        language='en',
        features=Features(
            entities=EntitiesOptions(emotion=True, sentiment=True, limit=20),
            keywords=KeywordsOptions(emotion=True, sentiment=True, limit=20),
            relations=RelationsOptions(),
            categories=CategoriesOptions(limit=20),
            concepts=ConceptsOptions(limit=20),
            # metadata=MetadataOptions(),
            semantic_roles=SemanticRolesOptions(),
            sentiment=SentimentOptions(document=True),
            emotion=EmotionOptions(document=True),
            syntax=SyntaxOptions(sentences=True, tokens=SyntaxOptionsTokens(
                lemma=True, part_of_speech=True))
        )).get_result()
    if response["language"] == "en":
    filler = {
        "syntax": {"tokens": [{"text": "", "part_of_speech": "", "location": [], "lemma":""}], "sentences": [{"text": "", "location": []}]},
        "sentiment": {"document": {"score": 0, "label": ""}},
        "semantic_roles": [{"subject": {"text": ""}, "sentence": "", "object": {"text": ""}, "action": {"verb": {"text": "", "tense": ""}, "text": "", "normalized": ""}}],
        "relations": [{"type": "", "sentence": "", "score": 0, "arguments": [{"text": "", "location": [], "entities":[{"type": "", "text": ""}]}]}],
        "keywords": [{"text": "", "sentiment": {"score": 0, "label": ""}, "relevance": 0, "emotion": {"sadness": 0, "joy": 0, "fear": 0, "disgust": 0, "anger": 0}, "count": 0}],
        "entities": [{"type": "", "text": "", "sentiment": {"score": 0, "label": "0"}, "relevance": 0, "emotion": {"sadness": 0, "joy": 0, "fear": 0, "disgust": 0, "anger": 0}, "count": 0, "confidence": 0}],
        "emotion": {"document": {"emotion": {"sadness": 0, "joy": 0, "fear": 0, "disgust": 0, "anger": 0}}},
        "concepts": [{"text": "", "relevance": 0, "dbpedia_resource": ""}],
        "categories": [{"score": 0, "label": ""}]
    }
    response["empty"] = []
    if 'warnings' in response:
    for val in response["warnings"]:
    key = val.split(":")
    response[key[0]] = filler[key[0]]
    response["empty"].append(key[0])
    del response['warnings']
    con = json.dumps(response)
    con = con.replace("&apos;", " ")
    con = con.replace("'", "&apos;")
    sq = "UPDATE userprofiles SET nlu_translate='{}', status_nlu=TRUE WHERE id={}".format(
        con, id)
    mycursor.execute(sq)
    mess += "[DONE] ~> "
    return con
    else:
    mess += "[FAIL] ~> "
    return "0"


if __name__ == "__main__":
    args = len(sys.argv)
    if args == 2:
        agent = sys.argv[1]
        if not path.exists(dir + "/flag.txt"):
            f = open(dir + "/flag.txt", "w")
            f.write("wowowowoooww! i have deleted!")
            f.close()
            sql = "SELECT * FROM userprofiles WHERE nlu_status=Null ORDER BY id ASC limit 1"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            while row is not None:
                mess = ""
                i = 0
                n = nluprocess(row)
                while n == "0" and i < maxtry:
                    i += 1
                    n = nluprocess(row)
                    print(mess)
                    now = datetime.now()
                    os.remove(dir + "/flag.txt")
                    # if n != "0":
                    # 	row['translate'] = n
                    # 	i = 0
