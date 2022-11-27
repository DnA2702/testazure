import json
from typing import Union
from fastapi import FastAPI, Response, status, Header, Request
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
    print(param.username)
    print(param.password)
    for i in range (len(akun)) :
        if (param.username == akun[i]["username"]):
            found = True
            if (get_hash(param.password) == akun[i]["password"]):
                token = encode_token(param.username)
                print(token)
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
        

# @app.get('/')
# def identitas():
#     return {'Natanael Dias (18220051)'}

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
        'jumlahMinimum': param.jumlahMinimum
    }
    data["gudang"].append(dict(new_data))

    with open("gudang.json", "w") as write_file :
        json.dump(data, write_file, indent = 4)
    return {"message": "Data barang berhasil ditambahkan"}
    write_file_close()