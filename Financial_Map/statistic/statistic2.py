import xlrd
import re 
import csv
import xlwt
class Event(object):
   def __init__(self, uid, time, content, title, _type, sentence, trigger, value):
       self.uid = uid  
       self.time = time
       self.content = content
       self.title = title
       self.type = _type
       self.sentence = sentence
       self.trigger = trigger
       self.value = value
    

def read_data(pas,file):
    csv_reader = csv.reader(open(pas +"/"+ file))
    events = []
    for line in csv_reader:
        events.append(line)
    return events

if __name__ == '__main__':
    events = []
    events2 = []
    # input1 = read_data(".","zhibiao_extract.csv")
    # i = 0
    # for i in range(1,len(input1)):
    #     event = Event(input1[i][0],None,input1[i][1],None,None,input1[i][2],input1[i][3],input1[i][6])
    #     events.append(event)
    # print(len(events))

    # input2 = read_data(".","1.2.1_result.csv")
    # i = 0
    # for i in range(1,len(input2)):
    #     for event in events:
    #         if event.uid == input2[i][0] and re.search(event.trigger , input2[i][3]):
    #             event.time = input2[i][1]
    #             event.title = input2[i][2]
    #             event.type = input2[i][4]
    #     i+=1
    input1 = read_data(".","1.2.1_result.csv")
    i = 0
    for i in range(1,len(input1)):
        event = Event(None,input1[i][1],None,input1[i][2],input1[i][4],None,None,None)
        events.append(event)
    # print(len(events))

    input2 = read_data(".","zhibiao_extract.csv")
    i = 0
    for i in range(1,len(input2)):
        event = Event(input2[i][0],None,input2[i][1],None,None,input2[i][2],input2[i][3],input2[i][6])
        events2.append(event)



    # # type
    statistic = {}
    for event in events:
        if event.type in statistic.keys():
            statistic[event.type] += 1
        else:
            statistic[event.type] = 1

    
    # trigger
    statistic_trigger = {}
    for event in events2:
        if event.trigger in statistic_trigger.keys():
            statistic_trigger[event.trigger] += 1
        else:
            statistic_trigger[event.trigger] = 1


    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('sheet')

#type
    i = 0
    worksheet.write(i,0,"event1.2 type")
    worksheet.write(i,1,len(events))
    i+=1
    for key in statistic.keys():
        worksheet.write(i,0,key)
        worksheet.write(i,1,statistic[key])
        i+=1
    
# trigger
    
    i = 0
    worksheet.write(i,3,"event1.2 trigger")
    worksheet.write(i,4,len(events2))
    i+=1
    for key in statistic_trigger.keys():
        worksheet.write(i,3,key)
        worksheet.write(i,4,statistic_trigger[key])
        i+=1
   

    workbook.save('1.2type_Frequency.xls')