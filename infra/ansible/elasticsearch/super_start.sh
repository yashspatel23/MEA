#!/bin/bash
set +e
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
FILEDIR=`pwd -P`

conf=$FILEDIR"/deploy/supervisord.conf"
pid_file=$FILEDIR"/pids/supervisord.pid"

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

