import pandas as pd

grades = {
    "name": ["Mike", "Sherry", "Cindy", "John"],
    "math": [80, 75, 93, 86],
    "chinese": [63, 90, 85, 70]
}

df = pd.DataFrame(grades)


df.to_csv('hrdata_modified.csv')

