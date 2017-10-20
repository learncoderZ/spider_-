from urllib.request import urlopen
from io import StringIO
import csv

data = urlopen("http://pythonscraping.com/files/MontyPythonAlbums.csv").read().decode('ascii', 'ignore')
dataFile = StringIO(data)
dictreader = csv.DictReader(dataFile)
#print(dictreader.fieldnames)

for row in dictreader:
    #print("The ablum \""+row[0]+"\" was released in "+str(row[1]))
    print(row)
