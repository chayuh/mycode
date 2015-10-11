# -*- coding: utf-8 -*-
import xlrd
import xlwt
import os
from xlutils.copy import copy

def write_title(filename):
    file = xlwt.Workbook()
    style1 = xlwt.XFStyle()
    font1 = xlwt.Font()   #创建font1
    font1.name = u'宋体'  #字体为'Times New Roman'
    font1.bold = True   #加粗
    style1.font = font1

    table = file.add_sheet(u'主机信息',cell_overwrite_ok=True)
    table.write(0,0,u'主机IP',style1)
    table.write(0,1,u'主机名',style1)
    table.write(0,2,u'用户名',style1)
    table.write(0,3,u'UID',style1)
    table.write(0,4,u'权限组',style1)
    table.write(0,5,u'系统版本',style1)
    file.save(filename)

    """
    # 打开文件
    workbook = xlrd.open_workbook(r'demo.xlsx')
    # 获取所有sheet
    print workbook.sheet_names() # [u'sheet1', u'sheet2']
    sheet2_name = workbook.sheet_names()[1]

    # 根据sheet索引或者名称获取sheet内容
    sheet2 = workbook.sheet_by_index(1) # sheet索引从0开始
    sheet2 = workbook.sheet_by_name('sheet2')

    # sheet的名称，行数，列数
    print sheet2.name,sheet2.nrows,sheet2.ncols

    # 获取整行和整列的值（数组）
    rows = sheet2.row_values(3) # 获取第四行内容
    cols = sheet2.col_values(2) # 获取第三列内容
    print rows
    print cols

    # 获取单元格内容
    print sheet2.cell(1,0).value.encode('utf-8')
    print sheet2.cell_value(1,0).encode('utf-8')
    print sheet2.row(1)[0].value.encode('utf-8')

    # 获取单元格内容的数据类型
    print sheet2.cell(1,0).ctype
    """
def write_text(filename):
    oldWb = xlrd.open_workbook(filename)
    print oldWb
    newWb = copy(oldWb)
    print newWb
    newWs = newWb.get_sheet(0)

    newWs.write(1, 0, "value1")
    newWs.write(1, 1, "value2")
    newWs.write(1, 2, "value3")
    print "write new values ok"



if __name__ == '__main__':
    global filename
    filename = 'hostinfo.xls'
    if os.path.exists(filename):
         write_text(filename)
    else:
         write_title(filename)

