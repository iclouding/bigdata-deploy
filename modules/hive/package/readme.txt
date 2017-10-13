2017-3-28:
>  project:ql
>  jar: hive-exec-2.1.1.jar
>  ql: hive-exec.jar:
1. /ql/src/java/org/apache/hadoop/hive/ql/exec/tez/TezSessionPoolManager.java
canWorkWithSameSession
增加!session.isOpen()的判断
2. org.apache.hadoop.hive.ql.io.parquet.serde.primitive.ParquetStringInspector
修改类型转换逻辑，让所有类型均可转为string

2017-4-7:
>  project:ql
>  jar: hive-exec-2.1.1.jar
>  ql: hive-exec.jar:
TezSessionState.java cleanupScratchDir
添加if(tezScratchDir==null) return;
TezSessionState.java closeClient
添加额外的catch部分，做容错保护

2017-4-22:
> hcatalog-core
增加了org.apache.hive.hcatalog.data.JsonSerDe2,使得json结构化字段都可以转化为string
增加NgxStyleStrDecoder,使得JsonSerDe2可以处理nginx编码后的日志内容

2017-5-6
>  project:hive-shims-common
>  jar: 先installhive-shims-common项目,然后package hive-exec-2.1.1.jar
HdfsUtils.java setFullFileStatus
aclEntries实例采用复制方式初始化,防止潜在的并发修改异常,并增加了去重逻辑

2017-7-12
> project:hive-serde
> jar:hive-serde-2.1.1.jar
> PrimitiveObjectInspectorConverter.java 增加AnyStringConvter类
> ObjectInspectorConverters.java: 164行增加AnyStringConvter类的入口

2017-6-8
> jar:hive-exec-2.1.1.jar
解决show create table命令注释中文乱码
修改hive的 org.apache.hadoop.hive.ql.exec.DDLTask类
outStream.writeBytes(createTab_stmt.toString());
改为
outStream.write(createTab_stmt.toString().getBytes("UTF-8"));

outStream.writeBytes(createTab_stmt.render());
改为
outStream.write(createTab_stmt.render().getBytes("UTF-8"));
编译之后替换原来的hive-exec-2.1.1.jar
参考
https://issues.apache.org/jira/browse/HIVE-11837
https://issues.apache.org/jira/secure/attachment/12791019/HIVE-11837.1.patch