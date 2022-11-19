import json
from typing import Union
from fastapi import FastAPI

with open("gudang.json", "r") as read_file:
    data = json.load(read_file)
app = FastAPI()

@app.get('/')
def identitas():
    return {'Natanael Dias (18220051)'}

#Read Data Warehouse
@app.get('/gudang')
async def get_warehouse():
    return data["gudang"]

#Add New Data
@app.post('/gudang')
async def add_barang(nama: str, jenis: str, stok: float, jumlahMinimum: float):
    id = 1
    if (len(data["gudang"]) > 0) :
        id = data["gudang"][len(data["gudang"]) - 1]["id"] + 1
    new_data = {'id': id, 'nama': nama, 'jenis': jenis, 'stok': stok, 'jumlahMinimum': jumlahMinimum}
    data["gudang"].append(dict(new_data))

    with open("gudang.json", "w") as write_file :
        json.dump(data, write_file, indent = 4)
    return {"message": "Data barang berhasil ditambahkan"}
    write_file_close()