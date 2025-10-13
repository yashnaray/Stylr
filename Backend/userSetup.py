from datasets import load_dataset
import pandas as pd
import numpy as np
import os
from typing import Any
from enum import Enum
from collections import Counter
from functools import lru_cache
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
    __slots__ = ('username', 'password', 'role', 'pref_counter')
    _dataset = None
    _sample_pool = None
    
    def __init__(self, username: str, password: str, role: UserRole):
        self.username = username
        self.password = password
        self.role = role
        if User._dataset is None:
            df = pd.DataFrame(load_dataset("ashraq/fashion-product-images-small")["train"])
            cat_cols = ['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season', 'usage']
            for col in cat_cols:
                if col in df.columns:
                    df[col] = df[col].astype('category')
            User._dataset = df
            User._sample_pool = np.arange(len(df))
    
    @staticmethod
    @lru_cache(maxsize=256)
    def _get_filtered_data(prefs_tuple):
        df = User._dataset
        conditions = []
        for key, value in prefs_tuple:
            if key == 'gender':
                gender_map = {'Male': 'Men', 'Female': 'Women'}
                mapped_gender = gender_map.get(value, value)
                conditions.append(f"{key} == '{mapped_gender}'")
            elif key in df.columns:
                conditions.append(f"{key} == '{value}'")
        
        if conditions: 
            query = ' & '.join(conditions)
            filtered = df.query(query)
        else: filtered = df
        
        return filtered.index.tolist(), len(filtered)

    def set_init_pref(self,**kwargs) -> None: # kwargs are of type userEnums
        assert kwargs is not None and len(kwargs) > 2
        self.pref_counter = Counter({k: kwargs[k].value for k in kwargs})
    
    def update_preference(self, **kwargs) -> None: # kwargs are of type userEnums
        if not hasattr(self, 'pref_counter'):
            self.pref_counter = Counter()
        self.pref_counter.update({k: kwargs[k].value for k in kwargs})

    def get_recs(self, num_recs = 5) -> list[Any]:
        from random import sample
        if not hasattr(self, 'pref_counter') or not self.pref_counter: return []
        
        all_prefs = dict(self.pref_counter)
        other_prefs = {k: v for k, v in all_prefs.items() if k != 'gender'}
        
        rand = np.random.random()
        if other_prefs:
            if rand < 0.8: match_count = max(1, int(0.8 * len(other_prefs)))
            elif rand < 0.95: match_count = max(1, int(0.6 * len(other_prefs)))
            else: match_count = 0
            
            if match_count > 0: selected_prefs = dict(sample(list(other_prefs.items()), min(len(other_prefs), match_count)))
            else: selected_prefs = {}
        else: selected_prefs = {}
        
        if 'gender' in all_prefs: selected_prefs['gender'] = all_prefs['gender']
        
        prefs_tuple = tuple(sorted(selected_prefs.items()))
        indices, count = self._get_filtered_data(prefs_tuple)
        
        if not indices: return []
        
        n_samples = min(num_recs, count)
        if count <= num_recs:
            sample_indices = indices
        else:
            sample_indices = np.random.choice(indices, n_samples, replace=False)
        
        return User._dataset.iloc[sample_indices].to_dict('records')

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
    
    recs = u.get_recs(7)
    if recs:
        print(f"Found {len(recs)} recommendations:")
        for i, rec in enumerate(recs):
            print(f"{i+1}. {rec['productDisplayName']}")
        recs[0]['image'].show()
    else:
        print("No recommendations found")
if __name__ == "__main__":
    main()
