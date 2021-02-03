"""
update your own cookies
run this with command like: scrapy crawl neeq_rules > log/crwal_$(date '+%Y%m%d%H%M') 2>&1 &
"""
import scrapy
import json
from urllib.parse import urlencode
import sqlite3
import urllib
import os
import html2text
import re
import time
import shutil
from ..utils import difflog


pageSize = 20
fileRootPath = "./download/neeq_rules/"
conn = sqlite3.connect('neeq_rules.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn.row_factory = dict_factory
c = conn.cursor()
webRoot = "http://www.neeq.com.cn"


class NeeqRulesSpider(scrapy.Spider):
    """
    crawl neeq_rules
    """

    name = 'neeq_rules'
    allowed_domains = ['neeq.com.cn']

    cookies = {
        "BIGipServerJY_NEEQV1.3C_WEB_8000": "251724724.16415.0000",
        "Hm_lvt_b58fe8237d8d72ce286e1dbd2fc8308c": "1605691757",
        "Hm_lpvt_b58fe8237d8d72ce286e1dbd2fc8308c": "1606373060",
        "AlteonP": "AbHXI0FueGp2sX8PpyuXew$"
    }
    headers = {
        "Connection": "keep-alive",
        "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebK/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://www.neeq.com.cn",
        "Referer": "http://www.neeq.com.cn/rule/regulation_list.html",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    params = {
        'pageSize': pageSize,
        # 'keywords': '非上市',
        'startTime': '',
        'needFields[]': ['infoId', 'title', 'linkUrl', 'htmlUrl', 'publishDate', 'fileUrl', 'fileExtension'],
        # 'nodeIds[]': 105 # 法律法规
    }
    base_url = "http://www.neeq.com.cn/info/listse.do?callback=&"
    query_url = base_url + urlencode(params, True)
    
    diff = difflog.DiffLog('neeq_rules')

    def downloadFileWithRetry(self, url, filepath, retry):
        """
        """
        for i in range(retry):
            try:
                urllib.request.urlretrieve(url, filepath)
            except:
                time.sleep(1)
            if os.path.exists(filepath):
                return True
        return False


    def fileExist(self, filepath, title):
        """
        """
        return os.path.exists(filepath + title)


    def downloadFile(self, url, filepath='', title=''):
        """
        """
        if self.fileExist(filepath, title):
            return True
        if filepath and not os.path.exists(filepath):
            os.makedirs(filepath)
        print("[download file]", url, filepath + title)
        if url[0] == '/':
            url = webRoot + url
        # urllib.request.urlretrieve(webRoot + url, filepath + title)
        if not self.downloadFileWithRetry(url, filepath + title, 3):
            print("[downlaod file failed] %s" % url)
        res = os.path.exists(filepath + title)
        return res


    def html2md(self, url, filepath, title):
        """
        """
        if self.fileExist(filepath, title):
            return
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        print("[parse html]", url, filepath + title)
        # get text area
        meta = {
            "filepath": filepath,
            "title": title
        }
        return scrapy.Request(url, headers=self.headers, cookies=self.cookies, callback=self.parse_html, meta=meta)


    def parse_html(self, response):
        """
        """
        main_text = response.css("div.in_main")
        meta = response.meta
        row_html = main_text.get()
        # print(row_html)
        # get <a> within <a>
        # note that py regex is different from normal 
        # pattern1 = r'((?<=<a.*>.*>)<a.*>.*</a>(?=.*</a>))' wrong
        pattern1 = r"<a.*>.*>(<a.*>.*</a>).*</a>"
        pattern2 = r'<a.*>.*<a.*>.*</a>.*</a>'
        pattern3 = r"</a>.*<a.*>.*</a>.*<a.*>" # case: <a></a><a></a><a></a>, need to ignore
        # if there is more than one case, only first case will work
        hrefs = re.findall(pattern1, row_html)
        if hrefs:
            if not re.findall(pattern3, row_html):
                # print(hrefs)
                row_html = re.sub(pattern2, hrefs[0], row_html)
        # print(row_html)
        md = html2text.html2text(row_html)
        # print(md)

        # img
        # imgs = main_text.css("img").getall()
        # for img in imgs:
        #     print(img)

        # rm img
        pattern2 = r'(?:!\[(.*?)\]\((.*?)\))'
        md = re.sub(pattern2, '', md)
        # print(md)

        # attachment
        attachs = main_text.css("a")
        # download to relative path
        relPath= "./附件/%s" % meta["title"][:-3]
        abuPath = "%s附件/%s" % (meta["filepath"], meta["title"][:-3])
        
        # download to root path

        if attachs and not os.path.exists(abuPath):
            os.makedirs(abuPath)
        for attach in attachs:
            # print(attach)
            name = html2text.html2text(attach.get())
            # print(name)
            if "![]" not in name and "mailto" not in name:
                name = name.replace("\n", '').replace("\r", '')
                # print(name)
                name = name[1:].split(']')[0]
                if len(name) > 5 and '.' in name[-5:]: # if suffix in
                    name = name.split('.')[0].strip()
                name = name.replace("\.", ".").replace(" ", "")
                suffix = attach.attrib["href"].split('.')[-1]
                if not os.path.exists("%s/%s.%s" % (abuPath, name, suffix)):
                    print("[attach path]", webRoot + attach.attrib["href"], "%s/%s.%s" % (abuPath, name, suffix))
                    if not self.downloadFile(attach.attrib["href"], "%s/" % (abuPath), "%s.%s" % (name, suffix)):
                        print("[downlaod failed] %s" % webRoot + attach.attrib["href"])
                    # urllib.request.urlretrieve(webRoot + attach.attrib["href"], "%s/%s.%s" % (abuPath, name, suffix))
                attachPath = "%s/%s.%s" % (relPath, name, suffix)
                md = md.replace(attach.attrib["href"], attachPath)

        # md
        md = md.replace("\.\r", ".").replace("\.\n", ".")
        # print(md)

        f = open(meta["filepath"] + meta["title"], 'w')
        f.write(md)
        f.close


    def saveOne(self, ruleType, path, info):
        """
        """
        print("[save one]", ruleType, path, info)
        infoId = int(info["infoId"])
        res = False
        if path[-1] != '/':
            path = '%s/' % path
        info['title'] = info["title"].strip()
        title = '%s.%s' % (info['title'], info['fileExtension'])
        # html to md
        if info['fileExtension'] == '' and info['htmlUrl']:
            title = '%s.md' % (info['title'])
        # link to md or file
        if info['fileExtension'] == '' and info["linkUrl"]:
            suff = info["linkUrl"].split(".")[-1]
            # print(suff)
            if suff == "html":
                title = '%s.md' % (info['title'])
            else:
                info['fileExtension'] = suff
                info['fileUrl'] = info["linkUrl"]
                title = '%s.%s' % (info['title'], info['fileExtension'])

        # download pdf/doc/docx/xls/xlsx file
        if info['fileExtension'] in set(('pdf', 'doc', 'docx', 'xls', 'xlsx', 'rar')):
            res = self.downloadFile(info['fileUrl'], path, title)
            if not res:
                print("file download failed: %s" % title)
                return
        
        # check if data in db
        c.execute('SELECT * FROM neeq_rules WHERE infoId=?', (infoId,))
        row = c.fetchone()
        # test case 200008399
        # if infoId == 200008399:
        #     info["title"] = "[已废止]中国证监会关于全国中小企业股份转让系统挂牌公司转板上市的指导意见"
        #     title = info["title"] + ".md"
        #     ruleType == 496
        #     path = fileRootPath + "业务规则/已废止业务类/"
        if row:
            # maybe old data updated
            # check data change
            # update sql, update file name, update file path, mv attach if needed
            print("[db data exist]", row)
            # if data updated, normally the title or ruleType will be changed
            if row["title"] != info["title"] or row["ruleType"] != ruleType:
                print("[db data update]", row)
                # move old attachment path to new path
                oldAttachPath = row["attachPath"]
                newAttachPath = path + "/".join(row["attachPath"].split("/")[-2:])
                print("[attach path diff] old: %s, new: %s" % (oldAttachPath, newAttachPath))
                if os.path.exists(oldAttachPath):
                    shutil.move(oldAttachPath, newAttachPath)
                # move file to new path and rename it
                shutil.move(row["filePath"], path + title)
                c.execute("UPDATE neeq_rules SET title=?, ruleType=?, publishDate=?, filePath=?, attachPath=? WHERE infoId=?", \
                    (info["title"], ruleType, info["publishDate"], path + title, newAttachPath, infoId, ))
                conn.commit()

                loginfo = {
                    "infoId": infoId,
                    "title": info['title'],
                    "fileExtension": row['fileExtension'],
                    "publishDate": info['publishDate'],
                    "filePath": path + title, 
                    "attachPath": newAttachPath,
                    "ruleType": ruleType
                }
                res, message = self.diff.WriteDiffRow('m', infoId, loginfo, row)
                print("[diff log res]", res, message)
                return
            else:
                if self.fileExist(path, title):
                    print("[data exist] infoId: %d" % infoId)
                    return
        else:
            # insert sql
            c.execute("INSERT INTO neeq_rules (infoId, title, fileExtension, fileUrl, linkUrl, htmlUrl, publishDate, filePath, attachPath, ruleType) \
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                    (infoId, info['title'], info['fileExtension'], info['fileUrl'], info['linkUrl'], info['htmlUrl'], info['publishDate'], path + title, path + "附件/" + info["title"], ruleType))
            conn.commit()
            # new data, log diff 
            loginfo = {
                "infoId": infoId,
                "title": info['title'],
                "fileExtension": info['fileExtension'],
                "publishDate": info['publishDate'],
                "filePath": path + title, 
                "attachPath": path + "附件/" + info["title"],
                "ruleType": ruleType
            }
            res, message = self.diff.WriteDiffRow('+', infoId, loginfo)
            print("[diff log res]", res, message)

        # html
        if info['fileExtension'] == '' and info['htmlUrl']:
            if info['htmlUrl'][0] == "/":
                info['htmlUrl'] = webRoot + info['htmlUrl']
            return self.html2md(info['htmlUrl'], path, title)
        # link
        if info['fileExtension'] == '' and info['linkUrl']:
            if info['linkUrl'][0] == "/":
                info['linkUrl'] = webRoot + info['linkUrl']
            return self.html2md(info['linkUrl'], path, title)
        # except:
            # print(info)
            # return


    def saveData(self, ruleType, typeName, data):
        """
        """
        try:
            content = data["content"]
        except:
            print('[content wrong]', data)
            return
        elePath = "/".join(typeName.split('$$'))
        path = "%s%s" % (fileRootPath, elePath)
        for info in content:
            yield self.saveOne(ruleType, path, info)


    def start_requests(self):
        # loop all types 
        c.execute("SELECT * FROM rule_types;")
        for info in c.fetchall():
            meta = {}
            meta["ruleType"] = info["ruleType"]
            meta["ruleName"] = info["ruleName"]
            meta["page"] = 0
            # if meta["ruleType"] != 1131:
            #     continue
            url = self.query_url + "&page=%d&nodeIds[]=%d" % (meta["page"], meta["ruleType"]) 
            yield scrapy.Request(url, headers=self.headers, cookies=self.cookies, callback=self.parse, meta=meta)


    def parse(self, response):
        results = json.loads(response.text[1:-1])
        result = results.pop()
        data = result['data']
        meta = response.meta
        # write to sqlite
        # self.saveData(self.nodeId, "业务规则$$综合类", data)
        for req in self.saveData(meta["ruleType"], meta["ruleName"], data):
            if req:
                time.sleep(0.5)
                yield req
        # yield from response.follow_all([req for req in self.saveData(meta["ruleType"], meta["ruleName"], data) if req], self.parse_html)
        
        yield {'data': data}
        if not data['lastPage']:
            meta["page"] += 1
            url = self.query_url + "&page=%d&nodeIds[]=%d" % (meta["page"], meta["ruleType"]) 
            time.sleep(1)
            yield response.follow(url, headers=self.headers, cookies=self.cookies, callback=self.parse, meta=meta)