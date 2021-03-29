import requests
import xlrd
import re 
import csv
import time
import os
import multiprocessing
from multiprocessing import Manager

import hashlib
import json

class Event(object):
   def __init__(self, uid, time, _type, result_country, content, emotion,title,source,sentence,trigger,value):
       self.uid = uid  
       self.time = time
       self.type = _type
       self.result_country = result_country
       self.content = content
       self.emotion = emotion
       self.title = title
       self.source = source
       self.sentence = sentence
       self.trigger = trigger
       self.value = value

class Opinion(object):
   def __init__(self, uid, company, opinion,sentence):
       self.uid = uid
       self.company = company
       self.opinion = opinion
       self.sentence = sentence


def read_dictionary(pas,file):
    data = xlrd.open_workbook(pas+"/"+file)
    table = data.sheets()[0]
    nrows = table.nrows 

    trigger = []

    for i in range(1,nrows):
        row_detail = table.row_values(i)
        trigger.append(row_detail[0])
        trigger.append(row_detail[1])
        trigger.append(row_detail[2])
    
    while '' in trigger:
        trigger.remove("")

    return trigger

def read_excel_data(pas,file):
    data = xlrd.open_workbook(pas+"/"+file)
    table = data.sheets()[0]
    nrows = table.nrows 

    events = []

    for i in range(1,nrows):
        row_detail = table.row_values(i)

        row_detail[4] = re.sub(r'\s+', "", row_detail[4])
        row_detail[4] = re.sub(r'\#+', '。', str(row_detail[4]))
        row_detail[4] = re.sub(r'\：', '。', str(row_detail[4]))
        
        # event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[5][j+2],row_detail[3],row_detail[2])
        # print(event.result_type)
        event = Event(row_detail[0],row_detail[1],None,None,row_detail[4],None,row_detail[3],row_detail[2],None,None,None)
        events.append(event)


    return events

def read_csv_data(pas,file):
    events = []
    csv.field_size_limit(500 * 1024 * 1024)
    with open(pas+file, newline='') as f:
        reader = csv.reader(f)
        # i =0
        for row in reader:
            # if i > 1:
            #     break
            # print(row)
            # i += 1
            row[4] = re.sub(r'\s+', "", row[4])
            row[4] = re.sub(r'\#+', '。', str(row[4]))
            row[4] = re.sub(r'\：', '。', str(row[4]))

            event = Event(row[0],row[1],None,None,row[4],None,row[3],row[2],None,None,None)
            events.append(event)
    # print(len(events))
    return events


def pruning(string):
    index = string.find("，")
    # print(index)
    string = string[index+1:]

    return string

def extractOpinion(ori_events,opinions):
    # opinions = []
    for i in range(0,len(ori_events)):
        print("extract opinion "+str(i))
        uid = ori_events[i].uid
        text = ori_events[i].content

        url = "http://shenjiaosuo-sow-opinion.datagrand.com:10010/opinion"
        data = {'text':text}
        try:
            x = requests.post(url,data).text
            # print(x)
            opinion = Opinion(uid,None,None,None)
            if eval(x)["status"] == "FAIL" or len(eval(x)["opinions"]) == 0:
                opinions.append(opinion)
            else:
                for item in eval(x)["opinions"]:
                    # opinions = eval(x)["opinions"][0]
                    # print(result)
                    opinion.company = item["org"]
                    opinion.opinion = pruning(item["opinion"])
                    sentence = re.search('([^。]*('+opinion.opinion+')[^。]*)',ori_events[i].content)
                    opinion.sentence = sentence.group(0)
                    opinions.append(opinion)
        except:
            time.sleep(5)
    # for opinion in opinions:
    #     print(opinion.opinion)
    #     print(opinion.company)
    #     print(opinion.sentence)
    return opinions
# def extractOpinion(ori_event,opinions,i):
#     # opinions = []
#     # for i in range(0,len(ori_events)):
#         print("extract opinion "+str(i))
#         uid = ori_event.uid
#         text = ori_event.content

#         url = "http://shenjiaosuo-sow-opinion.datagrand.com:10010/opinion"
#         data = {'text':text}
#         try:
#             x = requests.post(url,data).text
#             # print(x)
#             opinion = Opinion(uid,None,None)
#             if eval(x)["status"] == "FAIL" or len(eval(x)["opinions"]) == 0:
#                 opinions.append(opinion)
#             else:
#                 for item in eval(x)["opinions"]:
#                     # opinions = eval(x)["opinions"][0]
#                     # print(result)
#                     opinion.company = item["org"]
#                     opinion.opinion = pruning(item["opinion"])
#                     opinions.append(opinion)
#         except:
#             time.sleep(5)

    # return opinion

def extractName(text):
    url = 'http://47.95.178.212:33006/api/kg-nlp/ner/predict'
    data = {'sentences':[text]}
    try:
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
    except:
        time.sleep(5)

    return target_name


def extractValue(text):
    url = "http://shenjiaosuo-sow-opinion.datagrand.com:10010/zhishu"
    # url = "http://100.100.22.2:10010/zhishu"
    data = {'text':text}
    try:
        x = requests.post(url,data).text
        values = []
        if eval(x)["status"] == "FAIL" or len(eval(x)["results"]) == 0:
            value = None
        else:
            for item in eval(x)["results"]:
                # result = eval(x)["results"][0]
                # print(result)
                value = ("").join(item["change"])
                values.append(value)
    except:
        time.sleep(5)
    
    return values



def extractEvent(ori_events,trigger,events):
    # events = []
    for i in range(0,len(ori_events)):
    # for i in range(70,80):
        sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',ori_events[i].content)
        
        for item in sentences:
            # print(item)
            if ori_events[i].title != item[0]:
                if len(list(item[0]))>6:
                    ori_events[i].sentence = item[0]
                    ori_events[i].trigger = item[1]
                # if extractValue(ori_events[i].trigger, ori_events[i].sentence):
                #     ori_events[i].value = extractValue(ori_events[i].trigger,ori_events[i].sentence)
                # if extractValue(ori_events[i].sentence):
                #     ori_events[i].value = extractValue(ori_events[i].sentence)
                # event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
                # print(extractValue(ori_events[i].sentence))
                if extractValue(ori_events[i].sentence):
                    values = extractValue(ori_events[i].sentence)
                    for value in values:
                        print("multi value")
                        ori_events[i].value = value
                        event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
                        events.append(event)

                else:
                    event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,None)
                    events.append(event)
            else:
                print(ori_events[i].title)
            
        print("extract event "+str(i))
    return events
# def extractEvent(ori_event,trigger,events,i):
#     # events = []
#     # for i in range(0,len(ori_events)):
#     # for i in range(70,80):
#     sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',ori_event.content)
    
#     index = 0
#     for item in sentences:
#         # print(item)
#         if ori_event.title != item[0]:
#             if len(list(item[0]))>6:
#                 ori_event.sentence = item[0]
#                 ori_event.trigger = item[1]
#             # if extractValue(ori_events[i].trigger, ori_events[i].sentence):
#             #     ori_events[i].value = extractValue(ori_events[i].trigger,ori_events[i].sentence)
#             # if extractValue(ori_events[i].sentence):
#             #     ori_events[i].value = extractValue(ori_events[i].sentence)
#             # event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
#             # print(extractValue(ori_events[i].sentence))
#             if extractValue(ori_event.sentence):
#                 values = extractValue(ori_event.sentence)
#                 for value in values:
#                     print("multi value")
#                     ori_event.value = value
#                     event = Event(ori_event.uid,ori_event.time, ori_event.type, ori_event.result_country, ori_event.content, ori_event.emotion,ori_event.title,ori_event.source,ori_event.sentence,ori_event.trigger,ori_event.value)
#                     event.index = index
#                     index += 1
#                     events.append(event)

#             else:
#                 event = Event(ori_event.uid,ori_event.time, ori_event.type, ori_event.result_country, ori_event.content, ori_event.emotion,ori_event.title,ori_event.source,ori_event.sentence,ori_event.trigger,None)
#                 event.index = index
#                 index += 1
#                 events.append(event)
#         else:
#             print(ori_event.title)
        
#         print("extract event "+str(i))
#     # return event

def get_md5(data):
    m5 = hashlib.md5()
    m5.update(json.dumps(data).encode())
    return m5.hexdigest()

def makeEventCSV(events):
    i=0
    for event in events:
        if event.trigger != None:
            i+=1
            print("write event "+str(i))
            if event.value:
                # csv_write.writerow(["V","trigger",event.uid+str(4*i+1),event.trigger, "时间", event.time, "值", event.value[0][2]])
                csv_write.writerow(["V","trigger",get_md5(str(event.sentence)+str(event.trigger))+'trigger',event.trigger, "时间", event.time, "值", event.value])
            else:
                csv_write.writerow(["V","trigger",get_md5(str(event.sentence)+str(event.trigger))+'trigger',event.trigger, "时间", event.time])
            # print(event.trigger)
            csv_write.writerow(["V","event",get_md5(event.sentence)+'event',event.sentence])
            # print(event.sentence)
            # csv_write.writerow(["V","time",event.uid+str(4*i+2),event.time])
            csv_write.writerow(["V","event_type",event.type,event.type])
            csv_write.writerow(["E","包含",get_md5(event.sentence)+'event',get_md5(str(event.sentence)+str(event.trigger))+'trigger'])
            csv_write.writerow(["E","属于",get_md5(event.sentence)+'event',event.type])

    return None


def makeOpinionCSV(opinions):
    i=0
    for opinion in opinions:
        i += 1
        print("write opinion "+str(i))
        if opinion.opinion != None:
            csv_write.writerow(["V","organization",opinion.company,opinion.company])
            csv_write.writerow(["V","opinion",opinion.uid+opinion.company+"opinion",opinion.opinion])
            name = extractName(opinion.sentence)
            if name != None:
                # print(name)
                csv_write.writerow(["V","人物",opinion.uid+opinion.company+"people",name])
                csv_write.writerow(["E","任职于",opinion.uid+opinion.company+"people",opinion.company])
                csv_write.writerow(["E","发表",opinion.uid+opinion.company+"people",opinion.uid+opinion.company+"opinion"])
            csv_write.writerow(["E","发布",opinion.company,opinion.uid+opinion.company+"opinion"])
                    
    return None

def makePoint2EventCSV(events,opinions):
    i=0
    for opinion in opinions:
        i += 1
        print("write opinion2event "+str(i))
        for event in events:
            if opinion.uid == event.uid and opinion.opinion != None and event.sentence != None:
                csv_write.writerow(["E","分析",opinion.uid+opinion.company+"opinion",get_md5(event.sentence)+'event'])
    return None



if __name__ == '__main__':
    events = []
    # max_cpu = os.cpu_count()
    ori_events = read_csv_data("./data/","unlabel_database_other_source.csv")

    # ori_events = read_csv_data("./","source_less.csv")
    # for event in events:
    #     print(event.uid)

    trigger = read_dictionary("./event","金融术语-经济指标.xlsx")
    # trigger = trigger[0:5]
    read_trigger = "|".join(trigger)

    events = extractEvent(ori_events,read_trigger,events)

    opinions = extractOpinion(ori_events,opinions=[])


    # manager = Manager()
    # return_list = manager.list() 也可以使用列表list
    # return_list = manager.list()
    
    
    # opinions = manager.list()
    # events = manager.list()

    # length = len(ori_events)//4

    # jobs = []

    # for i in range(4):
    #     for j in range(length):
    #         if i*length+j<len(ori_events):
    #             p = multiprocessing.Process(target=extractEvent, args=(ori_events[i*length+j],read_trigger,events,i*length+j))
    #             jobs.append(p)
    #             p.start()
    # for proc in opinions:
    #     proc.join()
    #     proc.close()


    # jobs = []
    # for i in range(4):
    #     for j in range(length):
    #         if i*length+j<len(ori_events):
    #             p = multiprocessing.Process(target=extractOpinion, args=(ori_events[i*length+j], opinions,i*length+j))
    #             jobs.append(p)
    #             p.start()
    # for proc in opinions:
    #     proc.join()
    #     proc.close()

    

    with open("Triple_other_source.csv",'w') as f:
        csv_write = csv.writer(f)

        makeEventCSV(events)
        makeOpinionCSV(opinions)
        makePoint2EventCSV(events, opinions)







