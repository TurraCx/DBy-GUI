pyinstaller -F -i=dby.ico test.py
copy dist\test.exe .\
rename test.exe DanishBytes.exe
rmdir dist /q /s
rmdir build /q /s
rmdir __pycache__ /q /s
del app.spec