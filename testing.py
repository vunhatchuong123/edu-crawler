# from datetime import datetime

# date_str = "29-03-2021"

# # print(datetime.strptime(date, '%d-%m-%y').date())
# # date_str = '09-19-2018'

# date_object = datetime.strptime(date_str, '%d-%m-%Y').date().
# print(type(date_object))
# print(date_object)  # printed in default formatting

count = 0
while count < 3:
    try:
        print("trying")
    except:
        count += 1
        print("Stale ID, retry No." + str(count))

print("Finishes")
