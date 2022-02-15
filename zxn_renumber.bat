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
SET FULLFILE=%~f1
SET FILENAME=%~n1
SET EXTENSION=%~x1
SET FILEDIR=%~dp1
SET ACTION=%2

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

IF [%ACTION%] == [] (
    SET ACTION=renumber
)

IF /I "%ACTION%"=="renumber" (
    ECHO Renumbering %FILENAME%.bas...
    py -3 "%MYPATH%\rennextbasic.py" -i "%FULLFILE%"
    SET RETVAL=%ERRORLEVEL%
    IF NOT %RETVAL% EQU 0 (
        ECHO Error^^!^^!^^!
        exit /b %RETVAL%
    )
)

IF /I "%ACTION%"=="format" (
    ECHO Formatting %FILENAME%.bas...
    COPY "%FULLFILE%" "%FILEDIR%\%FILENAME%.bas.bak"
    py -3 "%MYPATH%\txt2nextbasic.py" -i "%FULLFILE%" -o "%FILEDIR%\%FILENAME%.tmp.bas"
    SET RETVAL=%ERRORLEVEL%
    IF NOT %RETVAL% EQU 0 (
        ECHO Error^^!^^!^^!
        exit /b %RETVAL%
    )
    py -3 "%MYPATH%\nextbasic2txt.py" -i "%FILEDIR%\%FILENAME%.tmp.bas" -o "%FULLFILE%" -n "%FILENAME%"
    SET RETVAL=%ERRORLEVEL%
    IF NOT %RETVAL% EQU 0 (
        ECHO Error^^!^^!^^!
        exit /b %RETVAL%
    )
    DEL "%FILEDIR%\%FILENAME%.tmp.bas"
)

:End
	ECHO Done

ENDLOCAL
