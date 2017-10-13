#日志流并行期过渡版本

需要保留已经使用的部分nginx日志记录方式,以及所有反向代理到logcenter的日志
实现方案上采用了子请求, nginx日志发送一次子请求到/log/${appId}接口, logcenter日志则一次发送2次子请求,分别到logcenter和/log/${appId}