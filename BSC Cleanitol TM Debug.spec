# -*- mode: python -*-
def Datafiles(*filenames, **kw):
    import os
    
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))
datas = Datafiles( "Cleanitol.ico","splash.jpg","current.lang","logo.jpg")

a = Analysis(['BSC Cleanitol TM.py'],
             pathex=['D:\\Dev\\PythonDev\\Cleanitol'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          datas,
          name=os.path.join('dist', 'BSC Cleanitol TM Debug.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
