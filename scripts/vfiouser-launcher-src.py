#!/usr/bin/env python3
import socket
import os
import subprocess
import time

# Please launch the destination using
# Please connect to the source client using "socat /home/qemu-sock stdio"
# and initiate migration using "migrate -d tcp:0:4444" HMP command

PROC_QEMU='/home/qemu-separation/qemu-split/build/x86_64-softmmu/qemu-system-x86_64'

if os.path.exists("/tmp/remotesock"):
    os.remove("/tmp/remotesock")

remote_cmd = [ PROC_QEMU,                                                      \
               '-machine', 'x-remote,vfio-user=on',                            \
               '-device', 'megasas,id=sas1',                                   \
               '-drive', 'id=drive_image1,file=/home/ol7-test.qcow2',          \
               '-device', 'scsi-hd,id=drive1,drive=drive_image1,bus=sas1.0,'   \
                              'scsi-id=0',                                     \
               '-nographic',                                                   \
               '-monitor', 'unix:/home/rem-sock,server,nowait',                \
               '-object', 'x-vfio-user-server,id=vfioobj1,type=unix,path=/tmp/remotesock,device=sas1',                                       \
             ]

proxy_cmd = [ PROC_QEMU,                                                       \
              '-name', 'OL7.4',                                                \
              '-machine', 'pc,accel=kvm',                                      \
              '-smp', 'sockets=1,cores=1,threads=1',                           \
              '-m', '2048',                                                    \
              '-object', 'memory-backend-memfd,id=sysmem-file,size=2G',        \
              '-numa', 'node,memdev=sysmem-file',                              \
              '-device', 'virtio-scsi-pci,id=virtio_scsi_pci0',                \
              '-drive', 'id=drive_image1,if=none,format=qcow2,'                \
                            'file=/home/ol7-hdd-1.qcow2',                      \
              '-device', 'scsi-hd,id=image1,drive=drive_image1,'               \
                             'bus=virtio_scsi_pci0.0',                         \
              '-boot', 'd',                                                    \
              '-vnc', ':0',                                                    \
              '-device', 'vfio-user-pci,socket=/tmp/remotesock,x-enable-migration=true',               \
              '-monitor', 'unix:/home/qemu-sock,server,nowait',                \
            ]

pid = os.fork();

if pid:
    # In Proxy
    time.sleep(3)
    print('Launching QEMU with Proxy object');
    process = subprocess.Popen(proxy_cmd)
else:
    # In remote
    print('Launching Remote process');
    process = subprocess.Popen(remote_cmd)
