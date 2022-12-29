# Gehaltszettel Reader
Supports reading "Gehaltszettel" of pdf format.

Can extract the following information:
- Betriebsratsumlage

Setup:
1. Clone git repo
2. Create .env file in root
3. Add password to the .env file as follows

*.env* example:
```ini
password=1234
```

Usage:
```
usage: main.py [-h] path year

positional arguments:
  path
  year

options:
  -h, --help  show this help message and exit
```
e.g.
```
python ./main.py /home/username/Gehaltsabrechnung 2022
```