#!/usr/bin/env bash

pid_info=`su - yarn -c 'jps|grep NodeManager|grep -v "grep"|awk "{print \$1}"'`
echo "pid_info is ${pid_info}"
node_manager_pid=`echo "${pid_info}"|awk '{print \$1}'`
echo "node_manager_pid is ${node_manager_pid}"
echo "${node_manager_pid}" >> /sys/fs/cgroup/cpu/hadoop-yarn/tasks