#!/bin/bash
set -e
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
FILEDIR=`pwd -P`

bin_dir="bin"
lib_dir="lib"
data_dir="data"
fetch_dir="fetch"
run_dir="run"

mkdir -p $fetch_dir
mkdir -p $run_dir/pids
mkdir -p $run_dir/logs

# -----------------
# elasticsearch
# -----------------
es_folder_name="elasticsearch-5.5.1"
es_zip_file_name=$es_folder_name".zip"

# download
if [[ ! -e $fetch_dir/$es_zip_file_name ]]
then
    curl -o $fetch_dir/$es_zip_file_name -O https://artifacts.elastic.co/downloads/elasticsearch/$es_zip_file_name
else
    echo $es_zip_file_name" is already cahced in folder ./fetch "
fi

# unzip
unzip -q -o $fetch_dir/$es_zip_file_name -d $data_dir
rm -rf $data_dir/elasticsearch
mv $data_dir/$es_folder_name $data_dir/elasticsearch

# -----------------
# kibana
# -----------------
kibana_folder_name="kibana-5.5.1-darwin-x86_64"
kibana_zip_file_name=$kibana_folder_name".tar.gz"

# download
if [[ ! -e $fetch_dir/$kibana_zip_file_name ]]
then
    curl -o $fetch_dir/$kibana_zip_file_name -O https://artifacts.elastic.co/downloads/kibana/$kibana_zip_file_name
else
    echo $kibana_zip_file_name" is already cahced in folder ./fetch "
fi

# unzip
tar -xzf $fetch_dir/$kibana_zip_file_name
rm -rf $data_dir/kibana
mv $kibana_folder_name $data_dir/kibana

# # plugins
# $base_path/elasticsearch/bin/plugin install mobz/elasticsearch-head
# $base_path/elasticsearch/bin/plugin install cloud-aws
# $base_path/elasticsearch/bin/plugin install delete-by-query

# PUT _template/custom_monitor
# {
#     "template": ".monitor*",
#     "order": 1,
#     "settings": {
#       "number_of_shards": 1,
# 	"number_of_replicas": 0
#     }
# }
# DELETE .monitor*

