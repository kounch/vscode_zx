#/bin/sh

#    Copyright (c) 2020-2022 @Kounch
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


mypath=`dirname "$0"`
mode=$1
action=$2
fullfile=$3
filename=$(basename "$fullfile")
extension="${filename##*.}"
filename="${filename%.*}"
filedir=`dirname "$fullfile"`

python3bin=python3

if [ -x "$(command -v gettext)" ]; then
    . gettext.sh
    export TEXTDOMAIN=zxb_build.sh
    export TEXTDOMAINDIR=$mypath/locale
else
    shopt -s expand_aliases
    alias gettext='echo'
    alias eval_gettext='eval echo'
fi

shopt -s nocasematch
if [[ $extension != "bas" ]]; then
    echo $(gettext "ERROR: Not a .bas file")
    exit 1
fi
shopt -u nocasematch

if [ ! -f "$fullfile" ]; then
    echo $(eval_gettext "ERROR: \$fullfile Not Found")
    exit 2
fi

"$python3bin" -V >/dev/null 2>&1
retval=$?
if [ $retval != 0 ]; then
    echo $(gettext "ERROR: Python3 Not found")
    exit $retVal
fi

if [[ $mode == "zxbasic" ]]; then
    echo $(eval_gettext "Compiling \$filename")
    mkdir -p "$filedir/build"
    "$python3bin" "$mypath/zxbasic/zxb.py" -O 2 "$fullfile" -o "$filedir/build/$filename.bin"
    retval=$?
    if [ $retval != 0 ]; then
        echo $(gettext "Error while compiling")
        exit $retVal
    fi
    
    echo $(gettext "Creating Launcher")
    "$python3bin" "$mypath/txt2nextbasic.py" -n "$filename.bin" -o "$filedir/build/$filename.bas"
    retval=$?
    if [ $retval != 0 ]; then
        echo $(gettext "Error while creating launcher")
        exit $retVal
    fi
fi

if [[ $mode == "nextbasic" ]]; then
    echo $(eval_gettext "Converting \$filename")
    mkdir -p "$filedir/build"
    "$python3bin" "$mypath/txt2nextbasic.py" -i "$fullfile" -o "$filedir/build/$filename.bas"
    retval=$?
    if [ $retval != 0 ]; then
        echo $(gettext "Error while converting")
        exit $retVal
    fi
fi

shopt -s nocasematch
if [[ $action == "runCspect" ]]; then
    imagepath=$mypath/CSpect/systemnext.img
fi
shopt -u nocasematch

shopt -s nocasematch
if [[ $action == "runZEsarUX" ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        imagepath="$mypath/ZEsarUX.app/Contents/Resources/tbblue.mmc"
    else
        imagepath="$mypath/ZEsarUX/tbblue.mmc"
    fi
fi
shopt -u nocasematch

shopt -s nocasematch
if [[ $action == "runCspect" ]] || [[ $action == "runZEsarUX" ]]; then
    echo $(gettext "Copying files")
    "$mypath/hdfmonkey" put "$imagepath" "$filedir/build/$filename.bas" /devel/test.bas
    retval=$?
    if [ $retval -ne 0 ]; then
        echo $(eval_gettext "Copy Error (\$filename.bas)")
        exit $retVal
    fi
    
    if [[ $mode == "zxbasic" ]]; then
        "$mypath/hdfmonkey" put "$imagepath" "$filedir/build/$filename.bin" /devel/
        retval=$?
        if [ $retval -ne 0 ]; then
            echo $(eval_gettext "Copy Error (\$filename.bin)")
            exit $retVal
        fi
    fi
    
    if [[ -f "$filedir/$filename.filelist" ]]; then
        while read line; do
            "$mypath/hdfmonkey" put "$imagepath" "$filedir/${line%$'\r'}" /devel/
            retval=$?
            if [ $retval -ne 0 ]; then
                echo $(eval_gettext "Copy Error (\$line)")
                exit $retVal
            fi
        done < "$filedir/$filename.filelist"
    fi
fi
shopt -u nocasematch

shopt -s nocasematch
if [[ $action == "runCspect" ]]; then
    echo $(gettext "Running Cspect")
    cd "$mypath/CSpect"
    mono CSpect.exe -w2 -vsync -s28 -esc -60 -tv -basickeys -zxnext -nextrom -mmc=./systemnext.img
    retval=$?
    if [ $retval -ne 0 ]; then
        echo $(gettext "Emulator Error")
        exit $retVal
    fi
fi
shopt -u nocasematch

shopt -s nocasematch
if [[ $action == "runZEsarUX" ]]; then
    echo $(gettext "Running ZEsarUX")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        cd "$mypath/ZEsarUX.app/Contents/MacOS"
    else
        cd "$mypath/ZEsarUX"
    fi
    ./zesarux --configfile "$mypath/zesaruxrc"
    retval=$?
    if [ $retval -ne 0 ]; then
        echo $(gettext "Emulator Error")
        exit $retVal
    fi
fi
shopt -u nocasematch

echo $(gettext "Finished")
exit 0
