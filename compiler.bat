@echo off
cd C:\Users\%username%\Documents\GitHub\PyPackager

python main.py "C:\Users\%username%\Documents\GitHub\Infinite-Parkour-datapack-updater\packupdater.py" -tk -nc -i="C:\Users\%username%\Documents\GitHub\Infinite-Parkour-datapack-updater\pack.ico"

python main.py "C:\Users\%username%\Documents\GitHub\Infinite-Parkour-datapack-updater\updaterinstaller.py" -tk -nc -i="C:\Users\%username%\Documents\GitHub\Infinite-Parkour-datapack-updater\pack.ico"