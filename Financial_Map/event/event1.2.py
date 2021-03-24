import xlrd
import re 
import csv

class Event(object):
    #  uid, time, _type, result_country, content, title,sentence,trigger,value):
   def __init__(self, uid, time, content, title, _type, sentence, trigger, value):
       self.uid = uid  
       self.time = time
       self.content = content
       self.title = title
       self.type = _type
       self.sentence = sentence
       self.trigger = trigger
       self.value = value

# class Event(object):
#    def __init__(self, uid, time, _type, result_country, content, emotion,title,source,sentence,trigger,value):
#        self.uid = uid  
#        self.time = time
#        self.type = _type
#        self.result_country = result_country
#        self.content = content
#        self.emotion = emotion
#        self.title = title
#        self.source = source
#        self.sentence = sentence
#        self.trigger = trigger
#        self.value = value
    

def read_data(pas,file):
    csv_reader = csv.reader(open(pas +"/"+ file))
    events = []
    for line in csv_reader:
        events.append(line)
    return events

if __name__ == '__main__':
    events = []
    input1 = read_data(".","zhibiao_extract.csv")
    i = 0
    for i in range(1,len(input1)):
        event = Event(input1[i][0],None,input1[i][1],None,None,input1[i][2],input1[i][3],input1[i][6])
        events.append(event)

    input2 = read_data(".","1.2.1_result.csv")
    i = 0
    for i in range(1,len(input2)):
        for event in events:
            if event.uid == input2[i][0] and re.search(event.trigger , input2[i][3]):
                event.time = input2[i][1]
                event.title = input2[i][2]
                event.type = input2[i][4]
        i+=1
    
    with open("Triples_Event2.csv",'w') as f:
        csv_write = csv.writer(f)
        i= 0
        for event in events:
            if event.trigger != None:
                i += 1
                csv_write.writerow(["V","event",event.uid+str(event),event.sentence])
                csv_write.writerow(["V","trigger",event.uid+"trigger",event.trigger,"时间",event.time,"值",event.value])
                # csv_write.writerow(["V","time",event.uid+str(4*i+2),event.time])
                # csv_write.writerow(["V","value",event.uid+str(4*i+3),event.value])
                csv_write.writerow(["V","event_type",event.type,event.type])
                csv_write.writerow(["E","包含",event.uid+str(event),event.uid+"trigger"])
                csv_write.writerow(["E","属于",event.uid+str(event),event.type])

                # csv_write.writerow(["E","值",event.uid+str(4*i+1),event.uid+str(4*i+3)])
                # csv_write.writerow(["E","时间",event.uid+str(4*i+1),event.uid+str(4*i+2)])

    



