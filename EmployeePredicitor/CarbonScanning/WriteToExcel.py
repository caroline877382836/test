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
        sheet.set_column('A:A', 20)
        #sheet.col_width(10)
        sheet.write(0,0, value)
        sheet.write(0, 1, "total_LayerCnt : %s" %  lay_cnt)
        self._sheet = sheet
        raw_idx =  self.raw_idx + 1
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
            self._sheet.write(raw_idx + idx + 2, 4, del_sigma[idx][0])
            self._sheet.write(raw_idx + idx + 2, 5, del_sigma[idx][1])
        raw_idx = raw_idx + len(benchMarch_sigma) + 2
        self.raw_idx = raw_idx
        return raw_idx 
             
    def save_sheet(self):
        self._book.close()  
           
    def insert_image2Excel(self,raw_idx,column,msg,img_path):
        self._sheet.write(raw_idx,column, msg)
        #self._sheet.insert_image('B2', 'C:\Users\Cnxuacar\Desktop\Figure_3.png',{'x_scale': 0.5, 'y_scale': 0.5})
        #Image.open(img_path).convert("RGB").save('violations.bmp') 
        #self._sheet.insert_bitmap('violations.bmp',5,13)
        self._sheet.insert_image(raw_idx + 1, column,img_path)
        raw_idx = raw_idx + 25
        self.raw_idx = raw_idx
        return raw_idx
                
    
#===============================================================================
# if __name__ == "__main__" : 
#     import os
#     os.chdir("D:\TestData")
#     book = WriteDada2Excel("te_output.xlsx")
#     sheet_raw_idx = book.add_sheet("patient_case_9",3)
#     sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, 'msg', "D:\TestData\IDD.png")
#     benchMarch_sigma = [[0,0],[1,1],[2,2]]
#     protonCS_sigma = [[1,1],[2,2],[5,5]]
#     del_sigma = [[2,2],[4,4],[6,6]]
#     book.write_sigmas_2_sheet(sheet_raw_idx, benchMarch_sigma, protonCS_sigma, del_sigma)
#     book.save_sheet()
#     
#===============================================================================
    
            