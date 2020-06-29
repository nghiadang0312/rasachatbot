import json
import requests
import feedparser
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def tao_data(f_xls, f_save):
    df = pd.read_excel(f_xls, 0, header=None)
    d_f= {}
    for i in range(1,len(df.iloc[:, 0])):
        dulieu = df.iloc[i,:]
        dn = str(dulieu[4])
        if dn == "không":
            tu_dn = None
        else:
            tu_dn = []
            while (1):
                tu_dn.append(dn[dn.rfind(";")+1:])
                dn = dn[0:dn.rfind(";")]
                if dn.rfind(";")<0:
                    tu_dn.append(dn[dn.rfind(";")+1:])
                    break
                
        d={
            "id":  str(dulieu[1]),
            "đơn vị": str(dulieu[3]),
            "từ đồng nghĩa": tu_dn,
            "domain": str(dulieu[2]),
            "địa chỉ": str(dulieu[5])
        }
        d_f[str(i)] = d 
    with open (f_save,'w',encoding='utf8') as f:
        json.dump(d_f,f,ensure_ascii=False)

def them_data(f_json,data):
    with open(f_json, 'r+', encoding='utf8') as file:
        d = json.load(file)
        id1 = len(d)+1
        d1= {str(id1): data}
        d.update(d1)
        file.seek(0)
        json.dump(d, file, ensure_ascii=False)
    
def tim_dn(s,d,t):
    for i in range(1,len(d)+1):
        data = d[str(i)]
        dong_nghia = data["từ đồng nghĩa"]
        if s == data["đơn vị"]:
            return data[t]
        else:
            try:
                for j in range(len(dong_nghia)):
                    if dong_nghia[j] == s:
                        return data[t]
            except:
                continue
            
    return False
