#/bin/sh

#    Copyright (c) 2020 @Kounch
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
fullfile=$1
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

echo $(eval_gettext "Converting bin \$filename to BAS txt..")
mkdir -p "$filedir/tests"
"$python3bin" "$mypath/nextbasic2txt.py" -i "$fullfile" -o "$filedir/tests/${filename}_txt_orig.bas"
retval=$?
if [ $retval != 0 ]; then
    echo $(gettext "Error while converting")
    exit $retVal
fi

echo $(eval_gettext "Converting BAS txt...")
mkdir -p "$filedir/build"
"$python3bin" "$mypath/txt2nextbasic.py" -i "$filedir/tests/${filename}_txt_orig.bas" -o "$filedir/tests/${filename}_bin.bas"
retval=$?
if [ $retval != 0 ]; then
    echo $(gettext "Error while converting")
    exit $retVal
fi

echo $(eval_gettext "Converting new bin to BAS txt..")
mkdir -p "$filedir/tests"
"$python3bin" "$mypath/nextbasic2txt.py" -i "$filedir/tests/${filename}_bin.bas" -o "$filedir/tests/${filename}_txt.bas"
retval=$?
if [ $retval != 0 ]; then
    echo $(gettext "Error while converting")
    exit $retVal
fi

echo $(eval_gettext "Comparing TXT files..")

# echo "$filedir/tests/${filename}_txt_orig.bas vs $filedir/tests/${filename}_txt.bas"
diff  "$filedir/tests/${filename}_txt_orig.bas" "$filedir/tests/${filename}_txt.bas"
