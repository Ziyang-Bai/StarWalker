@echo on
::打包的主文件
set MainFilePY=arageko.py

::--target-dir 打包后的程序路径
set TargetDir="C:\Users\Danie\Documents\GitHub\StarWalker\starwalker\build"

::--target-name 打包后的程序名
set TargetName="arageko.exe"

::--include-modules 要包含的模块或库
set IncludeModl="math skyfield"

::--icon 打包后的程序图标
set Icon="C:\Users\Danie\Documents\GitHub\StarWalker\starwalker\lib\image\starwalker-icon.ico"

cxfreeze %MainFilePY%  --target-name=%TargetName%  --icon=%Icon%

pause
