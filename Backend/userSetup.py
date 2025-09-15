from datasets import load_dataset
import pandas as pd
import os
from typing import Any
from enum import Enum

def setup_categories()-> None:
    dataset: Any = load_dataset("ashraq/fashion-product-images-small")
    train: pd.DataFrame = pd.DataFrame(dataset["train"])  
    print(train.head())
    for i in ["masterCategory", "subCategory","articleType", "baseColour","season", "usage"]:
        if not os.path.exists("ProdData"):
            os.makedirs("ProdData")
        if not os.path.exists(f"ProdData/{i}.txt"):
            with open(f"ProdData/{i}.txt", "w") as f:
                for category in train[i].unique():
                    f.write(category + "\n")

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class User:
    username: str
    password: str
    role: UserRole
    pref_counter: dict
    def __init__(self, username: str, password: str, role: UserRole):
        self.username = username
        self.password = password
        self.role = role

    def set_init_pref(self,**kwargs) -> None:
        assert kwargs is not None && len(kwargs) > 2 # Check if the user actually entered some data
        pref = {i:1 for i in kwargs} # We don't know the rankings yet

    def get_recs(self) -> list[Any]:
        from random import choice
        ch1 = None #Will add later
        return []

class budgetMacro:
    def __init__(self):
        for i in ["masterCategory", "subCategory","articleType", "baseColour","season", "usage"]:
            with open(f"ProdData/{i}.txt", "r") as f:
                categories = [line.strip() for line in f.readlines()]
                enum_members = '\n    '.join([f"{cat.upper().replace(' ', '_').replace('-', '_')} = '{cat}'" for cat in categories])
                print(f"class {i.capitalize()}(Enum):\n    {enum_members}")

def main():
    pass

if __name__ == "__main__":
    main()
