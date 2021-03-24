import os, re
import csv
import pandas as pd
import numpy as np
import requests

# import xlwt

def read_csv(pas,file): 
    ori_rows = pd.read_csv(pas+"/"+file)
    ori_rows = ori_rows.values.tolist()

    uid = []
    content = []
    all_opinions = []

    for row in ori_rows:
        uid.append(row[0])
        content.append(row[1])
        opinions = eval(row[2])

        all_opinions.append(opinions)

    return uid, all_opinions 

def pruning(string):
    index = string.find("，")
    # print(index)
    string = string[index+1:]

    return string


# return all organization
def all_organization(pas,file):
    uid, opinions = read_csv(pas,file)
    keys = []
    for item in opinions:
        keys+= list(item.keys())
    return keys

def extractName(text):
    url = 'http://47.95.178.212:33006/api/kg-nlp/ner/predict'
    data = {'sentences':[text]}
    result = requests.post(url,data).text
    result = eval(result[1:-2])
    index = 0
    if "position" in result["label"].keys():
        position = result["label"]["position"].values()
        index = list(position)[0][0][1]

    if "name" not in result["label"]:
        return None

    names_dic = result["label"]["name"]
    names = names_dic.keys()
    min_delta = 10000
    for name in names:
        name_index = names_dic[name][0][1]
        delta = abs(index-name_index)
        if delta < min_delta:
            target_name = name
            min_delta = delta

    return target_name



    

if __name__ == '__main__':
    uid, opinions = read_csv(".","市场观点提取20210222.csv")
    i = 0
    length = len(opinions)
    # count = 0

    with open("opinionTriples.csv",'w') as f:
        csv_write = csv.writer(f)
        while i < length:
            print(i)
            dic = opinions[i]
            keys = list(dic.keys())
            # print(keys) 
            j = 0
            while j < len(keys):
                # len(keys)
                k = 0
                # print(dic[keys[j]])
                while k < len(dic[keys[j]]):
                    # len(dic[keys[j]])
                    csv_write.writerow(["V","organization",str(keys[j]),str(keys[j])])
                    opinion = str(dic[keys[j]][k])
                    csv_write.writerow(["V","opinion",uid[i]+str(keys[j])+str(opinion),pruning(opinion)])
                    name = extractName(opinion)
                    if name != None:
                        csv_write.writerow(["V","人物",uid[i]+str(keys[j])+"people",name])
                        csv_write.writerow(["E","任职于",uid[i]+str(keys[j])+"people",str(keys[j])])
                        csv_write.writerow(["E","发表",uid[i]+str(keys[j])+"people",uid[i]+str(keys[j])+str(opinion)])
                    csv_write.writerow(["E","发布",str(keys[j]),uid[i]+str(keys[j])+str(opinion)])
                    
                    k += 1
                j += 1
            i += 1


