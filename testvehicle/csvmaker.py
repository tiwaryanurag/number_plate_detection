import csv

# Data to be written to the CSV file
data = [
    ['plate_number','owner_name','make','model','color'],
    ['HR26DK8337','Raj','Tesla','Y3','Red'],
    ['DL2C P 5428','Aryan','Tata','Nexon','Blue'],
    ['BR10F3464','Pankaj','TVS','Sports','Black'],
    ['MH04KF0011','UK07','Lambo','Urus','Yellow']
]

# File name for the CSV file
filename = '/home/aryan/code/vehicle/database.csv'
# /home/aryan/code/vehicle/database.csv

# Writing data to CSV file
with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(data)

print(f"CSV file '{filename}' created successfully.")
