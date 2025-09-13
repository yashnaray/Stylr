from datasets import load_dataset
import pandas as pd
import os
from typing import Any
from datasets import Dataset
from enum import Enum

def setup_categories()-> None:
    dataset: Any = load_dataset("ashraq/fashion-product-images-small")
    train: pd.DataFrame = pd.DataFrame(dataset["train"])  
    for i in ["gender","masterCategory", "subCategory","articleType", "baseColour","season", "usage"]:
        if not os.path.exists("ProdData"):
            os.makedirs("ProdData")
        if not os.path.exists(f"ProdData/{i}.txt"):
            with open(f"ProdData/{i}.txt", "w") as f:
                for category in train[i].unique():
                    f.write(category + "\n")

def main():
    setup_categories()

if __name__ == "__main__":
    main()