import xlwt
import os

mypath = "D:/"
textfile = [ os.path.join(mypath,f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath,f)) and '.txt' in f]

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False  
        
style = xlwt.XFStyle()
style.num_format_str = '#,###0.00' 

# read .txt to list 
f = open(textfile[0],'r+')

row_list = []
for row in f:
    row_list.append(row.split(':'))
# from list change to tuple
column_list = zip(*row_list)

workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('Sheet1')
i=0
for column in column_list:
    for item in range(len(column)):
        value = column[item].strip()
        if is_number(value):
            worksheet.write(item,i,float(value),style=style)
        else:
            worksheet.write(item,i,value)
    i+=1
workbook.save(textfile[0].replace('.txt','.xls'))