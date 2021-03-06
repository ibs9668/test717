#-*-coding=utf-8-*-

import time

def duplicate(items):
    """
    批量文本去重, 输入的文本可以有部分已经去完重的，以duplicate字段标识
    input:
        items: 一推文本，[{"_id": , "title": , "content": }], 
        文本以utf-8编码
    output:
        更新了duplicate和same_from字段的items， same_from链向相似的新闻的_id
    """

    not_same_items = [item for item in items if 'duplicate' in item and item['duplicate'] == False]
    duplicate_items = [item for item in items if 'duplicate' in item and item['duplicate'] == True]
    candidate_items = [item for item in items if 'duplicate' not in item]

    for item in candidate_items:
        idx, rate, flag = max_same_rate_shingle(not_same_items, item)
        if flag:
            item['duplicate'] = False
            item['same_from'] = item['_id']
            not_same_items.append(item)
        else:
            item['duplicate'] = True
            item['same_from'] = not_same_items[idx]['_id']
            duplicate_items.append(item)

    return not_same_items + duplicate_items


class ShingLing(object):
    def __init__(self, text1, text2, n=3):
        """
        input:
        text1: 输入文本1, unicode编码
        text2: 输入文本2, unicode编码
        n: 切片长度
        """
        if not isinstance(text1, unicode):
            raise ValueError("text1 must be unicode")

        if not isinstance(text2, unicode):
            raise ValueError("text2 must be unicode")

        self.n = n
        self.threshold = 0.2
        self.text1 = text1
        self.text2 = text2
        self.set1 = set()
        self.set2 = set()
        self._split(self.text1, self.set1)
        self._split(self.text2, self.set2)
        self.jaccard = 0

    def _split(self, text, s):
        if len(self.text1) < self.n:
            self.n = 1

        for i in range(len(text) - self.n + 1):
            piece = text[i: i + self.n]
            s.add(piece)

    def cal_jaccard(self):
        intersection_count = len(self.set1 & self.set2)
        union_count = len(self.set1 | self.set2)

        self.jaccard = float(intersection_count) / float(union_count + 1)
        return self.jaccard

    def check_duplicate(self):
        return True if self.jaccard > self.threshold else False 
         

def max_same_rate_shingle(items, item, rate_threshold=0.2):
    """
    input:
        items: 已有的不重复数据
        item: 待检测的数据
    output:
        idx: 相似的下标
        max_rate: 相似度
    """
    flag = True
    idx = 0
    max_rate = 0
    for i in items:
        sl = ShingLing((i['title'] + i['content']), (item['title'] + item['content']), n=3)
        sl.cal_jaccard()
        if sl.jaccard >= rate_threshold:
            max_rate = sl.jaccard
            flag = False
            break
        idx += 1

    return idx, max_rate, flag


if __name__ == '__main__':
    items = []
    count = 0
    weibo_text = dict()
    with open("sports_text.txt", "rb") as f:
        for line in f:
            item = line.strip()
            tmp = dict()
            tmp['_id'] = count
            tmp['title'] = ''
            tmp['content'] = item
            items.append(tmp)
            count += 1
            weibo_text[count] = item


    results = duplicate(items)
    dup_results = dict()
    for item in results:
        if item['duplicate']:
            dup_list = dup_results[item['same_from']]
            dup_list.append(item["content"])
            dup_results[item['same_from']] = dup_list
        else:
            dup_results[item['_id']] = [item['content']]
            
    dup_results.keys()




