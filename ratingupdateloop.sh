#!/usr/bin/zsh

while true; do
  python3 ratingUpdate.py
  clear && printf '\e[3J'
  zle && zle .reset-prompt && zle -R
  jq -r '
    to_entries[] 
    | ("\n" + .key),
      (.value[] | [.Kode, ."Nama Dosen", ."Jumlah Murid", ."Max Murid", ."Rating"] | @tsv)
  ' jadwal.json | column -t -s $'\t'
  date
  sleep 15
done
