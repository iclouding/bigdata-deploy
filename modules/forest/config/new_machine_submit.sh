#!/bin/bash

source ~/.bash_profile

#set -x

Params=($@)
MainClass=${Params[0]}
Length=${#Params[@]}
Args=${Params[@]:1:Length-1}

cd `dirname $0`
pwd=`pwd`


for file in ../conf/*
do
	if [ -n "$resFiles" ]; then
		resFiles="$resFiles:$file"
	else
		resFiles="$file"
    fi
done

for file in ../lib/*.jar
do
	if [ -n "$jarFiles" ]; then
		jarFiles="$jarFiles:$file"
	else
		jarFiles="$file"
	fi
done

day=`date +'%Y%m%d'`
JAVA_HOME="/usr/local/bin/java"
JarHome="../lib/Forest-1.0.0-SNAPSHOT.jar"
log_name=`echo ${MainClass}|awk -F '.' '{print $NF}'`

#set -x
nohup ${JAVA_HOME}/bin/java -XX:+UseParNewGC -XX:+UseConcMarkSweepGC -Djava.awt.headless=true -XX:CMSInitiatingOccupancyFraction=75 -XX:+UseCMSInitiatingOccupancyOnly -XX:+HeapDumpOnOutOfMemoryError -Xmx8g -Xms8g -cp ${jarFiles} ${MainClass} >/data/logs/forest-bi/${log_name}_${day}.log 2>&1 &