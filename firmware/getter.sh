#!/bin/bash
x=1
while [ $x -le 5 ]
do
echo " "
i2cget -y 1 0x20 0
i2cget -y 1 0x20 1
i2cget -y 1 0x20 2
i2cget -y 1 0x20 3
i2cget -y 1 0x20 4
i2cget -y 1 0x20 5
# sleep 0.1
done
