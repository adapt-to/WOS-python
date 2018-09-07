#coding:utf-8
import requests
import bs4
import time
import sys
import threading
import html5lib

from qt4_article import *
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

'''
class MyThread(QtCore.QThread):
	def __init__(self):
		super(MyThread, self).__init__()
		self.slot = slot_con()

	def run(self):
		self.slot.con_serial("开始下载文献......")
'''

class slot_con(QtGui.QWidget, Ui_Form): # 定义槽函数
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.setupUi(self)
		self.calibration_status = False
		self.parameter_status = False
		self.return1= return_text()
		self.article = DownArticle()

	def con_serial(self, message): #槽函数
		starttime = time.strftime("%H:%M:%S - ", time.localtime(time.time()))

		self.textBrowser_1.append(starttime + str(message))
		textcursor = QtGui.QTextCursor(self.textBrowser_1.textCursor())
		self.textBrowser_1.moveCursor(textcursor.atStart())

		text1 = self.return1.request1(str(message))
		if text1 == 1: #开始下载标志

			a = self.article.get_down_url()
			for i in range(self.article.nums + 1):
				self.article.writer(" ", self.article.path, self.article.get_contents(self.article.urls[i]) +  "\n文献地址:"+ self.article.urls[i] + "\n" , i)
				bb = float((i / self.article.nums) * 100)
				self.con_serial(bb)
			self.con_serial("下载完成！！！")
			return  1

		text2 = str(text1)
		endtime = time.strftime("%H:%M:%S - ", time.localtime(time.time()))
		self.textBrowser_1.append(endtime + str(message) + text2)
		textcursor = QtGui.QTextCursor(self.textBrowser_1.textCursor()) #自动滚屏
		self.textBrowser_1.moveCursor(textcursor.atStart())
		#return text2

	@QtCore.pyqtSignature("")
	def on_pushButton_1_clicked(self):
		self.article.target = self.lineEdit_1.text()
		if  self.article.target: # 不为空进入
			self.con_serial(self.article.target) # 调用con_serial函数
		#self.textBrowser_1.append("保存成功\n")

	@QtCore.pyqtSignature("")
	def on_pushButton_2_clicked(self):
		self.article.path = self.lineEdit_2.text()
		if  self.article.path:
			self.con_serial(self.article.path)

	@QtCore.pyqtSignature("")
	def on_pushButton_3_clicked(self):
		self.article.nums = int(self.lineEdit_3.text()) -1 #填写的下载数减1
		if  self.article.nums :
			self.con_serial(str(self.article.nums))

	@QtCore.pyqtSignature("")
	def on_pushButton_4_clicked(self):
		#thread = MyThread()
		#thread.start()
		self.con_serial("开始下载文献......")


class return_text():
	def __init__(self):
		pass
	def request1(self, message):
		if message == "开始下载文献......":
			return 1

		elif type(message) == float:
			return "已下载" + str(message)

		elif message == "下载完成！！！":
			return  "下载完成！！！"

		else:
			return "保存成功"






class DownArticle():
	def __init__(self):
		'''
		本程序仅适用于在校园网状态下，爬取 web of science （WOS）网址的文献摘要。

		'''
		self.server = "http://apps.webofknowledge.com/"
		#self.target = "http://apps.webofknowledge.com/UseSpellSuggestion.do?action=takeSuggestion&product=UA&SID=5DXFiaPNvTXGNviCDJj&search_mode=GeneralSearch&update_back2search_link_param=yes&viewType=summary&qid=67" #这里网址更换为搜索后的网址
		self.target = " "
		self.names = []
		self.urls = []
		self.nums = 0
		self.path = " "

	def get_down_url(self):
		req = requests.get(url = self.target)
		#req = urllib.request.urlopen(self.target)
		html = req.text
		#html = req.read()
		bf = bs4.BeautifulSoup(html,features="html5lib")
		#print (bf)
		texts = bf.find_all("a", class_ = "smallV110 snowplow-full-record", limit=1) # class_ = "smallV110 snowplow-full-record"
		for i in texts:
			self.names.append(i.text)
			self.urls.append(self.server + i.get("href"))
		if len(self.names) > 1:
			self.nums = len(self.names)
			return 1
		for m in range(self.nums):
			n = self.urls[0]
			#print (n)
			nn = n.split("=")
			#print ("nn=",nn)
			nn[-1] = str(m+2)
			nnn = "=".join(nn)
			#print ("nnn=",nnn)
			self.urls.append(nnn)
			#print("nn=",nn)
		
		return self.urls
	def get_contents(self,target):
		req = requests.get(url = target)
		html = req.text
		bf = bs4.BeautifulSoup(html,features="html5lib")
		
		search_title = bf.find_all("div", class_ = "title")

		qikan = " "
		search_qikan = bf.find_all("div", class_="title3")
		for i in range(len(search_qikan)):
			if "出版商" in search_qikan[i].text or "Publisher" in search_qikan[i].text:
				title3_1 = search_qikan[i].string.parent
				div_1 = title3_1.parent  # 获取父节点 div
				for string in div_1.stripped_strings:  # 循环获取div内的内容
					qikan += str(string + "  ")

		list_message = []
		list_name = []
		search_pub = bf.find_all("p", class_ = "FR_field")
		for i in range(len(search_pub)):
			if "作者:" in search_pub[i].text or "By:" in search_pub[i].text:
				n = bs4.BeautifulSoup(str(search_pub[i]), features="html5lib")
				aa = n.find_all('a', title = "查找此作者的更多记录")
				if len(aa) == 0:
					aa = n.find_all('a', title = "Find more records by this author")
				for m in aa:
					list_name.append(m.string)

			if "DOI:" in search_pub[i].text or "出版年:" in search_pub[i].text or "Published:" in search_pub[i].text or "KeyWords Plus:" in search_pub[i].text:
				list_message.append(search_pub[i].text)
		
		name = " ; ".join(list_name)
		message = " ".join(list_message)

		search_number = bf.find_all("span", class_ = "large-number") #被引次数



		texts = bf.find_all("div", class_ = "block-record-info")
		for i in range(len(texts)):
			a_bf = str(texts[i])
			
			if "摘要" in a_bf or "Abstract" in a_bf:
				return search_title[0].text + "\n" +"被引次数:"+search_number[0].text+" 引用文献数:"+ search_number[1].text +"\n"+"作者:" + name + "\n" + qikan + message + "\n" + texts[i].text
		
		return search_title[0].text + "\n" +"被引次数:"+search_number[0].text+" 引用文献数:"+ search_number[1].text +"\n"+"作者:" + name + "\n" + qikan + message + "\n" + "该文献无摘要"
			

			#break
	def writer(self,name,path,text,i):
		write_flag = True
		with open(path, 'a',encoding='utf-8') as f:
			f.write(str(i+1) + name)
			if text:
			    f.writelines(text)
			else:
				f.writelines("该文章无摘要")
			f.write('\n')

class slot(QtGui.QMainWindow):
	def __init__(self,ui,tab):
		QtGui.QMainWindow.__init__(self)
		self.tab = tab

	def graphical_intf(self):
		self.con = slot_con(self.tab)
		self.con.setGeometry(QtCore.QRect(0, 0, 740, 480))
	# self.con.show()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)

	widget = QtGui.QTabWidget()
	widget.resize(750, 500)
	a = QtGui.QFrame(widget)
	a.setGeometry(QtCore.QRect(0, 0, 740, 480))
	w = slot(widget,a)
	w.graphical_intf()


	widget.show()

	'''
	Form = QtGui.QTabWidget()
	ui = Ui_Form()
	ui.setupUi(Form)
	Form.show()
 	'''
	sys.exit(app.exec_())
