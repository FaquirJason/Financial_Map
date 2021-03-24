import xlrd
import re 
import csv
import requests


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

   

def read_data(pas,file):
    data = xlrd.open_workbook(pas+"/"+file)
    table = data.sheets()[0]
    nrows = table.nrows 

    events = []

    for i in range(1,nrows):
        row_detail = table.row_values(i)
        row_detail[5] = row_detail[5][1:-1]
        row_detail[5] = re.sub(r'\s+', "", row_detail[5])
        row_detail[4] = re.sub(r'\s+', "", row_detail[4])
        row_detail[5] = re.sub(r'\[', ' ', str(row_detail[5]))
        row_detail[5] = re.sub(r'\]', '+', str(row_detail[5]))
        row_detail[5] = re.sub(r'\,', ' ', str(row_detail[5]))
        row_detail[5] = re.sub(r'\'', ' ', str(row_detail[5]))
        row_detail[4] = re.sub(r'\#+', '。', str(row_detail[4]))
        row_detail[4] = re.sub(r'\：', '。', str(row_detail[4]))
        row_detail[5] = row_detail[5].split()
        
        # event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[5][j+2],row_detail[3],row_detail[2])
        # print(event.result_type)
        if len(row_detail[5])!=0:
            j = 0
            while j < len(row_detail[5]):

                event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[5][j+2],row_detail[3],row_detail[2],None,None,None)
                j += 4
                events.append(event)
        else:
            event = Event(row_detail[0],row_detail[1],None,None,row_detail[4],None,row_detail[3],row_detail[2],None,None,None)
            events.append(event)


    return events

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



def extractValue(text):
    url = "http://shenjiaosuo-sow-opinion.datagrand.com:10010/zhishu"
    # url = "http://100.100.22.2:10010/zhishu"
    data = {'text':text}
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
    return values



# def extractEvent(ori_events,trigger):
#     events = []
#     for i in range(0,len(ori_events)):
#     # for i in range(70,80):
#         sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',ori_events[i].content)
#         # print((str(ori_events[i].title),"title"))
#         # print("***"*4)
#         for item in sentences:
#             # print(item)
#             if ori_events[i].title != item[0]:
#                 if len(list(item[0]))>6:
#                     ori_events[i].sentence = item[0]
#                     ori_events[i].trigger = item[1]
#                 # if extractValue(ori_events[i].trigger, ori_events[i].sentence):
#                 #     ori_events[i].value = extractValue(ori_events[i].trigger,ori_events[i].sentence)
#                 # if extractValue(ori_events[i].sentence):
#                 #     ori_events[i].value = extractValue(ori_events[i].sentence)
#                 # event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
#                 if extractValue(ori_events[i].sentence):
#                     values = extractValue(ori_events[i].sentence)
#                     for value in values:
#                         print("multi value")
#                         ori_events[i].value = value
#                         event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
#                         events.append(event)

#                 else:
#                     event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,None)
#                     events.append(event)
#             else:
#                 print(ori_events[i].title)
            
#         print(i)
#     return events

def extractEvent(ori_events,trigger):
    events = []
    for i in range(0,len(ori_events)):
    # for i in range(70,80):
        sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',ori_events[i].content)
        # print((str(ori_events[i].title),"title"))
        # print("***"*4)
        index = 0
        for item in sentences:
            print(item[0:5])
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
                if extractValue(ori_events[i].sentence):
                    values = extractValue(ori_events[i].sentence)
                    for value in values:
                        print("multi value")
                        ori_events[i].value = value
                        event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,ori_events[i].value)
                        event.index = index
                        index += 1
                        events.append(event)

                else:
                    event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content, ori_events[i].emotion,ori_events[i].title,ori_events[i].source,ori_events[i].sentence,ori_events[i].trigger,None)
                    event.index = index
                    index += 1
                    events.append(event)
            else:
                print(ori_events[i].title)
            
        print("extract event "+str(i))
    return events


# def extractValue(trigger,sentence):
#     # zhibiao_origin = read_dictionary(pas,file)
#     key_word = ['涨','跌','反弹','收高','上升','为','增长','下降','降低','达到','总额','升高']
#     zhibiao_rule = str(trigger)
#     key_word = "|".join(key_word)

#     result = []
#     find_name_sentence = re.findall('((' + zhibiao_rule + ')[^ ，。；】\s]*)', str(sentence))
#     find_name_all = re.findall('(' + zhibiao_rule + ')', str(sentence))
#     if find_name_all:
#         for find_name in find_name_all:
#             find_key_word = re.findall('((' + key_word + ')[^ ，。；】？！\s]*)', find_name_sentence[0][0])
#             if find_key_word:
#                 find_index = re.findall('[\d.]+[%点美元分亿万百]+', find_key_word[0][0])
#                 if find_index:
#                     result.append([find_name_sentence[0][0], find_name, find_key_word[0][1]+find_index[0]])
#                 else:
#                     result.append([find_name_sentence[0][0], find_name, find_key_word[0][1]])

#     return result

def makeCSV(events):
    
    # i=0
    # for event in events:
    #     if event.trigger != None:
    #         i+=1
    #         if event.value:
    #             # csv_write.writerow(["V","trigger",event.uid+str(4*i+1),event.trigger, "时间", event.time, "值", event.value[0][2]])
    #             csv_write.writerow(["V","trigger",event.uid+str(trigger),event.trigger, "时间", event.time, "值", event.value])
    #         else:
    #             csv_write.writerow(["V","trigger",event.uid+str(trigger),event.trigger, "时间", event.time])
    #         # print(event.trigger)
    #         csv_write.writerow(["V","event",event.uid+str(event),event.sentence])
    #         # print(event.sentence)
    #         # csv_write.writerow(["V","time",event.uid+str(4*i+2),event.time])
    #         csv_write.writerow(["V","event_type",event.type,event.type])
    #         csv_write.writerow(["E","包含",event.uid+str(event),event.uid+str(trigger)])
    #         csv_write.writerow(["E","属于",event.uid+str(event),event.type])

    with open("Triples_Event1.1.1.csv",'w',encoding= 'utf-8-sig') as f:
        csv_write = csv.writer(f)
        for event in events:
            if event.trigger != None:
                csv_write.writerow(["event",event.trigger,event.sentence])
                csv_write.writerow(["content",event.content])
                csv_write.writerow([])
    return None

if __name__ == '__main__':
    # events = []
    ori_events = read_data(".","舆情事件及情感识别.xlsx")
    # for event in events:
    #     print(event.uid)

    trigger = read_dictionary(".","金融术语-经济指标.xlsx")
    # trigger = trigger[0:5]
    read_trigger = "|".join(trigger)

    events = extractEvent(ori_events,read_trigger)

    # with open("Triples_Event1.csv",'w') as f:
    # with open("Triples_Event1.1.2.2.csv",'w',encoding="utf-8-sig") as f:
        # csv_write = csv.writer(f)
   
    makeCSV(events)

