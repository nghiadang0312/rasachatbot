
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

import requests
import json
import urllib.request
from bs4 import BeautifulSoup
from pyvi import ViTokenizer, ViPosTagger
import numpy as np

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

def lay_tt(s):
    dulieu = json.loads(s)
    kq = []
    ten = 'Tên cơ quan: '+ dulieu['tccn_ten']  
    diachi= 'Địa chỉ: '+ dulieu['tccn_diachi'] 
    tenhs= 'Tên hồ sơ: '+ dulieu['tenhoso']
    so_cmnd = 'Số CMND: ' + dulieu['socmnd']
    ngay_tn = 'Ngày tiếp nhận: ' + dulieu['ngaynhan']
    trang_thai ='Tình trạng xử lý hồ sơ: ' + dulieu['tinhtrang_hoso']
    ngay_tkq= 'Ngày trả kết quả: ' + dulieu['ngaytraketqua']
    ngay_xlx='Ngày xử lý xong: ' + dulieu['ngayxulyxong']
    nguoinhan = 'Người nhận:'+ dulieu['nguoinhan']

    kq.append(ten)
    kq.append(diachi)
    kq.append(tenhs)
    if so_cmnd !='0000000000':
        kq.append(so_cmnd)
    kq.append(ngay_tn)
    kq.append(trang_thai)
    kq.append(ngay_xlx)
    kq.append(ngay_tkq)
    if nguoinhan != None:
        kq.append(nguoinhan)
    return kq

class action_tra_cuu_hs(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_tra_cuu_hs'
    
    def run(self, dispatcher, tracker, domain):
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        ma_hs = next(tracker.get_latest_entity_values("ma_hs"), None)
        ma_hs = ma_hs.replace(" ","")
        url = 'http://thamdon.myxuyen.soctrang.gov.vn/api/hoso/tracuuhoso?tukhoa='+ma_hs
        # Tien hanh lay thong tin tu URL
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        s = str(np.copy(str(soup)))
        return_msg = lay_tt(s)
        print(lay_tt(s))
        for i in return_msg:
            dispatcher.utter_message(i)
        dispatcher.utter_message(template="utter_restart")
        return [Restarted()]

def lay_tttk(s):
    dulieu = json.loads(s)
    kq = []
    tl_thang = round(float(dulieu['tile_daxuly_thang'])*100,2)
    tl_nam =  round(float(dulieu['tile_daxuly_nam'])*100,2)
    dunghan_thang = 'Hồ sơ xử lý đúng hạn theo tháng: ' + str(dulieu['hs_xldunghan_thang'])
    tile_thang= 'Tỉ lệ đúng hạn theo tháng: ' + str(tl_thang)+'%'
    dunghan_nam= 'Hồ sơ xử lý đúng hạn theo năm: ' + str(dulieu['hs_xldunghan_nam'])
    tronghan_nam = 'Hồ sơ xử lý trong hạn theo năm: ' + str(dulieu['hs_tronghan_nam'])
    trehan_thang = 'Hồ sơ xử lý trễ hạn theo tháng: ' + str(dulieu['hs_xl_trehan_thang'])
    tile_nam = 'Tỉ lệ đúng hạn theo năm: ' + str(tl_nam)+'%'
    tronghan_thang ='Hồ sơ xử lý trong hạn theo tháng: ' + str(dulieu['hs_tronghan_thang'])
    moi_thang ='Hồ sơ mới tiếp nhận theo tháng: ' + str(dulieu['hs_moitiepnhan_thang'])
    moi_nam ='Hồ sơ mới tiếp nhận theo năm: ' + str(dulieu['hs_moitiepnhan_nam'])
    trehan_nam='Hồ sơ xử lý trễ hạn năm: ' + str(dulieu['hs_xl_trehan_nam'])
    kq.append(moi_thang)
    kq.append(dunghan_thang)
    kq.append(tronghan_thang)
    kq.append(trehan_thang)
    kq.append(tile_thang)
    return kq
            
class action_thong_ke_full(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_thong_ke_full'
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        thang = tracker.get_slot("thang_tk")
        thang = thang.replace(" ","")
        nam = tracker.get_slot("nam_tk")
        nam = nam.replace(" ","")
        donvi_cb = tracker.get_slot("don_vi")
        with open('data_full.json',encoding='utf8') as file_write:
            d = json.load(file_write)
        try:
            domain = tim_dn(donvi_cb, d, "domain")
            #print(domain, ' ', thang, ' ', nam)
            try:
                domain = domain.replace("motcua.", "motcua")
            except:
                domain = domain
            url = 'https://motcuasotuphap.soctrang.gov.vn/api/lienthongiso/tkttxlhs?domain=' + domain + '&thang=' + thang + '&nam=' + nam
            # Tien hanh lay thong tin tu URL
            print(url)
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup(page, 'html.parser')
            s = str(np.copy(str(soup)))
            return_msg = lay_tttk(s)

            dispatcher.utter_message("Kết quả thống kê của "+ donvi_cb + " vào tháng "+thang+" năm "
                                     + nam+ " có kết quả như sau: ")
            for i in return_msg:
                dispatcher.utter_message(i)
        except:
            dispatcher.utter_message(template="utter_loi")
        dispatcher.utter_message(template="utter_restart")
        return [Restarted()]

class action_tra_cuu_diachi(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
            return 'action_tra_cuu_diachi'
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Khai bao dia chi luu tru ket qua so xo. O day lam vi du nen minh lay ket qua SX Mien Bac
        donvi_cb = tracker.get_slot("don_vi")
        donvi_cb = donvi_cb.lower()
        with open('data_full.json', encoding='utf-8') as file_write:
            d = json.load(file_write)

        diachi = tim_dn(donvi_cb,d,"địa chỉ")
        try:
            dispatcher.utter_message(diachi)
        except:
            dispatcher.utter_message(template="utter_loi")
        dispatcher.utter_message(template="utter_restart")
        return [Restarted()]


class action_greet(Action):
    def name(self):
        # Doan nay khai bao giong het ten ham ben tren la okie
        return 'action_greet'

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text= "Chào bạn, Tôi là hệ thống Dịch vụ công Sóc Trăng.",
                                 image="https://dichvucong.soctrang.gov.vn/gioi-thieu;jsessionid=6F5D238588A01B3AD7A04CF2E5DDB58F?p_p_id=GioiThieu_WAR_cgatecongchungportlet_INSTANCE_7Xm7axzx1EGP&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1&_GioiThieu_WAR_cgatecongchungportlet_INSTANCE_7Xm7axzx1EGP_javax.faces.resource=slider%2F55.png&_GioiThieu_WAR_cgatecongchungportlet_INSTANCE_7Xm7axzx1EGP_ln=images")
        dispatcher.utter_message(template="utter_chuc_nang")
        return []

class thongke_form(FormAction):
    
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "thongke_form"
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        
        return ["don_vi","thang_tk","nam_tk"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        

        return {
            "don_vi": self.from_entity(entity="don_vi", intent=["thong_ke","chi_co_dv"]),
            "thang_tk": self.from_entity(entity="thang_tk", intent=["inform","thong_ke"]),
            "nam_tk": self.from_entity(entity="nam_tk", intent=["inform","thong_ke"]),
            }
    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False
    
    def validate_thang_tk(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if np.shape(value) != ():
            value = value[0]
        if self.is_int(value) and int(value)>0 and int(value)<= 12:
            return {"thang_tk": value}
        else:
            dispatcher.utter_message(template="utter_saithang")
            # validation failed, set slot to None
            return {"thang_tk": None}

    def validate_nam_tk(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if np.shape(value) != ():
            value = value[0]
        if self.is_int(value) and int(value)>0:
            return {"nam_tk": value}
        else:
            dispatcher.utter_message(template="utter_sainam")
            # validation failed, set slot to None
            return {"nam_tk": None}
    
    def validate_don_vi(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        with open('data_full.json',encoding='utf8') as file_write:
            d = json.load(file_write)
        if np.shape(value) != ():
            value = value[0]

        value = value.lower()
        if tim_dn(value,d,"đơn vị") != False:
            donvi = tim_dn(value,d,"đơn vị")
            return {"don_vi": donvi}
        else:
            dispatcher.utter_message(template="utter_saidv")
            return {"don_vi": None}
        
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        #dispatcher.utter_message(template="utter_thong_ke")
        return []


class diachi_form(FormAction):

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "diachi_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["don_vi"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "don_vi": self.from_entity(entity="don_vi", intent=["tra_cuu_diachi","chi_co_dv"])
        }

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_don_vi(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        with open('data_full.json', encoding='utf8') as file_write:
            d = json.load(file_write)
        if np.shape(value) != ():
            value = value[0]

        value = value.lower()
        if tim_dn(value, d, "đơn vị") != False:
            donvi = tim_dn(value, d, "đơn vị")
            return {"don_vi": donvi}
        else:
            dispatcher.utter_message(template="utter_saidv")
            return {"don_vi": None}

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []

class mahs_form(FormAction):

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "mahs_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["ma_hs"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "ma_hs": self.from_entity(entity="ma_hs", intent=["tra_cuu_hs","inform"])
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []
