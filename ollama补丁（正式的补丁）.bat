::@echo off
@echo off


xcopy "%~dp0web" "%~dp0comfyui-ollama\web" /E /I /H /K /R /Y
pause

