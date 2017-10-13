以下功能指令均需在/data/tools/ansible/modules/dw/etl/playbook中执行

--安装包分发
ansible all -i dw_etl.host -m shell -a "rm -f /opt/dw/etl/.install"
ansible-playbook -i dw_etl.host install_dw_etl.yml -t install


--配置分发
ansible-playbook -i dw_etl.host install_dw_etl.yml -t config
