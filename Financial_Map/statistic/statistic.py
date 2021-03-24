import xlrd
import re 
import csv
import xlwt

# 1.1

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
        row_detail[5] = re.sub(r'\[', ' ', str(row_detail[5]))
        row_detail[5] = re.sub(r'\]', '+', str(row_detail[5]))
        row_detail[5] = re.sub(r'\,', ' ', str(row_detail[5]))
        row_detail[5] = re.sub(r'\'', ' ', str(row_detail[5]))
        row_detail[4] = re.sub(r'\#+', '。', str(row_detail[4]))
        row_detail[4] = re.sub(r'\：', '。', str(row_detail[4]))
        row_detail[5] = row_detail[5].split()
        j = 0
        # event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[5][j+2],row_detail[3],row_detail[2])
        # print(event.result_type)
        while j < len(row_detail[5]):

            event = Event(row_detail[0],row_detail[1],row_detail[5][j+1],row_detail[5][j],row_detail[4],row_detail[5][j+2],row_detail[3],row_detail[2],None,None,None)
            j += 4
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

if __name__ == '__main__':
    events = read_data(".","舆情事件及情感识别.xlsx")
    trigger = read_dictionary(".","金融术语-经济指标.xlsx")
    read_trigger = "|".join(trigger)
    for i in range(0,len(events)):
        sentences = re.findall('([^。]*('+read_trigger+')[^。]*)',events[i].content)
        for item in sentences:
            events[i].sentence = item[0]
            events[i].trigger = item[1]
            # print(item[1])

    
    # # type
    statistic = {}
    for event in events:
        if event.type in statistic.keys():
            statistic[event.type] += 1
        else:
            statistic[event.type] = 1
    # trigger
    statistic_trigger = {}
    for event in events:
        if event.trigger in statistic_trigger.keys():
            statistic_trigger[event.trigger] += 1
        else:
            statistic_trigger[event.trigger] = 1



    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('sheet')

#type
    i = 0
    worksheet.write(i,0,"event1.1 type")
    worksheet.write(i,1,len(events))
    i+=1
    for key in statistic.keys():
        worksheet.write(i,0,key)
        worksheet.write(i,1,statistic[key])
        i+=1
    

# trigger
    
    i = 0
    worksheet.write(i,3,"event1.1 trigger")
    worksheet.write(i,4,len(events))
    i+=1
    for key in statistic_trigger.keys():
        
        worksheet.write(i,3,key)
        worksheet.write(i,4,statistic_trigger[key])
        i+=1
  
    workbook.save('1.1type_Frequency.xls')