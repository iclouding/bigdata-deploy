# -*- coding: utf-8 -*-

# sendto = "peng.tao@whaley.cn"
sendto = "lian.kai@whaley.cn,peng.tao@whaley.cn,wang.baozhi@whaley.cn"
logs = "/data/logs/monitor_hdfs_log/monitor_hdfs_log.log"
hours = 4

rule1_file_pattern = "/log/{rule1_project_keys}/rawlog/{rule_date_str1}/log.{rule1_project_values}.{rule_date_str2}_{hostname}_{rule1_index}.log"
rule2_file_pattern = "/log/{appids_values}/rawlog/{rule_date_str1}/{appids_keys}.log-{rule_date_str3}-{hostname}"
rule3_file_pattern = "/data_warehouse/ods_origin.db/log_raw/key_day={rule_date_str1}/key_hour={rule_date_str4}/{appids_keys}.log-{rule_date_str3}-{hostname}"

rule1_index = (1, 2, 3, 4)
rule1_project = {"whaley": "helios", "medusa": "medusa", "eagle": "eagle"}

# # rule_hostname = ("bigdata-extsvr-log1", "bigdata-extsvr-log2", "bigdata-extsvr-log3", "bigdata-extsvr-log4", "bigdata-extsvr-log5","bigdata-extsvr-log6", "bigdata-extsvr-log7")
# rule_hostname = ("bigdata-extsvr-log3", "bigdata-extsvr-log7")
rule_hostname = (
    "bigdata-extsvr-log1", "bigdata-extsvr-log2", "bigdata-extsvr-log3", "bigdata-extsvr-log4", "bigdata-extsvr-log5",
    "bigdata-extsvr-log6", "bigdata-extsvr-log7", "bigdata-extsvr-log01", "bigdata-extsvr-log02",
    "bigdata-extsvr-log03", "bigdata-extsvr-log04", "bigdata-extsvr-log05", "bigdata-extsvr-log06",
    "bigdata-extsvr-log07", "bigdata-extsvr-log08", "bigdata-extsvr-log09", "bigdata-extsvr-log10",
    "bigdata-extsvr-log11", "bigdata-extsvr-log12","bigdata-extsvr-log13","bigdata-extsvr-log14")
rule_date_str1 = "yyyyMMdd"
rule_date_str2 = "yyyy-MM-dd-HH"
rule_date_str3 = "yyyyMMddHH"
rule_date_str4 = "HH"
appids = {"boikgpokn78sb95kjhfrendoj8ilnoi7": "boikgpokn78sb95kjhfrendoj8ilnoi7",
          "boikgpokn78sb95k0000000000000000": "boikgpokn78sb95k0000000000000000",
          "boikgpokn78sb95kjhfrendoepkseljn": "boikgpokn78sb95kjhfrendoepkseljn",
          "boikgpokn78sb95ktmsc1bnkechpgj9l": "boikgpokn78sb95ktmsc1bnkechpgj9l",
          "boikgpokn78sb95kjhfrendo8dc5mlsr": "boikgpokn78sb95kjhfrendo8dc5mlsr",
          "boikgpokn78sb95kjhfrendojtihcg26": "boikgpokn78sb95kjhfrendojtihcg26"}

white_list_pattern = ("boikgpokn78sb95kjhfrendobgjgjolq.log-(\d{8}0[1-6])-([\w\-]+)",
                      "boikgpokn78sb95kjhfrendoepkseljn.log-(\d{8}0[1-6])-([\w\-]+)")
