#!/bin/bash
NOW=$(date +"%m-%d-%Y-%H-%M-%s" )
FILES="/tmp/process_list.$NOW"
ps -ef > $FILES