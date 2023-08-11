import re

string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36" 
pattern = '\([^)]+\)|\S+\/'
result = re.findall(pattern, string)
print(result)
print(len(result))
