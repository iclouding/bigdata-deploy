main_class="org.elasticsearch.bootstrap.Elasticsearch"
pid=$(ps -ef |grep ${main_class} |grep -v grep |awk '{print $2}')
echo "pid is ${pid}"
if [ "${pid}" ]; then
    echo "stopping..."
    kill ${pid}
    exit 0
fi