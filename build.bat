@echo off
if exist dist (
    rm -rf dist
) 
pyinstaller dungeon.spec && rm -rf build && xcopy .\assets\ .\dist\dungeon\assets /E /H /C /I
pause