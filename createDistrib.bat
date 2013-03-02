d:\python27\python.exe -OO ..\pyinstaller\pyinstaller.py -n "BSC Cleanitol TM" -F	 -w --upx-dir=..\..\upx308w "BSC Cleanitol TM.spec"
d:\python27\python.exe -OO ..\pyinstaller\pyinstaller.py -n "BSC Cleanitol TM Debug" -F -c --upx-dir=..\..\upx308w "BSC Cleanitol TM Debug.spec"
rem copy splash.jpg "dist\BSC Cleanitol TM"
rem copy logo.jpg "dist\BSC Cleanitol TM"
copy *.lang "dist\"
rem copy *.ico "dist\BSC Cleanitol TM"
copy cleanupList.txt dist