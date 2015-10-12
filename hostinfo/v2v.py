# -*- coding: utf-8 -*-
import xlwt
import xlrd
import os
from xlutils.copy import copy

def create_xls(filename):
    styleBoldRed   = xlwt.easyxf('font: color-index black, bold on')
    headerStyle = styleBoldRed
    file = xlwt.Workbook()
    table = file.add_sheet(u'主机信息',cell_overwrite_ok=True)
    table.write(0,0,u'主机IP',headerStyle)
    table.write(0,1,u'主机名',headerStyle)
    table.write(0,2,u'用户名',headerStyle)
    table.write(0,3,u'UID',headerStyle)
    table.write(0,4,u'权限组',headerStyle)
    table.write(0,5,u'系统版本',headerStyle)
    file.save(filename)

def write_xls(filename):
    oldWb = xlrd.open_workbook(filename,formatting_info=True)
    newWb = copy(oldWb)
    newWs = newWb.get_sheet(0)
    sheet2 = oldWb.sheet_by_index(0)
    col=sheet2.ncols
    row=sheet2.nrows
    print('row=%d' %row)
    print('col=%d' %col)
    newWs.write(row, 0, "value1")
    newWs.write(row, 1, "value2")
    newWs.write(row, 2, "value3")
    newWs.write_merge(1, 2, 0, 0, 'Long Cell')
    newWb.save(filename)

if __name__ == '__main__':
    global filename
    filename = 'hostinfo.xls'
    if os.path.exists(filename):
         write_xls(filename)
    else:
         create_xls(filename)

