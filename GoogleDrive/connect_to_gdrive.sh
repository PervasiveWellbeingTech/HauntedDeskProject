#!/bin/sh

umount $HOME/mnt/gdrive-test
rclone mount gdrive-test: $HOME/mnt/gdrive-test/
