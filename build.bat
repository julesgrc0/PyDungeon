@echo off
if exist dist (
    rm -rf dist
) 
pyinstaller demo.spec && rm -rf build && xcopy .\assets\ .\dist\demo\assets /E /H /C /I
pause