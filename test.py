from datetime import date
from math import floor

TODAY = date.today()

def Years_Between(date1, date2):
    date1 = str(date1)
    date2 = str(date2)
    
    years1 = int(date1.split("-")[0]) + (int(date1.split("-")[1])/12) + (int(date1.split("-")[2])/365)
    years2 = int(date2.split("-")[0]) + (int(date2.split("-")[1])/12) + (int(date2.split("-")[2])/365)
    
    return floor(abs(years1 - years2))

print(Years_Between("2007-12-04", TODAY))