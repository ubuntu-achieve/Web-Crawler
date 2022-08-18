import os
import json
import glob
import img2pdf
import requests
import threading

papers = [
    "e53b0327a7fa0dcf04df3362a128cca1",
    "ec39ef1c6da3b6ea521b67b34c7562ba",
    "04ae1eea2b4a25a8d3a500da8eed6e14",
    "d434c150940b3cfef79581df7dddad91",
    "d8b0599f4ba4cebc546d130f2e443de6",
    "d816c362f8597ce8f568156d869655f7",
    "3a51292c9c3ffd07d4b56f5ab0db6ece",
    "f8556123c87e758b3552595c3beb809e",
    "1288767ecd10342eb528e0f9b7ddc7cc",
    "e043eb4621ab55d33e65eba325195f61",
    "e53b0327a7fa0dcf04df3362a128cca1",
    "a52dcf00127184230ebf917617cb37d4",
    "08e86ada05099b7de2b24c8577b22073",
    "6022ae042a0e77907d71cbc484b3c305",
    "17d8319a18421df3d4e2a728066bf126",
    "76f84b918433d7b3121eb267b1b8f579",
    "4a0b15f96f14db8aaf4ca0893bd8e1db"
]

name_url = "https://kd.nsfc.gov.cn/api/baseQuery/projectInfluenceAnalysisData"
info_url = "https://kd.nsfc.gov.cn/api/baseQuery/completeProjectReport"
img_url  = "https://kd.nsfc.gov.cn/"
headers  = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

def get_paper(begin, end, thread_index=1):
    '''
    begin:批量下载文献的起始索引
    end:批量下载文件的结束索引
    '''
    for index in range(begin, end):
        fromdata1 = {
            "projectID": papers[index]
        }
        paper_name = requests.post("https://kd.nsfc.gov.cn/api/baseQuery/projectInfluenceAnalysisData",headers=headers,data=fromdata1)
        paper_name = json.loads(paper_name.text)["data"][0]['chineseTitle']
        try:
            os.mkdir(paper_name)
        except:
            pass
        img_index = 1
        while True:
            print("\r%d 正在下载《%s》\t第%d页"%(index, paper_name, img_index-1), end='')
            if os.path.isfile(os.path.join(paper_name, "%d.png"%(img_index-1))):
                img_index += 1
                continue
            fromdata2 = {
                "id":papers[index],
                "index":str(img_index)
            }
            img_path = requests.post("https://kd.nsfc.gov.cn/api/baseQuery/completeProjectReport",headers=headers,data=fromdata2)
            img_path = json.loads(img_path.text)["data"]["url"]
            img      = requests.get(img_url + img_path)
            if img.status_code != 200:
                break
            with open(os.path.join(paper_name, "%d.png"%(img_index-1)), 'wb') as f:
                f.write(img.content)
            img_index += 1
        sum_num = len(glob.glob(os.path.join(paper_name, "*.png")))
        with open("%s.pdf"%paper_name, "wb") as f:
            f.write(img2pdf.convert(["%s//%s.png"%(paper_name, str(pdf_index)) for pdf_index in range(sum_num)]))
        print()
    print("第%d线程下载完成"%thread_index)

def mutl_threading_download(num):
    '''
    num: 下载的线程数
    '''
    number        = len(papers)//num
    download_list = []
    print("%d线程下载"%num)
    for i in range(num):
        download_list.append(threading.Thread(target=get_paper, args=(i*number,(i+1)*number, i), name="Job%d"%i))
        #download_list[-1].setDaemon(True)
        download_list[-1].start()
    print("漏掉",number*(num+1)-1)

if __name__ =="__main__":
    #mutl_threading_download(1)
    get_paper(0,len(papers))
