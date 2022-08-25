import time
from datetime import date
from functions import minutes_between, swap

TIME = time.ctime(time.time()).split(" ")[3][:-3]
TODAY = date.today()

patients1 = [
    {'full_name': 'Person 1', 'date': '2022-10-20 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 2', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 3', 'date': '2022-10-24 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 4', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-5 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-6 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-7 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-8 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 6', 'date': '-', 'is_sorted': 'false'}
]

patients2 = [
    {'full_name': 'Person 1', 'date': '2022-10-20 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 3', 'date': '2022-10-24 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-5 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-6 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-7 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-8 17:00', 'is_sorted': 'false'}
]

patients3 = [
    {'full_name': 'Person 1', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 2', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 3', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 4', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 6', 'date': '-', 'is_sorted': 'false'},
    {'full_name': 'Person 3', 'date': '2022-10-24 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-5 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-6 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-7 17:00', 'is_sorted': 'false'},
    {'full_name': 'Person 5', 'date': '2022-9-8 17:00', 'is_sorted': 'false'},
]

patients4 = [
    {'full_name': 'Person 1', 'date': '2022-07-17 08:00', 'is_sorted': 'false'},
    {'full_name': 'Person 2', 'date': '2022-08-16 18:30', 'is_sorted': 'false'},
    {'full_name': 'Person 3', 'date': '2022-08-20 13:00', 'is_sorted': 'false'}
]



def function(array):
    sorted_patients = array.copy()
    length = len(sorted_patients)

    # Sorting patients who doesn't have appointment to the end of the list
    counter1 = length-1
    for i in range(length-1, -1, -1):
        if sorted_patients[i]["date"] == "-":
            # Move to the bottom of the list
            sorted_patients[i]["is_sorted"] = "true"
            swap(sorted_patients, i, counter1)
            counter1 -= 1

    # Sorting patients who have an appointment from latest to earlier
    swap_counter = -1
    j = 0
    while swap_counter != 0:
        swap_counter = 0
        for i in range(0, counter1-j):
            if minutes_between(
                    sorted_patients[i]["date"].split(" ")[0],
                    sorted_patients[i]["date"].split(" ")[1],
                    sorted_patients[i+1]["date"].split(" ")[0],
                    sorted_patients[i+1]["date"].split(" ")[1]) > 0:
                swap(sorted_patients, i, i+1)
                swap_counter += 1
        j += 1

    return sorted_patients



for patient in function(patients4):
    print(patient)