import re, jieba
import jieba.posseg as pseg
from pyltp import SentenceSplitter
import xlrd
import csv
import time
import requests

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
       self.index = 0

class CausalityExractor():
    def __init__(self):
        pass

    '''1由果溯因配套式'''
    def ruler1(self, sentence):
        '''
        conm2:〈[之]所以,因为〉、〈[之]所以,由于〉、 <[之]所以,缘于〉
        conm2_model:<Conj>{Effect},<Conj>{Cause}
        '''
        datas = list()
        word_pairs =[['之?所以', '因为'], ['之?所以', '由于'], ['之?所以', '缘于']]
        for word in word_pairs:
            pattern = re.compile(r'\s?(%s)/[p|c]+\s(.*)(%s)/[p|c]+\s(.*)' % (word[0], word[1]))
            result = pattern.findall(sentence)
            data = dict()
            if result:
                data['tag'] = result[0][0] + '-' + result[0][2]
                data['cause'] = result[0][3]
                data['effect'] = result[0][1]
                datas.append(data)
        if datas:
            return datas[0]
        else:
            return {}
    '''2由因到果配套式'''
    def ruler2(self, sentence):
        '''
        conm1:〈因为,从而〉、〈因为,为此〉、〈既[然],所以〉、〈因为,为此〉、〈由于,为此〉、〈只有|除非,才〉、〈由于,以至[于]>、〈既[然],却>、
        〈如果,那么|则〉、<由于,从而〉、<既[然],就〉、〈既[然],因此〉、〈如果,就〉、〈只要,就〉〈因为,所以〉、 <由于,于是〉、〈因为,因此〉、
         <由于,故〉、 〈因为,以致[于]〉、〈因为,因而〉、〈由于,因此〉、<因为,于是〉、〈由于,致使〉、〈因为,致使〉、〈由于,以致[于] >
         〈因为,故〉、〈因[为],以至[于]>,〈由于,所以〉、〈因为,故而〉、〈由于,因而〉
        conm1_model:<Conj>{Cause}, <Conj>{Effect}
        '''
        datas = list()
        word_pairs =[['因为', '从而'], ['因为', '为此'], ['既然?', '所以'],
                    ['因为', '为此'], ['由于', '为此'], ['除非', '才'],
                    ['只有', '才'], ['由于', '以至于?'], ['既然?', '却'],
                    ['如果', '那么'], ['如果', '则'], ['由于', '从而'],
                    ['既然?', '就'], ['既然?', '因此'], ['如果', '就'],
                    ['只要', '就'], ['因为', '所以'], ['由于', '于是'],
                    ['因为', '因此'], ['由于', '故'], ['因为', '以致于?'],
                    ['因为', '以致'], ['因为', '因而'], ['由于', '因此'],
                    ['因为', '于是'], ['由于', '致使'], ['因为', '致使'],
                    ['由于', '以致于?'], ['因为', '故'], ['因为?', '以至于?'],
                    ['由于', '所以'], ['因为', '故而'], ['由于', '因而']]

        for word in word_pairs:
            pattern = re.compile(r'\s?(%s)/[p|c]+\s(.*)(%s)/[p|c]+\s(.*)' % (word[0], word[1]))
            result = pattern.findall(sentence)
            data = dict()
            if result:
                data['tag'] = result[0][0] + '-' + result[0][2]
                data['cause'] = result[0][1]
                data['effect'] = result[0][3]
                datas.append(data)
        if datas:
            return datas[0]
        else:
            return {}
    '''3由因到果居中式明确'''
    def ruler3(self, sentence):
        '''
        cons2:于是、所以、故、致使、以致[于]、因此、以至[于]、从而、因而
        cons2_model:{Cause},<Conj...>{Effect}
        '''

        pattern = re.compile(r'(.*)[,，]+.*(于是|所以|故|致使|以致于?|因此|以至于?|从而|因而)/[p|c]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
        return data
    '''4由因到果居中式精确'''
    def ruler4(self, sentence):
        '''
        verb1:牵动、导向、使动、导致、勾起、引入、指引、使、予以、产生、促成、造成、引导、造就、促使、酿成、
            引发、渗透、促进、引起、诱导、引来、促发、引致、诱发、推进、诱致、推动、招致、影响、致使、滋生、归于、
            作用、使得、决定、攸关、令人、引出、浸染、带来、挟带、触发、关系、渗入、诱惑、波及、诱使
        verb1_model:{Cause},<Verb|Adverb...>{Effect}
        '''
        pattern = re.compile(r'(.*)\s+(牵动|已致|导向|使动|导致|勾起|引入|指引|使|予以|产生|促成|造成|引导|造就|促使|酿成|引发|渗透|促进|引起|诱导|引来|促发|引致|诱发|推进|诱致|推动|招致|影响|致使|滋生|归于|作用|使得|决定|攸关|令人|引出|浸染|带来|挟带|触发|关系|渗入|诱惑|波及|诱使)/[d|v]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
        return data
    '''5由因到果前端式模糊'''
    def ruler5(self, sentence):
        '''
        prep:为了、依据、为、按照、因[为]、按、依赖、照、比、凭借、由于
        prep_model:<Prep...>{Cause},{Effect}
        '''
        pattern = re.compile(r'\s?(为了|依据|按照|因为|因|按|依赖|凭借|由于)/[p|c]+\s(.*)[,，]+(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][0]
            data['cause'] = result[0][1]
            data['effect'] = result[0][2]

        return data

    '''6由因到果居中式模糊'''
    def ruler6(self, sentence):
        '''
        adverb:以免、以便、为此、才
        adverb_model:{Cause},<Verb|Adverb...>{Effect}
        '''
        pattern = re.compile(r'(.*)(以免|以便|为此|才)\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
        return data

    '''7由因到果前端式精确'''
    def ruler7(self, sentence):
        '''
        cons1:既[然]、因[为]、如果、由于、只要
        cons1_model:<Conj...>{Cause},{Effect}
        '''
        pattern = re.compile(r'\s?(既然?|因|因为|如果|由于|只要)/[p|c]+\s(.*)[,，]+(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][0]
            data['cause'] = result[0][1]
            data['effect'] = result[0][2]
        return data
    '''8由果溯因居中式模糊'''
    def ruler8(self, sentence):
        '''
        3
        verb2:根源于、取决、来源于、出于、取决于、缘于、在于、出自、起源于、来自、发源于、发自、源于、根源于、立足[于]
        verb2_model:{Effect}<Prep...>{Cause}
        '''

        pattern = re.compile(r'(.*)(根源于|取决|来源于|出于|取决于|缘于|在于|出自|起源于|来自|发源于|发自|源于|根源于|立足|立足于)/[p|c]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][2]
            data['effect'] = result[0][0]
        return data
    '''9由果溯因居端式精确'''
    def ruler9(self, sentence):
        '''
        cons3:因为、由于
        cons3_model:{Effect}<Conj...>{Cause}
        '''
        pattern = re.compile(r'(.*)是?\s(因为|由于)/[p|c]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][2]
            data['effect'] = result[0][0]

        return data

    '''抽取主函数'''
    def extract_triples(self, sentence):
        infos = list()
      #  print(sentence)
        if self.ruler1(sentence):
            infos.append(self.ruler1(sentence))
        elif self.ruler2(sentence):
            infos.append(self.ruler2(sentence))
        elif self.ruler3(sentence):
            infos.append(self.ruler3(sentence))
        elif self.ruler4(sentence):
            infos.append(self.ruler4(sentence))
        elif self.ruler5(sentence):
            infos.append(self.ruler5(sentence))
        elif self.ruler6(sentence):
            infos.append(self.ruler6(sentence))
        elif self.ruler7(sentence):
            infos.append(self.ruler7(sentence))
        elif self.ruler8(sentence):
            infos.append(self.ruler8(sentence))
        elif self.ruler9(sentence):
            infos.append(self.ruler9(sentence))

        return infos
    
    def read_dictionary(self,pas,file):
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

    def existEvent(self,content):
        trigger = self.read_dictionary("./event","金融术语-经济指标.xlsx")
        trigger = "|".join(trigger)
        sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',content)
        # print(sentences)
        return sentences

    '''抽取主控函数'''
    def extract_main(self, content):
        sentences = self.process_content(content)
        datas = list()
        for sentence in sentences:
            events = self.existEvent(str(sentence))
            if len(events) != 0:

                subsents = self.fined_sentence(sentence)
                subsents.append(sentence)
                for sent in subsents:
                    sent = ' '.join([word.word + '/' + word.flag for word in pseg.cut(sent)])
                    result = self.extract_triples(sent)
                    if result:
                        for data in result:
                            if data['tag'] and data['cause'] and data['effect']:
                                if data['cause'] in events or data['effect'] in events:
                                    print("??")
                                    datas.append(data)
                return datas

    '''文章分句处理'''
    def process_content(self, content):
        return [sentence for sentence in SentenceSplitter.split(content) if sentence]

    '''切分最小句'''
    def fined_sentence(self, sentence):
        return re.split(r'[？！，；]', sentence)


'''测试'''
def test():
    content1 = """
    啥纳指上涨5%造成69227人死亡，374643人受伤，17923人失踪，是中华人民共和国成立以来破坏力最大的地震，也是唐山大地震后伤亡最严重的一次地震。
    """
    content2 = '''
    2015年1月4日下午3时39分左右，贵州省遵义市习水县二郎乡遵赤高速二郎乡往仁怀市方向路段发生山体滑坡，发生规模约10万立方米,导致多辆车被埋，造成交通双向中断。此事故引起贵州省委、省政府的高度重视，省长陈敏尔作出指示，要求迅速组织开展救援工作，千方百计实施救援，减少人员伤亡和财物损失。遵义市立即启动应急救援预案，市应急办、公安、交通、卫生等救援力量赶赴现场救援。目前，灾害已造成3人遇难1人受伤，一辆轿车被埋。
    当地时间2010年1月12日16时53分，加勒比岛国海地发生里氏7.3级大地震。震中距首都太子港仅16公里，这个国家的心脏几成一片废墟，25万人在这场骇人的灾难中丧生。此次地震中的遇难者有联合国驻海地维和部队人员，其中包括8名中国维和人员。虽然国际社会在灾后纷纷向海地提供援助，但由于尸体处理不当导致饮用水源受到污染，灾民喝了受污染的水后引发霍乱，已致至少2500多人死亡。
    '''
    content3 = '''
    American Eagle 四季度符合预期 华尔街对其毛利率不满导致股价大跌
    我之所以考试没及格，是因为我没有好好学习。
    因为天晴了，所以我今天晒被子。
    因为下雪了，所以路上的行人很少。
    我没有去上课是因为我病了。
    因为早上没吃的缘故，所以今天还没到放学我就饿了.
    因为小华身体不舒服，所以她没上课间操。
    因为我昨晚没睡好，所以今天感觉很疲倦。
    因为李明学习刻苦，所以其成绩一直很优秀。
    雨水之所以不能把石块滴穿，是因为它没有专一的目标，也不能持之以恒。
    他之所以成绩不好，是因为他平时不努力学习。
    你之所以提这个问题，是因为你没有学好关联词的用法。
    减了税,因此怨声也少些了。
    他的话引得大家都笑了，室内的空气因此轻松了很多。
    他努力学习，因此通过了考试。
    既然明天要下雨，就不要再出去玩。
    既然他还是那么固执，就不要过多的与他辩论。
    既然别人的事与你无关，你就不要再去过多的干涉。
    既然梦想实现不了，就换一个你自己喜欢的梦想吧。
    既然别人需要你，你就去尽力的帮助别人。
    既然生命突显不出价值，就去追求自己想要的生活吧。
    既然别人不尊重你，就不要尊重别人。 因果复句造句
    既然题目难做，就不要用太多的时间去想，问一问他人也许会更好。
    既然我们是学生，就要遵守学生的基本规范。
    '''
    extractor = CausalityExractor()
    datas = extractor.extract_main(content1)
    for data in datas:
        print('******'*4)
        print('cause', ''.join([word.split('/')[0] for word in data['cause'].split(' ') if word.split('/')[0]]))
        print('tag', data['tag'])
        print('effect', ''.join([word.split('/')[0] for word in data['effect'].split(' ') if word.split('/')[0]]))
        # print(data)

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

def get_md5(data):
    m5 = hashlib.md5()
    m5.update(json.dumps(data).encode())
    return m5.hexdigest()

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

def extractEvent(ori_event,trigger,events):
    events = []
    # for i in range(0,len(ori_events)):
    # for i in range(70,80):
    sentences = re.findall('([^。；，]*('+trigger+')[^。；，]*)',ori_event.content)
    
    for item in sentences:
        # print(item)
        if ori_event.title != item[0]:
            if len(list(item[0]))>6:
                ori_event.sentence = item[0]
                ori_event.trigger = item[1]
            
            if extractValue(ori_event.sentence):
                values = extractValue(ori_event.sentence)
                for value in values:
                    print("multi value")
                    ori_event.value = value
                    event = Event(ori_event.uid,ori_event.time, ori_event.type, ori_event.result_country, ori_event.content, ori_event.emotion,ori_event.title,ori_event.source,ori_event.sentence,ori_event.trigger,ori_event.value)
                    events.append(event)

            else:
                event = Event(ori_event.uid,ori_event.time, ori_event.type, ori_event.result_country, ori_event.content, ori_event.emotion,ori_event.title,ori_event.source,ori_event.sentence,ori_event.trigger,None)
                events.append(event)
        else:
            print(ori_event.title)
        
    # print("extract event "+str(i))
    return events

def changeType(data,trigger,event):
    events = []
    events = extractEvent(event,trigger,events)
    # events1 = []
    # events2 = []
    i,j = 0,0
    cause_event = ''.join([word.split('/')[0] for word in data['cause'].split(' ') if word.split('/')[0]])
    effect_event = ''.join([word.split('/')[0] for word in data['effect'].split(' ') if word.split('/')[0]])
    # print("cause:"+cause_event)
    # print("effect:"+effect_event)
    # print("****"*4)
    for event in events:
        if cause_event in event.sentence:
            i += 1
            events1 = event
        else:
            event0 = Event(event.uid,event.time,None,None,None,None,None,None,cause_event,None,None)
            events1 = event0

        if effect_event in event.sentence:
            j += 1
            events2 = event
        else:
            event0 = Event(event.uid,event.time,None,None,None,None,None,None,effect_event,None,None)
            events2 = event0
    return events1,events2


def makeCauseCSV(event1,event2):
    print("cause:"+event1.sentence)
    print("effect:"+event2.sentence)
    print("****"*4)
    csv_write.writerow(["V","event",get_md5(event1.sentence)+'event',event1.sentence])
    csv_write.writerow(["V","event",get_md5(event2.sentence)+'event',event2.sentence])
    csv_write.writerow(["E","造成",get_md5(event1.sentence)+'event'+"people",get_md5(event2.sentence)+'event'])
        
    return None



if __name__ == '__main__':
    news = read_csv_data("./data/","test.csv")
    trigger = read_dictionary("./event","金融术语-经济指标.xlsx")
    trigger = "|".join(trigger)
    all_datas = []
    extractor = CausalityExractor()
    with open("Triples_test_causality.csv",'w') as f:
        csv_write = csv.writer(f)
        for new in news:
            # contents.append(new.content)
            datas = extractor.extract_main(new.content)
            if datas != None:
                for data in datas:
                    event1,event2 = changeType(data,trigger,new)
                    if event1 != event2:
                        makeCauseCSV(event1,event2)
    
    
        
            

