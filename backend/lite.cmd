@REM 解决命令行乱码的问题，其中.liteclirc是litecli的配置文件，用于设置表格格式等
@echo off
chcp 65001 >nul
uvx litecli --liteclirc "%~dp0.liteclirc" "%~dp0app.db"