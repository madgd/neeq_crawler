import requests
import json
import datetime
import argparse
import re

codes_bad_ST_2022 = set(["833333","871369","872809","870446","831431","832521","430394","831003","832613","430083","831331","870069","430668","430177","430609","831266","832657","834827","872800","835041","871720","430032","430122","831114","837300","837639","837801","831084","832418","836021","836466","837402","837630","871450","872789","430123","430263","831226","831608","836657","870773","831372","833382","834085","834506","835574","839423","839635","870843","871311","871523","833529","833847","834017","834851","835463","835842","870334","871030","871641","430015","430065","430201","430462","830801","831405","831421","831603","831680","831808","831923","832199","832435","832946","833627","834304","836863","837716","837763","870162","870631","870965","871201","871253","872903","430323","830819","831725","831955","832172","832358","832608","833325","834953","835488","835566","837423","837499","837865","872584","872695","430107","430671","430684","830875","831090","831632","833410","836290","836407","836435","837563","838156","839818","871069","872157","872158","872366","872688"])
today = datetime.datetime.now().strftime("%Y-%m-%d")

parser = argparse.ArgumentParser(description='监控年报.')
parser.add_argument('--date', metavar='date', type=str, default=today,
                    help='日期，格式XXXX-XX-XX')
parser.add_argument('--keyword', metavar='keyword', type=str, default="",
                    help='标题关键词')
parser.add_argument('--code_list', metavar='code_list', type=str, default="",
                    help='代码列表，格式: 8xxxxx,4xxxxx 用英文符号分隔')                    
args = parser.parse_args()
# print(args.date)

print("监控年报工具")
if args.keyword == "":
    keyword = input("输入检索词. 直接回车默认为无:")
    if keyword:
        args.keyword = keyword
if args.date == today:
    date = input("输入日期, 格式XXXX-XX-XX。直接回车默认今天:")
    if date:
        args.date = date
if args.code_list == "":
    code_list = input("输入代码筛选列表, 格式: 8xxxxx,4xxxxx 用英文符号分隔。\n直接回车默认不筛选。\n输入b使用 2020年年报否定或无法表示意见公司名单-预约时间跟踪 列表\n:")
    if code_list:
        if code_list == 'b':
            args.code_list = codes_bad_ST_2022
        else:
            args.code_list = set(code_list.replace('，', ',').split(','))

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
    if not args.code_list or item['companyCd'] in args.code_list:
        if 'disclosureSubtype' in item and item['disclosureSubtype'] in disclosureSubtype or\
            re.search(':202[0-9]年年度报告', item['disclosureTitle']) and "摘要" not in item['disclosureTitle']:
        #  ((":2020年年度报告" in item['disclosureTitle'] or ":2021年年度报告" in item['disclosureTitle']) and "摘要" not in item['disclosureTitle']):
            print("%s(%s): %s, 链接: http://www.neeq.com.cn/%s" % (item['companyCd'], item['companyName'], item['disclosureTitle'], item['destFilePath']))
    
input("\n检索完成!")