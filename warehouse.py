import json
import math
from typing import Union
from fastapi import FastAPI, Response, status, Header, Request, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from utils import get_hash, encode_token, SECRET, authorize
import jwt
load_dotenv()

with open("gudang.json", "r") as read_file:
    data = json.load(read_file)

with open("user.json", "r") as read_file:
    akun = json.load(read_file)

app = FastAPI()

class LoginParamater(BaseModel):
    username: str
    password: str

@app.post('/login')
def login(param: LoginParamater, response: Response):
    found = False
    for i in range (len(akun)) :
        if (param.username == akun[i]["username"]):
            found = True
            if (get_hash(param.password) == akun[i]["password"]):
                token = encode_token(param.username)
                return { 
                    "message": "Login Sukses",
                    "data": { "token": token }
                }
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Password Salah Bre"}
    if not found:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "User not found!" }

#Read Data Warehouse
@app.get('/gudang')
async def get_warehouse(request: Request):
    authorize(request)
    return data["gudang"]

class AddBarang(BaseModel):
    nama: str
    jenis: str
    stok: float
    jumlahMinimum: float
    hargaModal: float

#Add New Data
@app.post('/gudang')
async def add_barang(request: Request, param: AddBarang):
    authorize(request)
    id = 1
    if (len(data["gudang"]) > 0) :
        id = data["gudang"][len(data["gudang"]) - 1]["id"] + 1
    new_data = {
        'id': id,
        'nama': param.nama, 
        'jenis': param.jenis, 
        'stok': param.stok, 
        'jumlahMinimum': param.jumlahMinimum,
        'hargaModal': param.hargaModal
    }
    data["gudang"].append(dict(new_data))

    with open("gudang.json", "w") as write_file :
        json.dump(data, write_file, indent = 4)
    return {"message": "Data barang berhasil ditambahkan"}

class UpdateStok(BaseModel):
    nama: str
    quantity: float

#Update Stok Barang
@app.put('/gudang/stok')
async def update_barang(request: Request, param: UpdateStok):
    authorize(request)
    found = False
    for warehouse in data['gudang']:
        if (param.nama == warehouse["nama"]):
            found = True
            if (param.quantity < warehouse["stok"]):
                warehouse["stok"] += param.quantity
                with open("gudang.json", "w") as write_file :
                    json.dump(data, write_file, indent = 4)
                if (warehouse["stok"] <= warehouse["jumlahMinimum"]):
                    return { "message": "Data barang berhasil diupdate, barang sudah dapat dipesan kembali" }
                else:
                    return { "message": "Data barang berhasil diupdate" }
            else:
                return { "message": "Masukan Salah" }
    if not found:
        return { "message": "Barang Tidak Ada" }

class UpdateHarga(BaseModel):
    nama: str
    hargaModal: float

#Update Harga Barang
@app.put('/gudang/harga')
async def update_barang(request: Request, param: UpdateHarga):
    authorize(request)
    found = False
    for warehouse in data['gudang']:
        if (param.nama == warehouse["nama"]):
            found = True
            warehouse["hargaModal"] = param.hargaModal
            with open("gudang.json", "w") as write_file :
                json.dump(data, write_file, indent = 4)
            return { "message": "Data barang berhasil diupdate" }
    if not found:
        return { "message": "Barang Tidak Ada" }

#Mendapat List Barang yang Harus Dipesan
@app.get('/gudang/listPesanBarang')
async def liat_list_barang(request: Request):
    authorize(request)
    listBarang = []
    found = False
    for warehouse in data['gudang']:
        if (warehouse["stok"] <= warehouse["jumlahMinimum"]):
            found = True
            listBarang.append(warehouse["nama"])
    if not found:
        return { "message": "Belum Ada Barang yang Harus Dipesan Kembali" }
    return listBarang


class FilterHarga(BaseModel):
    harga: float

#Mendapat Filter Barang dari Harga yang Dimasukkan
@app.get('/gudang/filterHarga')
async def filter_harga(request: Request, param:FilterHarga):
    authorize(request)
    listBarang = []
    found = False
    for warehouse in data['gudang']:
        if (warehouse["hargaModal"] <= param.harga):
            found = True
            listBarang.append(warehouse)
    if not found:
        return { "message": "Tidak Ditemukan Barang yang Lebih Murah dari Masukan" }
    return listBarang

class FilterJenis(BaseModel):
    jenis: str

#Mendapat Filter Barang dari Harga yang Dimasukkan
@app.get('/gudang/filterJenis')
async def filter_jenis(request: Request, param:FilterJenis):
    authorize(request)
    listBarang = []
    found = False
    for warehouse in data['gudang']:
        if (warehouse["jenis"] <= param.jenis):
            found = True
            listBarang.append(warehouse)
    if not found:
        return { "message": "Tidak Ditemukan Barang Berjenis Seperti Masukan" }
    return listBarang

class LiatHarga(BaseModel):
    nama: str
    keuntungan: float

#Melihat Harga Jual Barang Berdasarkan Keuntungan yang Diinginkan
@app.get('/gudang/hargaJual')
async def get_hargaJual(request: Request, param:LiatHarga):
    authorize(request)
    found = False
    for warehouse in data['gudang']:
        if (warehouse["nama"] == param.nama):
            return {
                warehouse["nama"], 
                warehouse["hargaModal"] + 1000 * math.ceil(warehouse["hargaModal"] * param.keuntungan/1000)
            }
    if not found:
        return { "message": "Barang Tidak Ada" }

class DeleteBarang(BaseModel):
    nama: str

#Menghapus Data Barang
@app.delete('/gudang/deleteBarang')
async def delete_barang(request: Request, param: DeleteBarang):
    authorize(request)
    for warehouse in data['gudang']:
        if (warehouse["nama"] == param.nama):
            data['gudang'].remove(warehouse)
            with open("gudang.json", "w") as write_file :
                json.dump(data, write_file, indent = 4)
            return { "message": "Data Barang Berhasil Dihapus" }
    raise HTTPException (
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Data Barang Tidak Ada"
    )

class LiatLaba(BaseModel):
    nama: str
    unitBeli: float
    unitTerjual: float
    hargaJual: float

#Menghitung Laba Kotor Suatu Barang Menggunakan Metode FIFO Sistem Periodik
@app.get('/gudang/hitungLaba')
async def liat_laba(request: Request, param: LiatLaba):
    authorize(request)
    for warehouse in data['gudang']:
        if (warehouse["nama"] == param.nama):
            unitSiapJual = warehouse["stok"] + param.unitBeli
            unitPersediaanAkhir = unitSiapJual - param.unitTerjual
            hpp = unitSiapJual * warehouse["hargaModal"] - unitPersediaanAkhir * warehouse["hargaModal"]
            labaKotor = param.unitTerjual * param.hargaJual - hpp
            if (labaKotor >= 0.5 * warehouse["hargaModal"]):
                return {
                    "message": [
                        "Laba Kotor yang Didapat Adalah",
                        labaKotor,
                        "Barang Harus di Stok Lebih Banyak"
                    ]
                }
            else:
                return { 
                    "message": [
                        "Laba Kotor yang Didapat Adalah", 
                        labaKotor
                    ]
                }
    raise HTTPException (
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Data Barang Tidak Ada"
    )