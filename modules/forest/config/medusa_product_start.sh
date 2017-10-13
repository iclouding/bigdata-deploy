#!/usr/bin/env bash

current_bin_path="`dirname "$0"`"
cd ${current_bin_path}
echo "current_bin_path is ${current_bin_path}"

main_class="cn.whaley.turbo.forest.main.MedusaLogProcessingNewApp2"
echo "main_class is ${main_class}"
pid=$(ps -ef |grep ${main_class} |grep -v grep |awk '{print $2}')
echo "pid is ${pid}"

if [ -z "${pid}" ]; then
    echo "pid is empty,start app directly...."
    ${current_bin_path}/new_machine_submit.sh ${main_class}
    exit 0
else
    echo "${main_class} is exist,no need to start."
fi