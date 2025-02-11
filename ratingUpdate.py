from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import pprint

url = "https://akademik.its.ac.id/list_frs.php"

# use login credential
session = requests.Session()
session.cookies.setdefault('PHPSESSID', 'bp3lnsblia0co30pascc756gd2')

# get data
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
                j["Rating"] = 0 if murid_skrg == max_murid else j["Default Rating"]

                j["Jumlah Murid"] = murid_skrg
                j["Max Murid"] = max_murid

with open('jadwal.json', 'w') as file:
    json.dump(json_data, file, indent=2)
