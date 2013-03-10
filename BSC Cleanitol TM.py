
import wx

import dircache
import os
import sys
import time
import glob
import distutils
import distutils.file_util
import webbrowser

#from win32com.shell import shell
#import win32api
#import win32con
import fnmatch

basedir = "."

import _winreg

KEY_WOW64_64KEY = 256



def encodeFilename(s):
	"""
	@param s The name of the file (of type unicode)
	"""

	if type(s) == type( '' ):
		return s
	assert type(s) == type(u'')

	return s.encode(sys.getfilesystemencoding(), 'ignore')

def GetListOfAllFiles( dlg, maxisFolder, pluginsFolder ):
	listFiles = {}
	if (maxisFolder != ''):
		for (root, dirs, files,) in os.walk(maxisFolder):
			dlg.Increment1st()
			wx.Yield()
			listFiles[root] = files

	if (pluginsFolder != ''):
		for (root, dirs, files,) in os.walk(pluginsFolder):
			dlg.Increment1st()
			wx.Yield()
			listFiles[root] = files

	return listFiles

def Match2Files( fileName, matcher):
	fN = fileName.replace('[', '&o').replace(']', '&c')
	m = matcher.replace('[', '&o').replace(']', '&c')
	b = fnmatch.fnmatch(fN, m)
	return b

def MatchFiles( fileNames, matcher):
	fNs = [ fileName.replace('[', '&o').replace(']', '&c') for fileName in fileNames ]
	m = matcher.replace('[', '&o').replace(']', '&c')
	return fnmatch.filter(fNs, m)

def locate( inputFile, dlg, rtc ):
	points = rtc.GetFont().GetPointSize()
	font = wx.Font((points + 1), wx.MODERN, wx.NORMAL, wx.BOLD, False)
	rtc.Log(((((((('*' * 50) + '\n') + (' ' * 20)) + MsgReportBIG) + '\n') + ('*' * 50)) + '\n'), wx.TextAttr('ORANGE', wx.NullColour, font))
	#df = shell.SHGetDesktopFolder()
	#pidl = df.ParseDisplayName(0, None, '::{450d8fba-ad25-11d0-98a8-0800361b1103}')[1]
	mydocs = wx.StandardPaths.Get().GetDocumentsDir()
	#mydocs = shell.SHGetPathFromIDList(pidl)
	try:
		maxisKey = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Maxis\\SimCity 4', 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY )
		maxisFolder = _winreg.QueryValueEx( maxisKey, 'Install Dir' )[0]
		_winreg.CloseKey( maxisKey )
		maxisFolder = os.path.join(maxisFolder, 'plugins')
	except:
		maxisFolder = ''
	pluginsFolder = os.path.join(mydocs, u'SimCity 4\\Plugins')
	if maxisFolder == '':
		rtc.Log( "Maxis\t\t:", wx.TextAttr('RED', wx.NullColour, font) )
		rtc.Log( MsgNotFound+"\n", wx.TextAttr('RED', wx.NullColour, font) )
	else:
		rtc.Log( "Maxis\t\t: ", wx.TextAttr('GREEN', wx.NullColour, font) )
		rtc.Log( maxisFolder+"\n", wx.TextAttr('GREEN', wx.NullColour, font) ) 
	rtc.Log( "Plugins\t: ", wx.TextAttr('GREEN', wx.NullColour, font) )
	rtc.Log( pluginsFolder+"\n" , wx.TextAttr('GREEN', wx.NullColour, font) ) 
	f = open(inputFile, 'rt')
	filesList = f.readlines()
	f.close()
	lines = [ x.strip().replace('\n', '') for x in filesList ]
	filesList = []
	dependancies = []
	for line in lines:
		if (line == ''):
			pass
		else:
			sp = line.split(';')
			if ((len(sp) == 1) and len(sp[0])):
				filesList.append(sp[0].strip())
			elif ((len(sp) > 1) and len(sp[0])):
				url = ';'.join(sp[1:])
				dependancies.append({'fileName': sp[0].strip(),
				 'url': url.strip(),
				 'present': False})

	files2Move = []
	reporting = {}
	for f in filesList:
		reporting[f] = []

	filesOnHD = GetListOfAllFiles(dlg, maxisFolder, pluginsFolder)
	allFiles = []
	for (folder, files,) in filesOnHD.iteritems():
		folderFiles = [ os.path.join( folder, f ) for f in files ]
		allFiles += folderFiles

	for matcher in filesList:
		dlg.Increment1st()
		wx.Yield()
		matches = MatchFiles( allFiles, "*\\"+matcher )
		for x in matches:
			if (x not in files2Move):
				files2Move.append(x)
			srcFileName = matcher
			try:
				reporting[srcFileName].append(x)
			except:
				reporting[srcFileName] = [x]
			rtc.Log(('%s ' % srcFileName), wx.TextAttr('BLUE', wx.NullColour))
			rtc.Log(('(%s) ' % os.path.split(x)[1]), wx.TextAttr('BLUE', wx.NullColour, font))
			rtc.Log(MsgFoundIn)
			rtc.Log(('%s\n' % os.path.split(x)[0]), wx.TextAttr('ORANGE', wx.NullColour))
	for depend in dependancies:
		if depend['present']:
			pass
		else:
			fileName = depend['fileName']
			wx.Yield()
			matches = MatchFiles(allFiles, "*\\"+fileName)
			if matches != []:
				depend['present'] = True
	if 0:
		for (folder, files,) in filesOnHD.iteritems():
			for fileOnHD in files:
				dlg.Increment1st()
				for matcher in filesList:
					wx.Yield()
					if Match2Files(fileOnHD, matcher):
						x = os.path.join(folder, fileOnHD)
						if (x not in files2Move):
							files2Move.append(x)
						srcFileName = matcher
						try:
							reporting[srcFileName].append(x)
						except:
							reporting[srcFileName] = [x]
						rtc.Log(('%s ' % srcFileName), wx.TextAttr('BLUE', wx.NullColour))
						rtc.Log(('(%s) ' % os.path.split(x)[1]), wx.TextAttr('BLUE', wx.NullColour, font))
						rtc.Log(MsgFoundIn)
						rtc.Log(('%s\n' % os.path.split(x)[0]), wx.TextAttr('ORANGE', wx.NullColour))

				for depend in dependancies:
					if depend['present'] :
						pass
					else:
						fileName = depend['fileName']
						wx.Yield()
						if Match2Files(fileOnHD, fileName):
							depend['present'] = True



	for k in filesList:
		v = reporting[k]
		if (v == []):
			rtc.Log(('%s ' % k), wx.TextAttr('BLUE', wx.NullColour, font))
			rtc.Log((MsgNotFound + '\n'))

	bOk = True
	for depends in dependancies:
		if (not depends['present']):
			bOk = False
			rtc.Log(MsgMissing, wx.TextAttr('RED', wx.NullColour, font))
			rtc.Log(('%s ' % depends['fileName']), wx.TextAttr('RED', wx.NullColour))
			rtc.Log((MsgDld % depends['url']))

	if bOk:
		rtc.Log(MsgUptodate, wx.TextAttr('BLACK', wx.NullColour, font))
	else:
		rtc.Log(MsgNotUptodate, wx.TextAttr('RED', wx.NullColour, font))

def process( inputFile, dlg, rtc ):
	points = rtc.GetFont().GetPointSize()
	font = wx.Font((points + 1), wx.MODERN, wx.NORMAL, wx.BOLD, False)
	rtc.Log(((((((('*' * 50) + '\n') + (' ' * 20)) + MsgReportBIG) + '\n') + ('*' * 50)) + '\n'), wx.TextAttr('ORANGE', wx.NullColour, font))
	mydocs = wx.StandardPaths.Get().GetDocumentsDir()
	try:
		maxisKey = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Maxis\\SimCity 4', 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY )
		maxisFolder = _winreg.QueryValueEx( maxisKey, 'Install Dir' )[0]
		_winreg.CloseKey( maxisKey )
		maxisFolder = os.path.join(maxisFolder, 'plugins')
	except:
		maxisFolder = ''
	pluginsFolder = os.path.join(mydocs, 'SimCity 4\\Plugins')
	
	if maxisFolder == '':
		rtc.Log( "Maxis\t\t:", wx.TextAttr('RED', wx.NullColour, font) )
		rtc.Log( MsgNotFound+"\n", wx.TextAttr('RED', wx.NullColour, font) )
	else:
		rtc.Log( "Maxis\t\t: ", wx.TextAttr('GREEN', wx.NullColour, font) )
		rtc.Log( maxisFolder+"\n", wx.TextAttr('GREEN', wx.NullColour, font) ) 
	rtc.Log( "Plugins\t: ", wx.TextAttr('GREEN', wx.NullColour, font) )
	rtc.Log( pluginsFolder+"\n" , wx.TextAttr('GREEN', wx.NullColour, font) ) 
	
	mainBackupFolder = os.path.join(mydocs, 'SimCity 4\\BSC_Cleanitol')
	try:
		os.mkdir(mainBackupFolder)
	except OSError:
		pass
	instanceFolder = time.strftime('%Y%m%d')
	instanceFolder = os.path.join(mainBackupFolder, instanceFolder)
	instance = 1
	while 1:
		try:
			backupFolder = instanceFolder+"_%02d"%instance
			os.mkdir( backupFolder )
			break
		except OSError:
			instance += 1
		pass
		
	rtc.Log( "Backup\t: ", wx.TextAttr('GREEN', wx.NullColour, font) )
	rtc.Log( backupFolder+"\n" , wx.TextAttr('GREEN', wx.NullColour, font) ) 
		
	f = open(inputFile, 'rt')
	filesList = f.readlines()
	f.close()
	lines = [ x.strip().replace('\n', '') for x in filesList ]
	dependancies = []
	for line in lines:
		if (line == ''):
			continue
		sp = line.split(';')
		if ((len(sp) == 1) and len(sp[0])):
			filesList.append(sp[0].strip())

	files2Move = []
	reporting = {}
	for f in filesList:
		reporting[f] = []

	filesOnHD = GetListOfAllFiles(dlg, maxisFolder, pluginsFolder)
	allFiles = []
	for (folder, files,) in filesOnHD.iteritems():
		folderFiles = [ os.path.join( folder, f ) for f in files ]
		allFiles += folderFiles

	for matcher in filesList:
		dlg.Increment1st()
		wx.Yield()
		matches = MatchFiles( allFiles, "*\\"+matcher )
		for x in matches:
			if (x not in files2Move):
				files2Move.append(x)
			srcFileName = matcher
			try:
				reporting[srcFileName].append(x)
			except:
				reporting[srcFileName] = [x]
			
	for depend in dependancies:
		if depend['present']:
			pass
		else:
			fileName = depend['fileName']
			dlg.Increment1st()
			wx.Yield()
			matches = MatchFiles(allFiles, "*\\"+fileName)
			if matches != []:
				depend['present'] = True
	if 0:
		for (folder, files,) in filesOnHD.iteritems():
			for fileOnHD in files:
				dlg.Increment1st()
				for matcher in filesList:
					wx.Yield()
					if Match2Files(fileOnHD, matcher):
						x = os.path.join(folder, fileOnHD)
						if ((x not in files2Move) and files2Move.append(x)):
							pass
						srcFileName = matcher
						try:
							reporting[srcFileName].append(x)
						except:
							reporting[srcFileName] = [x]

				for depend in dependancies:
					if depend['present']:
						continue
					fileName = depend['fileName']
					wx.Yield()
					if Match2Files(fileOnHD, fileName):
						depend['present'] = True
					
	undoName = os.path.join(backupFolder, 'undo.bat')
	undo = open(undoName, 'wt')
	
	for fileName in files2Move:
		dlg.Increment1st()
		wx.Yield()
		srcFileName = os.path.split( fileName )[1]
		destFileName = os.path.join( backupFolder, srcFileName )
		if os.path.exists( destFileName ):
			instance = 1
			while 1:
				dlg.Increment1st()
				wx.Yield()
				nameext = os.path.splitext( srcFileName )
				destFileName = os.path.join( backupFolder, nameext[0]+'_%02d'%instance+nameext[1] )
				if not os.path.exists( destFileName ):
					break
				instance += 1
		s = os.path.split(destFileName)[1]
		d = fileName.replace(pluginsFolder, u'..\\..\\Plugins')
		rtc.Log( '%s => %s\n' % (fileName.replace( pluginsFolder, '' ),s), wx.TextAttr('BLUE', wx.NullColour, font) )
		undo.write('copy "%s" "%s"\n' % ( encodeFilename( s ), encodeFilename( d ) ) )
		undo.flush()
		distutils.file_util.move_file(fileName, destFileName)
		#t = open( destFileName, "wb" )
		#t.close()
		
	undo.close()
	nameext = os.path.splitext(inputFile)
	reportFile = ((nameext[0] + '_result') + '.txt')
	reportFile2 = os.path.join(backupFolder, 'Cleanitol_result.html')
	report = open(reportFile, 'wt')
	report2 = open(reportFile2, 'wt')
	report2.write((('<html>\n <body>\n<H1>' + MsgCleanup.encode('iso-8859-15')) + '</H1>\n'))
	report.write(('*' * 50))
	report.write((('\n' + MsgCleanupBIG.encode('iso-8859-15')) + '\n'))
	report.write(('*' * 50))
	report.write('\n')
	for k in filesList:
		v = reporting[k]
		if ((v == []) and report.write((MsgReportNotFound % k.decode('iso-8859-15')).encode('iso-8859-15'))):
			report2.write((MsgHtmlReportNotFound % k.decode('iso-8859-15')).encode('iso-8859-15'))
			rtc.Log(('%s ' % k), wx.TextAttr('BLUE', wx.NullColour, font))
			rtc.Log((MsgNotFound + '\n'))

	report.write((MsgReportMove % (len(files2Move), backupFolder)).encode('iso-8859-15'))
	report2.write((MsgHtmlReportMove % (len(files2Move),backupFolder)).encode('iso-8859-15'))
	rtc.Log(('%d ' % len(files2Move)), wx.TextAttr('BLUE', wx.NullColour))
	rtc.Log(MsgMove)
	rtc.Log(('%s\n' % backupFolder), wx.TextAttr('PURPLE', wx.NullColour, font))
	if (len(dependancies) and report.write(('*' * 50))):
		report.write((('\n' + MsgDepBIG.encode('iso-8859-15')) + '\n'))
		report.write(('*' * 50))
		report.write('\n')
		report2.write((('<hr><H1>' + MsgDep.encode('iso-8859-15')) + '</H1>\n'))
		rtc.Log(((((((('*' * 50) + '\n') + (' ' * 12)) + MsgDepBIG) + '\n') + ('*' * 50)) + '\n'), wx.TextAttr('ORANGE', wx.NullColour, font))
		bOk = True
		for depends in dependancies:
			if depends['present']:
				bOk = False
				report.write(MsgMissing.encode('iso-8859-15'))
				report2.write((('<font color="red">' + MsgMissing.encode('iso-8859-15')) + '</font> '))
				report.write((MsgReportDld % (depends['fileName'],depends['url'])).encode('iso-8859-15'))
				report2.write((MsgHtmlReportDld % (depends['fileName'],depends['url'],depends['url'])).encode('iso-8859-15'))
				rtc.Log(MsgMissing, wx.TextAttr('RED', wx.NullColour, font))
				rtc.Log(('%s ' % depends['fileName']), wx.TextAttr('RED', wx.NullColour))
				rtc.Log((MsgDld % depends['url']))

		if (bOk and report.write(MsgUptodate.encode('iso-8859-15'))):
			report2.write(MsgHtmlUptodate.encode('iso-8859-15'))
			rtc.Log(MsgUptodate, wx.TextAttr('BLACK', wx.NullColour, font))
	report2.write((MsgHtmlUndo % undoName).encode('iso-8859-15'))
	report2.write('<hr></body></html>\n')
	report.write((MsgSaved % reportFile2).encode('iso-8859-15'))
	report.write((MsgUndo % undoName).encode('iso-8859-15'))
	rtc.Log(MsgSaved2, wx.TextAttr('BLUE', wx.NullColour))
	rtc.Log(('%s\n' % reportFile2), wx.TextAttr('PURPLE', wx.NullColour, font))
	rtc.Log(MsgUndo2, wx.TextAttr('BLUE', wx.NullColour))
	rtc.Log(('%s\n' % undoName), wx.TextAttr('PURPLE', wx.NullColour, font))
	report.close()
	report2.close()		
		
class ProcessDlg( wx.Dialog ):
	def __init__(self, parent, title = "Moving file, please wait") : #MsgTitle):
		pre = wx.PreDialog()
		pre.Create(parent, -1, 'BSC Cleanitol TM')
		self.PostCreate(pre)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.labelg1 = wx.StaticText(self, -1, title, size=(500, -1))
		sizer.Add(self.labelg1, 1, ((wx.EXPAND | wx.ALIGN_CENTRE) | wx.ALL), 5)
		self.g1 = wx.Gauge(self, -1, 32)
		self.g1.SetBezelFace(3)
		self.g1.SetShadowWidth(3)
		sizer.Add(self.g1, 0, ((wx.EXPAND | wx.ALIGN_CENTRE) | wx.ALL), 5)
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.g1.SetRange(32)
		self.maxg1 = 32
		self.valueg1 = 0

	def Increment1st(self):
		self.g1.Pulse()

	def OnCloseWindow(self, event):
		event.Veto()

class MainFrame( wx.Frame ):
	def __init__( self ):
		wx.Frame.__init__(self, None, title='BSC Cleanitol TM 2013.2 NAM Version')
		self.SetIcon(wx.Icon(os.path.join( basedir, 'cleanitol.ico' ), wx.BITMAP_TYPE_ICO))
		p = wx.Panel(self)
		label = wx.StaticText(p, -1, MsgFileList)
		txt = ''
		if (len(sys.argv) == 2):
			txt = os.path.abspath(sys.argv[1])
			if (not os.path.isfile(txt)):
				txt = ''
		self.fileName = wx.TextCtrl(p, -1, txt, size=(80, -1), style=wx.TE_READONLY)
		self.browse = wx.Button(p, -1, '...', size=(30, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse)
		self.bReport = wx.Button(p, -1, MsgLocate)
		self.Bind(wx.EVT_BUTTON, self.OnReport, self.bReport)
		self.bStart = wx.Button(p, -1, MsgBackup)
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.bStart)
		self.bQuit = wx.Button(p, -1, MsgQuit)
		self.Bind(wx.EVT_BUTTON, self.OnQuit, self.bQuit)
		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(label, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		box.Add(self.fileName, 1, ((wx.EXPAND | wx.ALIGN_CENTRE) | wx.ALL), 5)
		box.Add(self.browse, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		sizer.Add(box, 0, ((wx.GROW | wx.ALIGN_CENTER_VERTICAL) | wx.ALL), 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		self.text = wx.TextCtrl(p, -1, '', style=((((wx.HSCROLL | wx.TE_MULTILINE) | wx.TE_READONLY) | wx.TE_RICH2) | wx.TE_AUTO_URL), size=(600, 300))
		box.Add(self.text, 1, ((wx.EXPAND | wx.ALIGN_CENTRE) | wx.ALL), 5)
		sizer.Add(box, 1, ((wx.EXPAND | wx.ALIGN_CENTRE) | wx.ALL), 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(self.bReport, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		box.Add(self.bStart, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		box.Add(self.bQuit, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		sizer.Add(box, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		img = wx.Image( os.path.join( basedir, 'logo.jpg' ), wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
		b = wx.StaticBitmap(p, -1, img, size=(img.GetWidth(),img.GetHeight()))
		sizer.Add(b, 0, (wx.ALIGN_CENTRE | wx.ALL), 5)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.Bind(wx.EVT_TEXT_URL, self.getToUrl, self.text)
		self.urlString = ''
		self.urlRange = (-10, -15)
		p.SetSizer(sizer)
		sizer.Fit(p)
		sizer.Fit(self)
		self.valid = True
		if (txt == ''):
			self.bStart.Enable(False)
			self.bReport.Enable(False)
			self.auto = False
		else:
			self.auto = True
			self.bStart.Enable(False)
			self.bReport.Enable(False)
			self.bQuit.Enable(False)
			self.browse.Enable( False )
			wx.CallLater( 1000,self.OnStart, None )
		
	def getToUrl( self, event ):
		self.urlRange = (event.GetURLStart(), event.GetURLEnd())
		self.urlString = self.text.GetRange(self.urlRange[0], self.urlRange[1])
		if event.GetMouseEvent().LeftDown():
			webbrowser.open(self.urlString)
	
	def OnCloseWindow( self, event ):
		self.Destroy()
		sys.exit(1)
	
	def Log( self, what, style = None):
		pos = len(self.text.GetValue())
		self.text.AppendText(what)
		if (style is not None):
			self.text.SetStyle(pos, (self.text.GetLastPosition() - 1), style)
		wx.Yield()
		
	def OnBrowse( self, event ):
		dlg = wx.FileDialog(self, message=MsgChoose, defaultDir=os.getcwd(), defaultFile='', wildcard=MsgFileType, style=wx.OPEN)
		if (dlg.ShowModal() == wx.ID_OK):
			paths = dlg.GetPaths()
			self.fileName.SetValue(paths[0])
			self.bStart.Enable(True)
			self.bReport.Enable(True)
		dlg.Destroy()
		
	def OnReport( self, event ):
		self.bQuit.Enable(False)
		self.bStart.Enable(False)
		self.bReport.Enable(False)
		self.browse.Enable( False )
		self.text.SetValue('')
		dlg = ProcessDlg(self, MsgLocate)
		dlg.Show(True)
		dlg.Center()
		locate(self.fileName.GetValue(), dlg, self)
		dlg.Destroy()
		self.bQuit.Enable(True)
		self.bStart.Enable(True)
		self.bReport.Enable(True)
		self.browse.Enable( True )
	
	def OnStart( self, event ):
		self.browse.Enable( False )
		self.bQuit.Enable(False)
		self.bStart.Enable(False)
		self.bReport.Enable(False)
		try:
			self.text.SetValue('')
			dlg = ProcessDlg(self)
			dlg.Show(True)
			dlg.Center()
			process(self.fileName.GetValue(), dlg, self)
			dlg.Destroy()
		except:
			raise
			dlg = wx.MessageDialog(None, MsgErrorOccurs, MsgError, (wx.OK | wx.ICON_ERROR))
			dlg.ShowModal()
			dlg.Destroy()
		self.bQuit.Enable(True)
		if self.auto == False:
			self.bStart.Enable(True)
			self.bReport.Enable(True)
			self.browse.Enable( True )
	
	def OnQuit( self, event ):
		self.OnCloseWindow(event)

class SplashScreen( wx.SplashScreen ):
	def __init__(self):
		bmp = wx.Image( os.path.join( basedir, 'splash.jpg' ), wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
		wx.SplashScreen.__init__(self, bmp, (wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT), 500, None, -1)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		evt.Skip()
		self.Hide()
		self.ShowMain()

	def ShowMain(self):
		frame = MainFrame()
		frame.Show()
		frame.Center()

class App( wx.App ):
	def OnInit(self):
		splash = SplashScreen()
		splash.Show()
		return True
		

if getattr(sys, 'frozen', None):
	basedir = sys._MEIPASS
else:
	basedir = os.path.dirname(__file__)
print basedir
#os.chdir( basedir )

try:
    execfile( os.path.join( ".", 'current.lang') )
except IOError:
	print 'no current.lang in current folder, switching to runtime folder'
	try:
	    execfile( os.path.join( basedir, 'current.lang') )
	except IOError:
		pass

prog = App()
prog.MainLoop()
