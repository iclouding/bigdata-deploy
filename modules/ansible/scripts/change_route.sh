#!/bin/bash
route add default gw 10.255.128.49
route del default gw 10.255.131.254
ip route add 10.0.0.0/8 via 10.255.131.254 dev bond0