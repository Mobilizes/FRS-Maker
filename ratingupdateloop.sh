#!/usr/bin/bash

while true; do
  python3 ratingUpdate.py
  printf '\033[3J'
  jq -r '
    to_entries[] 
    | ("\n" + .key),
      (.value[] | [.Kode, ."Nama Dosen", ."Jumlah Murid", ."Max Murid"] | @tsv)
  ' jadwal.json | column -t -s $'\t'
  date
  sleep 15
done
