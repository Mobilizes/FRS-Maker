#!/usr/bin/bash

x=1

while true; do
  python3 ratingUpdate.py
  echo "Updated : $x"
  x=$((x + 1))
  sleep 10
done
