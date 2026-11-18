@echo off
setlocal
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\Nautic_app") do set "ORIG=%%~fI"

echo ============================================
echo   NAUTIC - MODO DEMO - sin base de datos
echo ============================================

REM ================= BACKEND =================
cd /d "%ROOT%BackEnd"
if errorlevel 1 goto :error

if exist "venv\Scripts\python.exe" goto :venv_ok
if not exist "%ORIG%\BackEnd\venv\Scripts\python.exe" goto :venv_create
echo [1/4] Copiando el entorno virtual desde la carpeta original - solo lectura...
robocopy "%ORIG%\BackEnd\venv" "%ROOT%BackEnd\venv" /E /NFL /NDL /NJH /NJS /NP >nul
:venv_create
if exist "venv\Scripts\python.exe" goto :venv_ok
echo [1/4] Creando entorno virtual...
py -m venv venv
if errorlevel 1 goto :error
:venv_ok

venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, itsdangerous, dotenv, requests, arrow" 2>nul
if not errorlevel 1 goto :deps_ok
echo [1/4] Instalando dependencias del backend - requiere internet...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
:deps_ok

echo [2/4] Cargando datos de muestra: spots, clima y puntajes...
venv\Scripts\python.exe -W ignore -m app.demo.seed_demo
if errorlevel 1 goto :error

echo [3/4] Levantando el backend en http://localhost:8000 ...
start "Nautic Backend DEMO" /D "%ROOT%BackEnd" cmd /k venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

REM ================= FRONTEND =================
cd /d "%ROOT%FrontEnd"
if errorlevel 1 goto :error

if exist "node_modules" goto :nm_ok
if not exist "%ORIG%\FrontEnd\node_modules" goto :nm_install
echo [4/4] Copiando node_modules desde la carpeta original - solo lectura...
robocopy "%ORIG%\FrontEnd\node_modules" "%ROOT%FrontEnd\node_modules" /E /NFL /NDL /NJH /NJS /NP >nul
if exist "node_modules" goto :nm_ok
:nm_install
echo [4/4] Instalando dependencias del frontend - requiere internet...
call npm install
if errorlevel 1 goto :error
:nm_ok

echo [4/4] Levantando el frontend en http://localhost:5173 ...
start "Nautic Frontend DEMO" /D "%ROOT%FrontEnd" cmd /k npm run dev

timeout /t 8 >nul
start "" http://localhost:5173

echo.
echo ============================================
echo   Listo. Se abrieron dos ventanas: Backend y
echo   Frontend. No las cierres durante la defensa.
echo ============================================
pause
exit /b 0

:error
echo.
echo *** Hubo un error. Revisa el mensaje de arriba. ***
pause
exit /b 1
