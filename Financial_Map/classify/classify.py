import xlrd
import re 
import csv
import xlwt

class Event(object):
   def __init__(self, uid, time, _type, result_country, content, title,sentence,trigger,value,classify):
       self.uid = uid  
       self.time = time
       self.type = _type
       self.result_country = result_country
       self.content = content
       self.title = title
       self.sentence = sentence
       self.trigger = trigger
       self.value = value
       self.classify = classify

def read_data1(pas,file):
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

        if len(row_detail[5])!=0:
            j = 0
            country_index = []
            while j < len(row_detail[5]):
                if row_detail[5][j] not in country_index:
                    country_index.append(j)
                j+=4
            for j in country_index:
                event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[3],None,None,None,None)
            # j += 4
            events.append(event)
        else:
            event = Event(row_detail[0],row_detail[1],None,None,row_detail[4],row_detail[3],None,None,None,None)
            events.append(event)

    return events

def read_dictionary(pas,file):
    data = xlrd.open_workbook(pas+"/"+file)
    table = data.sheets()[0]
    nrows = table.nrows 

    trigger = []

    for i in range(1,nrows):
        row_detail = table.row_values(i)
        row_detail[0] = re.sub(r'\s+', "", row_detail[0])
        row_detail[1] = re.sub(r'\s+', "", row_detail[1])
        row_detail[2] = re.sub(r'\s+', "", row_detail[2])

        trigger.append(row_detail[0])
        trigger.append(row_detail[1])
        trigger.append(row_detail[2])
    
    while '' in trigger:
        trigger.remove("")

    return trigger

def extractValue(trigger,sentence):
    # zhibiao_origin = read_dictionary(pas,file)
    key_word = ['涨','跌','反弹','收高','上升','为','增长','下降','降低','达到','总额','升高']
    zhibiao_rule = str(trigger)
    key_word = "|".join(key_word)

    result = []
    find_name_sentence = re.findall('((' + zhibiao_rule + ')[^ ，。；】\s]*)', str(sentence))
    find_name_all = re.findall('(' + zhibiao_rule + ')', str(sentence))
    if find_name_all:
        for find_name in find_name_all:
            find_key_word = re.findall('((' + key_word + ')[^ ，。；】？！\s]*)', find_name_sentence[0][0])
            if find_key_word:
                find_index = re.findall('[\d.]+[%点美元分亿万百]+', find_key_word[0][0])
                if find_index:
                    result.append([find_name_sentence[0][0], find_name, find_key_word[0][1]+find_index[0]])
                else:
                    result.append([find_name_sentence[0][0], find_name, find_key_word[0][1]])

    return result

def read_data2(pas,file):
    csv_reader = csv.reader(open(pas +"/"+ file))
    events = []
    for line in csv_reader:
        events.append(line)
    return events

if __name__ == '__main__':
    all_events = []
    events = []
    ori_events = read_data1(".","舆情事件及情感识别.xlsx")
    # for event in events:
    #     print(event.uid)

    trigger = read_dictionary(".","金融术语-经济指标.xlsx")
    # trigger = trigger[0:5]
    read_trigger = "|".join(trigger)

    for i in range(0,len(ori_events)):
    # for i in range(70,80):
        sentences = re.findall('([^。；，]*('+read_trigger+')[^。；，]*)',ori_events[i].content)
        # print((str(ori_events[i].title),"title"))
        # print("***"*4)
        for item in sentences:
            # print(item)
            if ori_events[i].title != item[0]:
                if len(list(item[0]))>6:
                    ori_events[i].sentence = item[0]
                    ori_events[i].trigger = item[1]
                # if extractValue(ori_events[i].trigger,ori_events[i].sentence):
                #     ori_events[i].value = extractValue(ori_events[i].trigger,ori_events[i].sentence)
                event = Event(ori_events[i].uid,ori_events[i].time, ori_events[i].type, ori_events[i].result_country, ori_events[i].content,ori_events[i].title,ori_events[i].sentence,ori_events[i].trigger,None,None)
                events.append(event)
        print(i)
    all_events = events

    events = []
    input1 = read_data2(".","zhibiao_extract.csv")
    i = 0
    for i in range(1,len(input1)):
        event = Event(input1[i][0],None,None,None,input1[i][1],None,input1[i][2],input1[i][3],input1[i][6],None)
        events.append(event)

    input2 = read_data2(".","1.2.1_result.csv")
    print("input finish")
    i = 0
    for i in range(1,len(input2)):
        for event in events:
            if event.uid == input2[i][0] and re.search(str(event.trigger) , input2[i][3]):
                event.time = input2[i][1]
                event.title = input2[i][2]
                event.type = input2[i][4]
            # print(i)
        i+=1
    print("finish2")
    print(len(all_events))
    all_events += events
    print(len(all_events))


    country_triggers = read_dictionary(".","国家地区.xlsx")

    for event in all_events:
        if event.result_country in country_triggers:
            event.classify = "今日关注，欧美市场"
        elif event.trigger!=None:
            if event.result_country == None:
                for trigger in country_triggers:
                    if trigger in event.sentence:
                        event.result_country = trigger
                        event.classify = "今日关注，欧美市场"
                    else:
                        event.result_country = "中国"
                        event.classify = "今日关注"
            else:
                event.classify = "今日关注"
        print(event.classify)
    

    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('sheet')
    worksheet.write(0,0,"uid")
    worksheet.write(0,1,"sentence")
    worksheet.write(0,2,"country")
    worksheet.write(0,3,"classify")
    i = 1
    for event in all_events:
        if event.sentence != None:
            worksheet.write(i,0,event.uid)
            worksheet.write(i,1,event.sentence)
            worksheet.write(i,2,event.result_country)
            worksheet.write(i,3,event.classify)
            print(i)
            i+=1

        workbook.save('classify.xls')

