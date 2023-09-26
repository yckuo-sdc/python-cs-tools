import os
import pickle
import pandas as pd

path_to_pickle = os.path.join(os.path.dirname(__file__), "data", "pickle",
                              "ipdn_dump.pickle")
with open(path_to_pickle, 'rb') as f:
    the_pickle = pickle.load(f)

print(len(the_pickle))

records = []
for key, value in the_pickle.items():
    #print(key, value)
    records.append({'IP': key} | value)


df = pd.DataFrame(records)
#print(df)
path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                           "ipdn_dump.csv")
df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
