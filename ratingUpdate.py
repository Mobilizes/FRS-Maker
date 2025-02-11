from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

url = "https://akademik.its.ac.id/list_frs.php"

# use login credential
load_dotenv()

session = requests.Session()
session.cookies.setdefault('PHPSESSID', os.getenv("TOKEN"))

# get data
response = session.get(url)
while response.status_code != 200:
    print("Failed to get response! Retrying...")
    time.sleep(1)
    response = session.get(url)
soup = BeautifulSoup(response.text, 'lxml')

rows = soup.find_all('table', class_='FilterBox')
data = rows[1].find_all('tr')
td_matkul = data[0].find_all('td')
matkul_depart = td_matkul[2].find_all('option')

dataMK = {'kode': [], 'nama_mk': [], 'kelas': [], 'ketersediaan': []}

for matkul in matkul_depart:
    raw = matkul.text.split()
    dataMK['kode'].append(raw[0])
    dataMK['nama_mk'].append(' '.join(raw[1:-2]))
    dataMK['kelas'].append(raw[-2])
    dataMK['ketersediaan'].append(raw[-1])

dataMK = pd.DataFrame(dataMK)

otherrows = soup.find_all('table', class_='GridStyle')
matkul_terambil = otherrows[0].find_all('tr', valign='top')

dataMKsendiri = {'kode': [], 'nama_mk': [], 'sks': [], 'kelas': [], 'alih_kredit': []}

for matkul in matkul_terambil:
    raw = [td.text for td in matkul.find_all('td')]
    dataMKsendiri['kode'].append(raw[0])
    dataMKsendiri['nama_mk'].append(raw[1])
    dataMKsendiri['sks'].append(raw[2])
    dataMKsendiri['kelas'].append(raw[3])
    dataMKsendiri['alih_kredit'].append(raw[4])

dataMKsendiri = pd.DataFrame(dataMKsendiri)

# data matakuliah sem 4
courses = [
    "Pemrograman Jaringan",
    "Probabilitas dan Statistik",
    "Otomata",
    "Manajemen Basis Data",
    "Perancangan dan Analisis Algoritma",
    "Pembelajaran Mesin",
    "Perancangan Perangkat Lunak"
]

abbreviation = [
    "ProgJar",
    "Probstat",
    "Otomata",
    "MBD",
    "PAA",
    "PM",
    "PPL"
]

abbrandcourse = {
    "ProgJar": "Pemrograman Jaringan",
    "Probstat": "Probabilitas dan Statistik",
    "Otomata": "Otomata",
    "MBD": "Manajemen Basis Data",
    "PAA": "Perancangan dan Analisis Algoritma",
    "PM": "Pembelajaran Mesin",
    "PPL": "Perancangan Perangkat Lunak"
}

pd.set_option('display.max_rows', None)

pattern = '|'.join(courses)
dataMK = dataMK[dataMK['nama_mk'].str.contains(pattern)].reset_index(drop=True)

with open("jadwal.json", "r") as file:
    json_data = json.load(file)

for i, abbr in enumerate(abbreviation):
    class_data = dataMK[dataMK['nama_mk'].str.contains(courses[i])].reset_index(drop=True)
    for index, row in class_data.iterrows():
        kode = row['kode']
        nama_mk = row['nama_mk']
        kelas = row['kelas']
        ketersediaan = row['ketersediaan']
        murid_skrg, max_murid = map(int, ketersediaan.split('/'))

        for j in json_data[abbr]:
            if j["Kode"] == kelas:
                j["Rating"] = 0 if murid_skrg >= max_murid - 1 else j["Default Rating"]

                j["Jumlah Murid"] = murid_skrg
                j["Max Murid"] = max_murid

for matkul in dataMKsendiri.iterrows():
    matkul = matkul[1]
    nama_mk = matkul["nama_mk"].strip()
    if nama_mk not in courses:
        continue
    abbr = abbreviation[courses.index(nama_mk)]
    kelas = matkul["kelas"]

    for j in json_data[abbr]:
        j["Rating"] = 0
        if str(j["Kode"]) == str(kelas):
            j["Rating"] = 10

with open("pick_order.json", "r") as file:
    pick_order = json.load(file)

reordered_json_data = {}
for abbr in pick_order:
    if abbr in json_data:
        reordered_json_data[abbr] = json_data[abbr]

with open('jadwal.json', 'w') as file:
    json.dump(reordered_json_data, file, indent=2)
