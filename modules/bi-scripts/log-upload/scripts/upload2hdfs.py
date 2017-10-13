# -*- coding: utf-8 -*-
import logging
import commands
import os
import json
import requests
import arrow
import upload2hdfs_config
import re
import pdb
from collections import defaultdict


def log_msg(fun_name, err_msg, level):
	message = fun_name + ':' + err_msg
	logger = logging.getLogger()
	logname = upload2hdfs_config.logs
	hdlr = logging.FileHandler(logname)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.NOTSET)
	logger.log(level, message)
	hdlr.flush()
	logger.removeHandler(hdlr)


def send_alter_mail(sub, body):
	mail_content = dict()
	mail_content["sub"] = sub
	mail_content["content"] = body
	mail_content["sendto"] = upload2hdfs_config.sendto
	mail_url = 'http://10.19.15.127:5006/mail/api/v1.0/send'
	
	heads = {'content-type': 'application/json'}
	r = requests.post(url = mail_url, headers = heads, data = json.dumps(mail_content))
	if r.status_code == 200:
		log_msg("send_alter_mail", "send mail success", 1)
	else:
		err_msg = "send mail failed ,output was %s" % r.content
		log_msg("send_alter_mail", err_msg, 2)


def run_cmd(cmd):
	dry_run = upload2hdfs_config.debug
	if dry_run:
		status = 0
	else:
		(status, output) = commands.getstatusoutput(cmd)
	#status=0
	if status == 0:
		log_msg("run_cmd", "run %s success!" % cmd, 1)
		return True
	else:
		msg = "run %s Failed,output was %s " % (cmd, output)
		log_msg("run_cmd", msg, 2)


class GetLocalFilesInfo():
	def __init__(self, path):
		self.localpath = path
		self.hours = upload2hdfs_config.hours
		self.filename_match = upload2hdfs_config.filename_match
		self.hdfs_change = upload2hdfs_config.hdfs_change
	
	def _match_files_rule(self, filename):
		is_found = False
		#pdb.set_trace()
		for matchRule in self.filename_match.split(','):
			file_match = re.search(matchRule, filename)
			if file_match:
				is_found = True
		return is_found
	
	def _check_file_time(self, filename):
		import re
		pattern="log\.(\w+)\.(\d{4}-\d{2}-\d{2}-\d{2})_"
		# filename like  log.helios.2017-09-06-09_bigdata-extsvr-log2_2.log
		match_values=re.match(pattern, filename)
		file_time=match_values.group(2)
		#file_time = filename.split('.')[2].split('_')[0]
		if file_time in self._str_time():
			return True
	
	def _str_time(self):
		utc = arrow.utcnow().to('Asia/Shanghai')
		str_time = list()
		for i in range(self.hours):
			str_time.append(utc.shift(hours = -i).format("YYYY-MM-DD-HH"))
		return str_time
	
	def _replace_hdfs_rule(self, values):
		for item in self.hdfs_change.keys():
			if values == item:
				values = self.hdfs_change[item]
		return values
	
	def _get_hdfs_path_by_local_filename(self, filename):
		project = filename.split('.')[1]
		file_time = filename.split('.')[2]
		hdfs_time = file_time.split('_')[0].replace('-', '')[0:8]
		new_projec = self._replace_hdfs_rule(project)
		hdfs_path = "/log/%s/rawlog/%s" % (new_projec, hdfs_time)
		return hdfs_path
	
	def get_local_files(self):
		# 取得Local下所有文件
		file_no_comp_with_hdfs = dict()
		files = os.listdir(self.localpath)
		for file_one in files:
			if os.path.isfile(os.path.join(self.localpath, file_one)):
				# 按关键词过滤本地文件列表
				if self._match_files_rule(file_one):
					# 按时间过滤需上传的文件列表
					if self._check_file_time(file_one):
						# 计算文件对应的HDFS路径
						file_no_comp_with_hdfs[file_one] = os.path.getsize(os.path.join(self.localpath, file_one))
						#print file_no_comp_with_hdfs
		
		# 为了减少HDFS交互IO，一次性进行本地与HDFS文件比对
		if file_no_comp_with_hdfs:
			hdfs_path_check_list = list()
			hdfs_path_check_list_duplicate = list()
			for filename in file_no_comp_with_hdfs:
				hdfs_path_check_list.append(self._get_hdfs_path_by_local_filename(filename))
				# 列表去重
			hdfs_path_check_list_duplicate = list(set(hdfs_path_check_list))
			# 比对本地文件及HDFS信息
			my_hdfs = CheckLocalHdfs(self.localpath, file_no_comp_with_hdfs, hdfs_path_check_list_duplicate)
			local_file_need_uploads = my_hdfs.check_local_file_need_upload()
			
			# 计算本地文件与HDFS对应关系
			local_file_need_uploads_hdfs_dict = dict()
			for local_file_need_uploads_one in local_file_need_uploads:
				local_file_need_uploads_hdfs_dict[local_file_need_uploads_one] = self._get_hdfs_path_by_local_filename(
					local_file_need_uploads_one)
			return local_file_need_uploads_hdfs_dict
		else:
			return None


class CheckLocalHdfs():
	def __init__(self, local_path, local_file_list,hdfs_path):
		self.local_file_list = local_file_list
		self.local_path = local_path
		self.hdfs_path = hdfs_path
		self.hdfs_info = self._get_hdfs_file_list()
		print "Hdfs info:"
		print self.hdfs_info
		self.local_info = self.get_local_file_list()
		print "Local info:"
		print self.local_info

	
	def get_local_file_list(self):
		file_local_info = dict()
		#files = os.listdir(self.local_path)
		for file_one in self.local_file_list:
			if os.path.isfile(os.path.join(self.local_path, file_one)):
				file_local_info[file_one] = os.path.getsize(os.path.join(self.local_path, file_one))
		# 返回指定本地目录下的文件及大小
		return file_local_info
	
	def check_local_file_need_upload(self):
		file_need_upload_list = list()
		for filename in self.local_info.keys():
			# 如果本地文件不在Hdfs
			if filename not in self.hdfs_info.keys():
				file_need_upload_list.append(filename)
			#如果本地文件为0，则不处理，报警
			if int(self.local_info[filename])==0:
				alter_local_msg="本地文件{filename} 大小为0 ，请人工介入！".format(filename=filename)
				log_msg("check_local_file_need_uload", alter_local_msg, 2)
				sub = "本地文件大小为0"
				send_alter_mail(sub = sub, body = alter_local_msg)

			# 如果本地文件大小与HDFS不符，且HDFS文件>0,暂不处理，提交报警邮件
			if int(self.local_info[filename]) != int(self.hdfs_info.get(filename, 0)) and int(self.hdfs_info.get(filename, 0)) > 0:
				alter_msg = "文件检查阶段：文件{filename}本地与HDFS不符: Local {localsize} HDFS {hdfssize}".format(
					filename = os.path.join(self.local_path, filename), localsize = str(self.local_info[filename]),
					hdfssize = str(self.hdfs_info[filename]))
				
				log_msg("check_local_file_need_uload", alter_msg, 2)
				sub = "文件检查阶段：本地文件与HDFS大小不一致"
				send_alter_mail(sub = sub, body = alter_msg)
		return file_need_upload_list
	
	def check_local_files_in_hdfs(self):
		no_found = list()
		diff_size = dict()
		for filename in self.local_info.keys():
			if filename not in self.hdfs_info.keys():
				no_found.append(filename)
				if int(self.local_info.get(filename, 0)) != int(self.hdfs_info.get(filename, 0)):
					values = (self.local_info.get(filename, 0), self.hdfs_info.get(filename, 0))
					diff_size[filename] = values
		return no_found, diff_size
	
	def _get_hdfs_file_list(self):
		file_hdfs_info = dict()
		for hdfs_one in self.hdfs_path:
			# mkdir_hdfs_path = "su - spark -c 'hadoop fs -mkdir -p %s'" % hdfs_one
			# run_cmd(mkdir_hdfs_path)
			cmd = "su - spark -c 'hadoop fs -ls %s'" % hdfs_one
			(status, output) = commands.getstatusoutput(cmd)
			if status == 0 and len(output.split('\n')) >1:
				for line in output.split('\n'):
					if line[0] == '-':
						file_hdfs_info[line.split()[7].split('/')[-1]] = line.split()[4]
			else:
				msg = "get %s from hadoop failed ,output was %s" % (self.hdfs_path, output)
				log_msg("_get_hdfs_file_list", msg, 2)
			
		return file_hdfs_info


class Up2Hdfs(object):
	def __init__(self, local_path, hdfs_info):
		self.local_path = local_path
		self.hdfs_info = hdfs_info
	
	def up2_hdfs(self):
		# todo 按HDFS路径做聚合上传
		poly_hdfs_info = defaultdict(list)
		
		for items in self.hdfs_info.items():
			poly_hdfs_info[items[1]].append(items[0])
			
		for hdfs_path in poly_hdfs_info.keys():
			mkdir_hdfs_dir = "su - spark -c'hadoop fs -mkdir -p %s'" % hdfs_path
			run_cmd(mkdir_hdfs_dir)
			
			upload_files = " ".join(poly_hdfs_info[hdfs_path])
			print "开始上传文件:%s" % upload_files
			up2_hdfs_cmd = "su - spark -c'cd %s && hadoop fs -put %s %s'" % (self.local_path,upload_files,hdfs_path)
			run_cmd(up2_hdfs_cmd)
			
		# 检查上传文件
		check_upload = CheckLocalHdfs(self.local_path, self.hdfs_info.keys(), poly_hdfs_info.keys())
		(no_found, diff_size) = check_upload.check_local_files_in_hdfs()
		if diff_size.keys():
			print "文件上传后发现不同大小的文件,数量%s "%str(len(diff_size.keys()))
			size_diff_msg = ""
			for item in diff_size.keys():
				size_diff_msg += "File {filename} size diff : Local {localsize} ,Hdfs {hdfsize} \n ".format(
					filename = item, localsize = diff_size[item][0], hdfsize = diff_size[item][1])
			log_msg("check_local_files_in_hdfs_diffSize", size_diff_msg, 2)
			send_alter_mail(sub = '文件上传后检查阶段:本地&HDFS 文件大小不同', body = size_diff_msg)
			return False
		if no_found:
			print "文件上传后发现HDFS未找到文件：数量%s"%str(len(no_found))
			no_found_msg = ""
			for item in no_found:
				no_found_msg += "local file %s not in Hdfs \n" % item
			log_msg("check_local_files_in_hdfs_nofound", no_found_msg, 2)
			send_alter_mail(sub='文件上传后检查阶段:HDFS 文件未找到', body = no_found_msg)
			return False
		return True

		
def up_workflow(local_path):
	my_local = GetLocalFilesInfo(local_path)
	local_file_need_uploads_hdfs_dict = my_local.get_local_files()
	if local_file_need_uploads_hdfs_dict:
		print "需要上传文件%s" % str(len(local_file_need_uploads_hdfs_dict))
		my_upload_hdfs = Up2Hdfs(local_path, local_file_need_uploads_hdfs_dict)
		if my_upload_hdfs.up2_hdfs():
			return True
		else:
			return False
	else:
		print "没有文件需要上传"
		log_msg("workflow", "检查本地路径%s，无文件需要上传"%local_path,1)
		return True
	

def main():
	retry = int(upload2hdfs_config.retry)
	i = 1
	for local_path in upload2hdfs_config.paths:
		while i <= retry:
			if up_workflow(local_path):
				print "本地路径%s 检查，上传完成！"%local_path
				log_msg("main", "日志上传操作，本地路径%s执行完成"%local_path, 1)
				break
			else:
				print "本地路径%s 重传！" % local_path
				i += 1
	print "检查完成"
	log_msg("main", "日志上传操作执行完成", 1)
if __name__ == "__main__":
	main()
