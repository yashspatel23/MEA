#!/bin/bash
set +e
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
FILEDIR=`pwd -P`

conf=$FILEDIR"/deploy/supervisord.conf"
pid_file=$FILEDIR"/pids/supervisord.pid"

# stop programs
echo ${green}"stopping all programs ..."${reset}
supervisorctl -c $conf stop all


# stop supervisord
if [[ -e $pid_file ]]
then
    echo ${green}"killing supervisord: "`cat $pid_file`${reset}
    kill -9 `cat $pid_file`
    rm $pid_file
else
    echo ${green}"No running supervisord."${reset}
fi

