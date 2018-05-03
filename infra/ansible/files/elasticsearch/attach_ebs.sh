#!/bin/bash
set -e

mkfs -t ext4 /dev/xvdh
mkdir -p /opt/ebs-data
mount /dev/xvdh /opt/ebs-data
echo /dev/xvdh  /opt/ebs-data ext4 defaults,nofail 0 2 >> /etc/fstab
