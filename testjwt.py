# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 20:21:29 2024

@author: dcask
"""

from fastapi import Request, FastAPI
import requests
from fastapi import APIRouter, Depends, HTTPException
import jwt
import json

CERTS_URL = "https://example.visiology.su/idsrv/.well-known/openid-configuration/jwks"

async def validate_visiology(request: Request):
    if verify_token(request) != True:
        raise HTTPException(status_code=403, detail="Authorizatuon failed")


def _get_public_keys():
    r = requests.get(CERTS_URL)
    public_keys = []
    jwk_set = r.json()
    for key_dict in jwk_set["keys"]:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
        public_keys.append(public_key)
    return public_keys


def verify_token():
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkI4QTNCMzcwOEM2RUJDMDM2QjcyQjJBMUMzOTM3MDlGMTJENDAzOUUiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJ1S096Y0l4dXZBTnJjcktodzVOd254TFVBNTQifQ.eyJuYmYiOjE3MDQ5MTE1MzgsImV4cCI6MTcwNDkxNTEzOCwiaXNzIjoiaHR0cHM6Ly9leGFtcGxlLnZpc2lvbG9neS5zdS9pZHNydiIsImF1ZCI6WyJjb3JlX2xvZ2ljX2ZhY2FkZSIsImRhc2hib2FyZHNfZXhwb3J0X3NlcnZpY2UiLCJkYXRhX2NvbGxlY3Rpb24iLCJtaWdyYXRpb25fc2VydmljZV9hcGkiLCJzY3JpcHRfc2VydmljZSIsInZpcXViZV9hcGkiLCJ2aXF1YmVhZG1pbl9hcGkiXSwiY2xpZW50X2lkIjoicHVibGljX3JvX2NsaWVudCIsInN1YiI6IjYzYTA0Mjc4ZmYxNTI3MjI0OTk0ZmIzNCIsImF1dGhfdGltZSI6MTcwNDkxMTUzOCwiaWRwIjoibG9jYWwiLCJnaXZlbl9uYW1lIjoi0JDQvdC00YDQtdC5IiwiZmFtaWx5X25hbWUiOiLQmtGD0YDQuNC90YHQutC40LkiLCJuYW1lIjoiZGNhc2siLCJyb2xlIjpbIlRFU1QiLCLQkNC00LzQuNC90LjRgdGC0YDQsNGC0L7RgCIsItCS0YHQtSDQsNCy0YLQvtGA0LjQt9C-0LLQsNC90L3Ri9C1INC_0L7Qu9GM0LfQvtCy0LDRgtC10LvQuCIsItCe0L_QtdGA0LDRgtC-0YAg0LLQstC-0LTQsCIsItCU0L7RgdGC0YPQvyDQuiDQkdCUIFZpUXViZSJdLCJzY29wZSI6WyJlbWFpbCIsIm9wZW5pZCIsInByb2ZpbGUiLCJyb2xlcyIsImNvcmVfbG9naWNfZmFjYWRlIiwiZGFzaGJvYXJkc19leHBvcnRfc2VydmljZSIsImRhdGFfY29sbGVjdGlvbiIsIm1pZ3JhdGlvbl9zZXJ2aWNlX2FwaSIsInNjcmlwdF9zZXJ2aWNlIiwidmlxdWJlX2FwaSIsInZpcXViZWFkbWluX2FwaSJdLCJhbXIiOlsicHdkIl19.rhMzVjl9UIhGWEsYPJPTofWJoDnJcdz452zZjt6YhFDghYoKYX25FHm8owBNPzhSnKDpK4izvwpQw7vo-stJUrWkRZRtAH2N8skEOVi6zoTjq1Itp2ndcLRg0KV7Keb5IbzTyLLVTHO_STIsSRJl7u_8Td_CzfI57_QO1Rd1RXqmnTBCOy2DMvhfb0uloavgbrudtixARwSKnIZEF90AcEG6dagBWJ5X0ubKoy7niie2WDw___eQ8nQOaXbVkquWY6wOFTRY5B6RvcX2UWawlJsYpWBWNz6KAoAAAJSlZmTIaZxuwf7i8yl6qW6zCMBpwxSRhZPtAR6XMJ6ohUGS8c-1YsaLc5MWtk9MKoaRuvsPHMfjJjzKif4xw2n59VNNoOPCqc73XjhlmW6_KXKH3hOuhM-LtJ4-xI4OkocCuYnw1ovJSFpGEQTpousWq79gCk9Q76gI0EFcnpIeF14IwZX1hDohP_Y64JpmPAju_3xlZNMJoK96bKRMrbq8BGufKeHBNvcv9vrVDFscsmoUIITlhpoxOhplAtZQ87h_WJ5XeQmOMg013Jv0E8OPIXJuFMPh5eBBBvrSy6b83etG99RQT2QqWbnFnTCKpRMBe-HJh6X6ZJaAZt6RaAZ3WGMM6E0JuxQzTqnBxCTbl9K17A2-4rbmR00Pc9lvaoEF5-0"

    # if "CF_Authorization" in request.cookies:
    #     token = request.cookies["CF_Authorization"]
    # else:
    #     raise HTTPException(status_code=400, detail="missing required cf authorization token")

    keys = _get_public_keys()
    print(keys)
    valid_token = False
    for key in keys:
        try:
            jwtdecoded=jwt.decode(token, key=key, algorithms=["RS256"], options={"verify_aud": False, "verify_signature": True})
            if 'Администратор' in jwtdecoded['role']:
                valid_token = True
            break
        except:
            raise HTTPException(status_code=400, detail="Error decoding token")
    if not valid_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    return True

# app = FastAPI()
# router = APIRouter(
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(validate_visiology)],
#     responses={404: {"description": "Not found"}}
# )

# @router.get("/")
# async def root():
#     return {"message": "Hello World"}
print(verify_token())
