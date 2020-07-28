import wx
import os
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas # Matplotlib埋め込み用バックエンド
from matplotlib import pyplot as plt
import csv
import pandas as pd
import numpy as np

app = wx.App()
frm = wx.Frame(None, title="OIM text file to csv converter", size=(1000,550))
notebook = wx.Notebook(frm, wx.ID_ANY)

# パネル
panel = wx.Panel(notebook, -1) # OIMtxt2csv用パネル
panel_analysis = wx.Panel(notebook, wx.ID_ANY)

# notebookにページを追加
notebook.InsertPage(0, panel, 'txt2csv')
notebook.InsertPage(1, panel_analysis, 'Analysis')


# ファイルダイアログを開く関数
def openFile(event):
    with wx.FileDialog(None, "Select txt file", wildcard="txt files (*.txt)|*.txt",
            style=wx.ID_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dialog.GetPath() # パスをGet
        text.SetValue(pathname) # textfieldにpathを入れる
        
        with open(pathname, encoding='utf-8') as f:
            lines = f.readlines()
        
        # ファイルの種類を判定
        if 'Chart:  Grain Size (diameter)\n' in lines:
            radio_grain.SetValue(True) # grain size ラジオボタンにチェックを入れる
        elif 'Chart:  Grain Shape Aspect Ratio\n' in lines:
            radio_aspect.SetValue(True) # aspect ratioのradioにチェックを入れる


# ラジオボタンでGrain sizeを選択したときの動作
def selectGrainsize(event):
    lst.DeleteAllColumns()
    lst.InsertColumn(0, "Grain size", wx.LIST_FORMAT_LEFT)
    lst.InsertColumn(1, "Area fraction", wx.LIST_FORMAT_LEFT)

# ラジオボタンでAspect ratioを選択したときの動作
def selectAspectratio(event):
    lst.DeleteAllColumns()
    lst.InsertColumn(0, "Aspect ratio", wx.LIST_FORMAT_LEFT)
    lst.InsertColumn(1, "Number fraction", wx.LIST_FORMAT_LEFT)

# saveボタンの動作
def saveBtnClicked(event):
    with wx.FileDialog(None, "Save file", wildcard="csv files (*.csv)|*.csv",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        path = fileDialog.GetPath() # ダイヤログからpathを取得
        try:
            filename = text.GetValue() # テキストフィールドからpathを取得
            with open(filename, encoding='utf-8') as f:
                lines = f.readlines() # ファイルの全ての行をstrで格納
                newline = [] # 処理後の文字列格納用配列の初期化
                data = [] # data格納用配列を初期化
        
                # grain sizeラジオボタンにチェックが入っている場合の動作
                if radio_grain.GetValue() == True:
                    headertext = ['grain size', 'area fraction']
                    data.append(headertext)
                    for i in range(8, len(lines)-5):
                        rline = lines[i].split(sep='; ') # それぞれの行を'; 'で区切りrlineにリスト形式で格納
                        rline.pop(2) # 改行コードを削除する
                        floatrline = [float(i) for i in rline]
                        data.append(floatrline)
        
                    # csvファイルに書き込み
                    with open(path, 'w', encoding='utf-8', newline='\n') as f:
                        writer = csv.writer(f)
                        writer.writerows(data)

                elif radio_aspect.GetValue() == True:
                    headertext = ['aspect ratio', 'number fraction']
                    data.append(headertext)
                    for i in range(6, len(lines)-5):
                        rline = lines[i].split(sep='; ') # それぞれの行を'; 'で区切りrlineにリスト形式で格納
                        rline.pop(2) # 改行コードを削除する
                        floatrline = [float(i) for i in rline]
                        data.append(floatrline)
                    
                    # csvファイルに書き込み
                    with open(path, 'w', encoding='utf-8', newline='\n') as f:
                        writer = csv.writer(f)
                        writer.writerows(data)

        except IOError:
            wx.LogError("Cannot save current file")



# showボタンの動作
def showBtnClicked(event):
    fn = text.GetValue()
    if fn == '':
        wx.MessageBox(u'ファイルを選択してください', u'Error', wx.ICON_EXCLAMATION)

    else:
        # Open selected file
        with open(fn, encoding="utf-8") as f:
            lines = f.readlines()
    
            newlines = []
            col1 = [] # Grain size or Aspectratio
            col2 = [] # Area fraction of Number fraction
    
            # grain sizeのラジオボタンにチェックが入っている場合の動作
            if radio_grain.GetValue() == True:
                if not 'Chart:  Grain Size (diameter)\n' in lines:
                    wx.MessageBox(u'正しいファイルを選択してください', u'正しいファイル選択', wx.ICON_EXCLAMATION)
                else:
                    for i in range(8, len(lines)-5):
                        rline = lines[i].split(sep="; ")
                        rline.pop(2)
                        col1.append(float(rline[0]))
                        col2.append(float(rline[1]))
                        lst.InsertItem(i-8,rline[0])
                        lst.SetItem(i-8,1,rline[1])
                    
                    h.set_xdata(col1)
                    h.set_ydata(col2)
                    ax.set_xlim(min(col1), max(col1))
                    ax.set_ylim(min(col2), max(col2))
                    ax.set_xlabel('Diameter (micron)')
                    ax.set_ylabel('Area fraction')
                    canvas.draw()
            
            
            # aspect ratioのラジオボタンにチェックが入っている場合の動作　
            elif radio_aspect.GetValue() == True:
                if not 'Chart:  Grain Shape Aspect Ratio\n' in lines:
                    wx.MessageBox(u'正しいファイルを選択してください', u'正しいファイル選択', wx.ICON_EXCLAMATION)
    
                else:
                    for i in range(6, len(lines)-5):
                        rline = lines[i].split(sep="; ") # ; でデータを区切る
                        rline.pop(2) # 改行コードを取り除く
                        col1.append(float(rline[0])) # xデータ用の配列にappend
                        col2.append(float(rline[1])) # yデータ用の配列にappend
                        lst.InsertItem(i-6,rline[0]) # GUIの表の1列目にaspect ratioを挿入
                        lst.SetItem(i-6,1,rline[1]) # 2列目にNumber fractionを挿入
        
                    h.set_xdata(col1) # xデータのセット
                    h.set_ydata(col2) # yデータのセット
                    ax.set_xlim(min(col1), max(col1)) # x軸の設定
                    ax.set_ylim(min(col2), max(col2)) # y軸の設定
                    ax.set_xlabel('Aspect ratio')
                    ax.set_ylabel('Number fraction')
                    canvas.draw() # Canvasの更新
        
            # チェックが入っていないときは何もしない
            else:
                pass
                    


# タイトルの設定
titlelabel = wx.StaticText(panel, -1, label="OIMtxt2csv Converter")
titlefont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
titlelabel.SetFont(titlefont)
    
# ファイルダイアログ
label1 = wx.StaticText(panel, -1, label="File:")
text = wx.TextCtrl(panel, -1)
btn = wx.Button(panel, -1, 'Open') # for file dialog open
btn.Bind(wx.EVT_BUTTON, openFile)

# ラジオボタンの設定
radio_label = wx.StaticText(panel, -1, label="File type")
radio_grain = wx.RadioButton(panel, label="grain size")
radio_grain.Bind(wx.EVT_RADIOBUTTON, selectGrainsize)
radio_aspect = wx.RadioButton(panel, label="aspect ratio")
radio_aspect.Bind(wx.EVT_RADIOBUTTON, selectAspectratio)

# initial figure
fig = plt.Figure()
ax = fig.add_subplot(111)
h, = ax.plot([1], [1])
plt.show()

# matplotlib canvas
canvas = FigureCanvas(panel, wx.ID_ANY, fig)

# List
lst = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT)
lst.InsertColumn(0, "Grain size", wx.LIST_FORMAT_LEFT,150)
lst.InsertColumn(1, "Area fraction", wx.LIST_FORMAT_LEFT,150)

#buttons
showbtn = wx.Button(panel, -1, "Show")
showbtn.Bind(wx.EVT_BUTTON, showBtnClicked)

savebtn = wx.Button(panel, wx.ID_ANY, 'Save')
savebtn.Bind(wx.EVT_BUTTON, saveBtnClicked)


## layout #############################
# file selector layout
sizer1 = wx.BoxSizer(wx.HORIZONTAL)
sizer1.Add(label1, flag=wx.RIGHT, border=10)
sizer1.Add(text, flag=wx.RIGHT, border=10)
sizer1.Add(btn)
#panel.SetSizer(sizer1)

# radio btns layout
radiosizer1 = wx.BoxSizer(wx.HORIZONTAL)
radiosizer1.Add(radio_grain, flag=wx.ALL, border=5)
radiosizer1.Add(radio_aspect, flag=wx.ALL, border=5)

# list and show btn layout
#lstsizer = wx.BoxSizer(wx.HORIZONTAL)
#lstsizer.Add(lst, flag=wx.ALIGN_CENTER_VERTICAL)
#lstsizer.Add(showbtn, flag=wx.ALIGN_CENTER_VERTICAL)
#lstsizer.Add(savebtn)

#btn layout
btnsizer = wx.BoxSizer(wx.HORIZONTAL)
btnsizer.Add(showbtn, flag=wx.ALL, border=5)
btnsizer.Add(savebtn, flag=wx.ALL, border=5)

# vertical layout
sizerV1 = wx.BoxSizer(wx.VERTICAL)
sizerV1.Add(titlelabel, flag=wx.BOTTOM, border=10)
sizerV1.Add(sizer1, flag=wx.BOTTOM, border=10)
sizerV1.Add(radio_label, flag=wx.BOTTOM, border=5)
sizerV1.Add(radiosizer1, flag=wx.ALL, border=5)
#sizerV1.Add(lstsizer)
sizerV1.Add(lst, flag= wx.TOP | wx.BOTTOM, border=10)
sizerV1.Add(btnsizer)

sizertotall = wx.BoxSizer(wx.HORIZONTAL)
sizertotall.Add(sizerV1, flag=wx.ALL, border=10)
sizertotall.Add(canvas, flag=wx.ALL, border=10)
panel.SetSizer(sizertotall)

## Analysis panel
def openBtn2Clicked(event):
    with wx.FileDialog(None, "Select txt file", wildcard="csv files (*.csv)|*.csv",
            style=wx.ID_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dialog.GetPath() # パスをGet
        fileent1.SetValue(pathname) # textfieldにpathを入れる

    with open(pathname, encoding='utf-8') as f:
        reader = csv.reader(f)
        l = [row for row in reader]
    header = l.pop(0) # headerを抽出
    data = pd.read_csv(pathname) # csv ファイルをデータフレームに
    # ファイルがgrain sizeの場合
    if 'grain size' in header:
        radio_grain2.SetValue(True) # ラジオボタンをgrain sizeに
        averageGS = sum(data['grain size'] * data['area fraction']) # 平均粒径の算出
        stdgrain = np.sqrt(sum((data['grain size'] - averageGS)**2 * data['area fraction'])) # 標準偏差の算出
        alldata = pd.DataFrame([averageGS, stdgrain])
        alldata.index = ['Average grain size', 'Standard deviation']

        # Listの設定
        lstana.DeleteAllColumns()
        lstana.InsertColumn(0, "Average grain size", wx.LIST_FORMAT_LEFT)
        lstana.InsertColumn(1, "Standard deviation", wx.LIST_FORMAT_LEFT)
        lstana.InsertItem(0,str(averageGS)) # GUIの表の1列目にaspect ratioを挿入
        lstana.SetItem(0,1,str(stdgrain)) # 2列目にNumber fractionを挿入
    
    # ファイルがaspect ratioの場合
    elif 'aspect ratio' in header:
        radio_aspect2.SetValue(True) # ラジオボタンをaspect ratioに
        aveaspect = sum(data['aspect ratio'] * data['number fraction']) # 平均aspect ratioを算出
        stdaspect = np.sqrt(sum((data['aspect ratio'] - aveaspect) ** 2 *data['number fraction'])) # aspect ratioの標準偏差
        overaspect = sum(data[data['aspect ratio']>0.5]['number fraction']) # aspect ratioが0.5より上の値のnumber fractionの合計
        underaspect = sum(data[data['aspect ratio']<=0.5]['number fraction']) # aspect ratioが0.5以下の値のnumber fractionの合計

        # 計算したデータをデータフレームにまとめる
        alldata = pd.DataFrame(
            [aveaspect, stdaspect, overaspect, underaspect]
        )
        alldata.index = ['Average aspect ratio', 'Standard deviation', '> 0.5', '<= 0.5']
        # Listの設定
        lstana.DeleteAllColumns()
        lstana.InsertColumn(0, "Average aspect ratio", wx.LIST_FORMAT_LEFT)
        lstana.InsertColumn(1, "Standard deviation", wx.LIST_FORMAT_LEFT)
        lstana.InsertColumn(2, "over 0.5", wx.LIST_FORMAT_LEFT)
        lstana.InsertColumn(3, "under 0.5", wx.LIST_FORMAT_LEFT)
        lstana.InsertItem(0,str(aveaspect)) # GUIの表の1列目にaspect ratioを挿入
        lstana.SetItem(0,1,str(stdaspect)) # 2列目にNumber fractionを挿入
        lstana.SetItem(0,2, str(overaspect))
        lstana.SetItem(0,3,str(underaspect))

# saveボタンの動作
def saveBtn2Clicked(event):
    with wx.FileDialog(None, "Save file", wildcard="csv files (*.csv)|*.csv",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        path = fileDialog.GetPath() # ダイヤログからpathを取得

        if radio_grain2.GetValue() == True:
            aveGS = float(lstana.GetItem(0,0).GetText())
            stdGS = float(lstana.GetItem(0,1).GetText())
            alldata = pd.DataFrame(
                    [aveGS, stdGS]
            )
            alldata.index = ['Average grain size', 'Standard deviation']
            alldata.to_csv(path, header=False)
        
        elif radio_aspect2.GetValue() == True:
            aveAR = float(lstana.GetItem(0,0).GetText())
            stdAR = float(lstana.GetItem(0,1).GetText())
            overAR = float(lstana.GetItem(0,2).GetText())
            underAR = float(lstana.GetItem(0,3).GetText())
            alldata = pd.DataFrame(
                [aveAR, stdAR, overAR, underAR]
            )
            alldata.index = ['Average aspect ratio', 'Standard deviation', '> 0.5', '<= 0.5']
            alldata.to_csv(path, header=False)



# title
anatitlelbl = wx.StaticText(panel_analysis, wx.ID_ANY, label="Analysis")
titlefont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
anatitlelbl.SetFont(titlefont)

# ファイルを選択
filet1 = wx.StaticText(panel_analysis, wx.ID_ANY, label='File')
fileent1 = wx.TextCtrl(panel_analysis, wx.ID_ANY)
openbtn2 = wx.Button(panel_analysis, wx.ID_ANY, label='Open')
openbtn2.Bind(wx.EVT_BUTTON, openBtn2Clicked)
savebtn2 = wx.Button(panel_analysis, wx.ID_ANY, label='Save')
savebtn2.Bind(wx.EVT_BUTTON, saveBtn2Clicked)

# ラジオボタン
filetypetext = wx.StaticText(panel_analysis, wx.ID_ANY, label='File type')
radio_grain2 = wx.RadioButton(panel_analysis, wx.ID_ANY, label='grain size')
radio_aspect2 = wx.RadioButton(panel_analysis, wx.ID_ANY, label='aspect ratio')
# radio buttonのレイアウト
radiobtnlayout = wx.BoxSizer(wx.HORIZONTAL)
radiobtnlayout.Add(radio_grain2)
radiobtnlayout.Add(radio_aspect2)

radioall = wx.BoxSizer(wx.VERTICAL)
radioall.Add(filetypetext)
radioall.Add(radiobtnlayout)
# 分析用list
lstana = wx.ListCtrl(panel_analysis, wx.ID_ANY, style=wx.LC_REPORT)

filesizer = wx.BoxSizer(wx.HORIZONTAL)
filesizer.Add(filet1)
filesizer.Add(fileent1)
filesizer.Add(openbtn2)

totalllayout2 = wx.BoxSizer(wx.VERTICAL)
totalllayout2.Add(anatitlelbl)
totalllayout2.Add(filesizer)
totalllayout2.Add(radioall)
totalllayout2.Add(lstana)
totalllayout2.Add(savebtn2)
panel_analysis.SetSizer(totalllayout2)
frm.Show()

app.MainLoop()
