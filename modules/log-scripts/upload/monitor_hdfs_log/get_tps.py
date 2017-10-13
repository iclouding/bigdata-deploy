# -*- coding: utf-8 -*-
import commands

cmd = "iostat -dm vdb 2 5|tail -2"
output = commands.getoutput(cmd)
print output.split()[1]
