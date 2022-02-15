@ECHO OFF
SETLOCAL EnableDelayedExpansion

::    Copyright (c) 2020-2022 @Kounch
::
::    This program is free software: you can redistribute it and/or modify
::    it under the terms of the GNU General Public License as published by
::    the Free Software Foundation, either version 3 of the License, or
::    (at your option) any later version.
::
::    This program is distributed in the hope that it will be useful,
::    but WITHOUT ANY WARRANTY; without even the implied warranty of
::    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
::    GNU General Public License for more details.
::
::    You should have received a copy of the GNU General Public License
::    along with this program.  If not, see <https://www.gnu.org/licenses/>.

SET MYPATH=%~dp0
SET MYDRIVE=%~d0
SET MODE=%1
SET ACTION=%2
SET FULLFILE=%~f3
SET FILENAME=%~n3
SET EXTENSION=%~x3
SET FILEDIR=%~dp3

IF /I NOT "%EXTENSION%"==".bas" (
    ECHO ERROR^^!^^! Not a .bas file^^!^^!^^!
    exit /b 1
)

IF NOT EXIST "%FULLFILE%" (
    ECHO ERROR^^!^^! "%2" Does not exist^^!^^!^^!
    exit /b 2
)

py -3 -V >nul 2>&1
SET RETVAL=%ERRORLEVEL%
IF NOT %RETVAL% EQU 0 (
    ECHO ERROR^^!^^! Python 3 not found^^!^^!^^!
    exit /b %RETVAL%
)

IF /I "%MODE%"=="zxbasic" (
	ECHO Compiling %FILENAME%.bas...
	mkdir "%FILEDIR%\build" 2>NUL
	py -3 "%MYPATH%\zxbasic\zxb.py" -O 2 "%FULLFILE%" -o "%FILEDIR%\build\%FILENAME%.bin"
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Compilation Error^^!^^!^^!
		exit /b %RETVAL%
	)

	ECHO Creating Launcher...
	py -3 "%MYPATH%\txt2nextbasic.py" -n "%FILENAME%.bin" -o "%FILEDIR%\build\%FILENAME%.bas"
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Launcher Creation Error^^!^^!^^!
		exit /b %RETVAL%
	)
)

IF /I "%MODE%"=="nextbasic" (
	ECHO Converting %FILENAME%.bas...
	mkdir "%FILEDIR%\build" 2>NUL
	py -3 "%MYPATH%\txt2nextbasic.py" -i "%FULLFILE%" -o "%FILEDIR%\build\%FILENAME%.bas"
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Conversion Error^^!^^!^^!
		exit /b %RETVAL%
	)
)

IF /I "%ACTION%"=="runCspect" (
	SET IMAGEPATH=%MYPATH%\CSpect\systemnext.img
	GOTO CopyFiles 
)
IF /I "%ACTION%"=="runZEsarUX" (
	SET IMAGEPATH=%MYPATH%\ZEsarUX\tbblue.mmc
	GOTO CopyFiles 
)
GOTO End

IF /I "%ACTION%"=="runCspect" (

:CopyFiles
	ECHO Copying files...
	"%MYPATH%\hdfmonkey.exe" put "%IMAGEPATH%" "%FILEDIR%\build\%FILENAME%.bas" /devel/test.bas
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Copy Error^^!^^!^^! "(%FILENAME%.bin)"
		exit /b %RETVAL%
	)

	IF /I "%MODE%"=="zxbasic" (
		"%MYPATH%\hdfmonkey.exe" put "%IMAGEPATH%" "%FILEDIR%\build\%FILENAME%.bin" /devel/
		SET RETVAL=%ERRORLEVEL%
		IF NOT %RETVAL% EQU 0 (
			ECHO Copy Error^^!^^!^^! "(%FILENAME%.bin)"
			exit /b %RETVAL%
		)
	)


	IF EXIST "%FILEDIR%%FILENAME%.filelist" (
		FOR /f "tokens=*" %%F IN (%FILEDIR%%FILENAME%.filelist) DO (
			"%MYPATH%\hdfmonkey.exe" put "%IMAGEPATH%" "%FILEDIR%\%%F" /devel/
			SET RETVAL=%ERRORLEVEL%
			IF NOT %RETVAL% EQU 0 (
				ECHO Copy Error^^!^^!^^! "(%%F)"
				exit /b %RETVAL%
			)
		)
	)

IF /I "%ACTION%"=="runCspect" (
	ECHO Running Cspect...
	%MYDRIVE%
	cd "%MYPATH%\CSpect"
	CSpect.exe -w2 -vsync -s28 -esc -60 -tv -basickeys -zxnext -nextrom -mmc=.\systemnext.img
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Emulator Error^^!^^!^^!
		exit /b %RETVAL%
	)
)

IF /I "%ACTION%"=="runZEsarUX" (
	ECHO Running ZEsarUX...
	%MYDRIVE%
	cd "%MYPATH%\ZEsarUX"
	ZEsarUX.exe --configfile "%MYPATH%\zesaruxwinrc"
	SET RETVAL=%ERRORLEVEL%
	IF NOT %RETVAL% EQU 0 (
		ECHO Emulator Error^^!^^!^^!
		exit /b %RETVAL%
	)
)

:End
	ECHO Done

ENDLOCAL
