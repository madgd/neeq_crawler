import requests
import json
import datetime
import argparse
import re

today = datetime.datetime.now().strftime("%Y-%m-%d")

parser = argparse.ArgumentParser(description='监控年报.')
parser.add_argument('--date', metavar='date', type=str, default=today,
                    help='日期，格式XXXX-XX-XX')
parser.add_argument('--keyword', metavar='keyword', type=str, default="ST",
                    help='标题关键词')
args = parser.parse_args()
# print(args.date)
if args.keyword == "ST":
    keyword = input("输入检索词. 直接回车默认为‘ST’:")
    if keyword:
        args.keyword = keyword
if args.date == today:
    date = input("输入日期, 格式XXXX-XX-XX。直接回车默认今天:")
    if date:
       args.date = date

codes = set(["833333","871369","872809","870446","831431","832521","430394","831003","832613","430083","831331","870069","430668","430177","430609","831266","832657","834827","872800","835041","871720","430032","430122","831114","837300","837639","837801","831084","832418","836021","836466","837402","837630","871450","872789","430123","430263","831226","831608","836657","870773","831372","833382","834085","834506","835574","839423","839635","870843","871311","871523","833529","833847","834017","834851","835463","835842","870334","871030","871641","430015","430065","430201","430462","830801","831405","831421","831603","831680","831808","831923","832199","832435","832946","833627","834304","836863","837716","837763","870162","870631","870965","871201","871253","872903","430323","830819","831725","831955","832172","832358","832608","833325","834953","835488","835566","837423","837499","837865","872584","872695","430107","430671","430684","830875","831090","831632","833410","836290","836407","836435","837563","838156","839818","871069","872157","872158","872366","872688"])
# date = "2022-02-08"
disclosureSubtype = set(["9503-1001"])
pageSize = 20
res = []
# params = {
#     'disclosureSubtype[]': ['9503-1001'],
# }
url = "http://www.neeq.com.cn/disclosureInfoController/infoResult_zh.do?callback=&keyword=%s&startTime=%s&endTime=%s&pageSize=%s" % (args.keyword, args.date, args.date, pageSize)
print(url)
r = requests.get(url)
data = json.loads(r.text[1:-1])
res += data[0]['listInfo']['content']
totalPages = data[0]['listInfo']['totalPages']
page = 1
while page < totalPages:
    url = "http://www.neeq.com.cn/disclosureInfoController/infoResult_zh.do?callback=&keyword=%s&startTime=%s&endTime=%s&pageSize=%s&page=%s" % (args.keyword, args.date, args.date, pageSize, page)
    print(url)
    r = requests.get(url)
    data = json.loads(r.text[1:-1])
    res += data[0]['listInfo']['content']
    page += 1

# print(res)
for item in res:
    if args.keyword != "ST" or item['companyCd'] in codes:
        if 'disclosureSubtype' in item and item['disclosureSubtype'] in disclosureSubtype or\
            re.search(':202[0-9]年年度报告', item['disclosureTitle']) and "摘要" not in item['disclosureTitle']:
        #  ((":2020年年度报告" in item['disclosureTitle'] or ":2021年年度报告" in item['disclosureTitle']) and "摘要" not in item['disclosureTitle']):
            print("%s(%s): %s" % (item['companyCd'], item['companyName'], item['disclosureTitle']))
    
