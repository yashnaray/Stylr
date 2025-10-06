from datasets import load_dataset
import pandas as pd
import os
from typing import Any
from enum import Enum
from collections import Counter
import userEnums
from PIL import Image

def setup_categories()-> None:
    dataset: Any = load_dataset("ashraq/fashion-product-images-small")
    train: pd.DataFrame = pd.DataFrame(dataset["train"])  
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
    pref_counter: Counter[str|int]
    _dataset = None
    
    def __init__(self, username: str, password: str, role: UserRole):
        self.username = username
        self.password = password
        self.role = role
        if User._dataset is None:
            User._dataset = pd.DataFrame(load_dataset("ashraq/fashion-product-images-small")["train"])

    def set_init_pref(self,**kwargs) -> None: # kwargs are of type userEnums
        assert kwargs is not None and len(kwargs) > 2
        self.pref_counter = Counter({k: kwargs[k].value for k in kwargs})

    def get_recs(self) -> list[Any]:
        from random import random, sample
        if not hasattr(self, 'pref_counter') or not self.pref_counter: return []
        
        df = User._dataset.copy()
        
        if 'gender' in self.pref_counter:
            gender_map = {'Male': 'Men', 'Female': 'Women'}
            mapped_gender = gender_map.get(self.pref_counter['gender'], self.pref_counter['gender'])
            df = df[df['gender'] == mapped_gender]
        
        other_prefs = {k: v for k, v in self.pref_counter.items() if k != 'gender'}
        if other_prefs:
            rand = random()
            if rand < 0.8: match_count = max(1, int(0.8 * len(other_prefs)))
            elif rand < 0.95: match_count = max(1, int(0.6 * len(other_prefs)))
            else: return sample(df.to_dict('records'), min(5, len(df))) if len(df) > 0 else []
            
            selected_prefs = dict(sample(list(other_prefs.items()), min(len(other_prefs), match_count)))
            
            for key, value in selected_prefs.items():
                if key in df.columns: df = df[df[key] == value]
            
            return sample(df.to_dict('records'), min(5, len(df))) if len(df) > 0 else []
        
        return sample(df.to_dict('records'), min(5, len(df))) if len(df) > 0 else []

class budgetMacro:
    def __init__(self):
        for i in ["masterCategory", "subCategory","articleType", "baseColour","season", "usage"]:
            with open(f"ProdData/{i}.txt", "r") as f:
                categories = [line.strip() for line in f.readlines()]
                enum_members = '\n    '.join([f"{cat.upper().replace(' ', '_').replace('-', '_')} = '{cat}'" for cat in categories])
                print(f"class {i.capitalize()}(Enum):\n    {enum_members}")

def main():
    u = User("test", "test", UserRole.USER)
    u.set_init_pref(gender = userEnums.Gender.MALE, baseColour= userEnums.Basecolour.BLACK, season=userEnums.Season.SUMMER)
    
    recs = u.get_recs()
    if recs:
        print(f"Found {len(recs)} recommendations:")
        for i, rec in enumerate(recs):
            print(f"{i+1}. {rec['productDisplayName']}")
        recs[0]['image'].show()
    else:
        print("No recommendations found")
if __name__ == "__main__":
    main()
