# Financial_Map
经过调整整合，triple_without_relation.py可以生成出事件关系外的其他三元组，包括事件，触发词，公司，观点，人名之间的关系。
causality.py可以生成事件因果关系的三元组。

发现的可能存在的问题：
1.triple_without_relation.py中人名没有抽取完全
2.causality.py没有优化过，存在很多重复的事件抽取工作，抽取结果不理想，一个没有标点的短句中如果存在两个金融事件会造成指向自己的关系，process_content函数切分出的长句子中如果包含一个金融事件，也会把该长句子中其他的跟金融事件无关的因果关系提取出来（这个调整了一半，调整出了一些问题，在extract_main函数的注释部分）。

顺承事件还没有开始
