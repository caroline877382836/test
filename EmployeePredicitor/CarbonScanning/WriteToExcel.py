from xlsxwriter.workbook import Workbook
import logging
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
from PIL import Image
import os

logger = logging.getLogger(__name__)

class WriteDada2Excel:  #each patient correspond to one sheet
    def __init__(self,excel_name):   # init create excel file: if exits / not        
        self.excel_name = excel_name
        if os.path.exists(excel_name):
            #book = open_workbook(excel_name,on_demand=True)
            #self._book = copy(book)
            os.remove(excel_name)
            logger.info('Delete the existing old excel file named:' + excel_name)        
        self._book = Workbook(excel_name)
        self.book_format = self._book.add_format({'bold': True, 'font_color': 'red'})  
        self.raw_idx = 0
     
    def add_sheet(self,testPatientName,lay_cnt):
        #Add a sheet with one line of data  
        value = "This sheet with patient named: %s" % testPatientName
        book = self._book
        try:
            sheet = book.add_worksheet(name = testPatientName)
            logger.info('worsheet with name: ' + testPatientName + 'created')
        except Exception,e:
            logger.error('create new worksheet {}. failed: Reason is: {}'.format(testPatientName, str(e)), exc_info=True)
            raise e        
        sheet.set_column('A:A', 30)
        #sheet.col_width(10)
        sheet.write(0,0, value)
        sheet.write(0, 1, "total_LayerCnt : %s" %  lay_cnt)
        self._sheet = sheet
        raw_idx = 1
        self.raw_idx = raw_idx
        return raw_idx
     
    def write_sigmas_2_sheet(self,raw_idx,benchMarch_sigma, protonCS_sigma, del_sigma):  
        self._sheet.write(raw_idx, 0, "benchMarch_sigmaX") 
        self._sheet.write(raw_idx, 1, "benchMarch_sigmaY") 
        self._sheet.write(raw_idx, 2, "protonCS_sigmaX") 
        self._sheet.write(raw_idx, 3, "protonCS_sigmaY")
        self._sheet.write(raw_idx, 4, "delta_sigmaX")  # bench - Proton
        self._sheet.write(raw_idx, 5, "delta_sigmaY") 
        for idx in range(0,len(benchMarch_sigma),1):
            self._sheet.write(raw_idx + idx + 2, 0, benchMarch_sigma[idx][0])
            self._sheet.write(raw_idx + idx + 2, 1, benchMarch_sigma[idx][1])
            self._sheet.write(raw_idx + idx + 2, 2, protonCS_sigma[idx][0])
            self._sheet.write(raw_idx + idx + 2, 3, protonCS_sigma[idx][1])
            if abs(del_sigma[idx][0]) >= 0.01:
                self._sheet.write(raw_idx + idx + 2, 4, del_sigma[idx][0], self.book_format)
            else:
                self._sheet.write(raw_idx + idx + 2, 4, del_sigma[idx][0])
            if abs(del_sigma[idx][1]) >= 0.01:
                self._sheet.write(raw_idx + idx + 2, 5, del_sigma[idx][1], self.book_format)
            else:
                self._sheet.write(raw_idx + idx + 2, 5, del_sigma[idx][1])
        raw_idx = raw_idx + len(benchMarch_sigma) + 2
        self.raw_idx = raw_idx
        return raw_idx 
             
    def save_book(self):
        try:
            self._book.close()
            logger.info("save excel file successful") 
        except Exception,e:
            logger.error('save excel file failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e  
        
    def write(self,raw_idx,column,sheet_data,msg):             
        self._sheet.write(raw_idx,column,sheet_data,self.book_format)
        self._sheet.write(raw_idx,column+2,msg,self.book_format)
        raw_idx=raw_idx+1
        self.raw_idx=raw_idx
        return raw_idx
    
    def write_single(self,raw_idx,column,msg):
        self._sheet.write(raw_idx, column, msg, self.book_format)
        raw_idx=raw_idx
        self.raw_idx=raw_idx
        return raw_idx  
           
    def insert_image2Excel(self,raw_idx,column,msg,img_path):
        self._sheet.write(raw_idx,column + 3, msg, self.book_format)
        #self._sheet.insert_image('B2', 'C:\Users\Cnxuacar\Desktop\Figure_3.png',{'x_scale': 0.5, 'y_scale': 0.5})
        #Image.open(img_path).convert("RGB").save('violations.bmp') 
        #self._sheet.insert_bitmap('violations.bmp',5,13)
        self._sheet.insert_image(raw_idx + 1, column,img_path)
        raw_idx = raw_idx + 25
        self.raw_idx = raw_idx
        return raw_idx
            