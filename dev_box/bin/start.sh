#!/bin/bash
set +e
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
FILEDIR=`pwd -P`


conf=$FILEDIR"/lib/supervisord.conf"
app_script=$FILEDIR"/lib/app.py"
pid_file=$FILEDIR"/run/pids/supervisord.pid"


# TODO: @jin Use python script to modify or template supervisord config file
# setup
$app_script

# supervisord config
echo "Using configuration: "$conf
echo ${green}'------------------------------------------'${reset}
cat $conf
echo ${green}'------------------------------------------'${reset}

# run supervisord
if [[ -e $pid_file ]]
then
    echo ${red}'Supervisord is already running.'${reset}
else
    echo ${green}'Starting supervisord.'${reset}
    echo ${green}'---------------------'${reset}
    supervisord -c $conf
fi

