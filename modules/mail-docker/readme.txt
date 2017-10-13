此项目包括运行与docker中的邮件服务的部署包及其部署脚本

0、首先安装docker:
    version: 1.12.5

1、登录docker hub:
    docker login -u whaleybigdata -p whaley888
2、取镜像
    docker pull whaleybigdata/warningemail
3、运行
    docker run --name warningMailBigdata -d -p 20260:8080 -i -t whaleybigdata/warningemail:latest /bin/bash -c "cd /go/src/email;bee run email"

注：另有whaleybigdata/warningmailer镜像为开发组所使用，给定端口号，即可按照第三步运行