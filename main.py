import os

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
import pandas as pd
from pedia import generate_pedia_scores, setup_training
import json

output_path = "output"
train_path = "train"
train_label = "1KG"
test_path = "input"
test_file = "test_file.csv"

config_data = {
    'train_label': train_label,
    'train_path': train_path,
    'output_path': output_path,
    'train_file': os.path.join(output_path, "train.csv"),
    'test_path': test_path,
    'param_fold': 0,
    'mode': 0, 'test_file': test_file
}
train_data = None
class GeneBase(BaseModel):
    gene_name: str
    gene_id: int
    cada_score: float
    cadd_score: float
    gestalt_score: float
    label: bool

class GeneList(BaseModel):
    genes: List[GeneBase]

class Case(BaseModel):
    case: str 
    data: List[GeneBase]

class CaseList(BaseModel): 
    cases: List[Case]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global config_data
    global train_data

    train_data = setup_training(config_data)

    yield

app = FastAPI(lifespan=lifespan)

@app.post("/pedia")
async def get_scores_endpoint(genes: GeneList):
    json_input = json.loads(genes.json())

    output = generate_pedia_scores(json_input, config_data, train_data)
    return output

