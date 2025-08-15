
import pandas as pd
NSW_train_patronage = pd.read_csv('NSW_Train_patronage_per_station.csv')
VIC_train_patronage = pd.read_csv('Victoria_Train_patronage_per_station.csv')

Modified_NSW_train_patronage = NSW_train_patronage.str.strip('_id')

def NSW_patronage():
    options = input('choose 1 if you would like to look at NSW train patronage. Press anything else to exit')
    if options == '1':
        print(Modified_NSW_train_patronage)



def dataset_home():
    print('\n === This is the dataset homepage: ===')
    print('\n Here, you can use and manipulate the listed datasets')
    print('\n1. train patronage in NSW suburbs and their densities')
    print('2. train patronage in VIC suburbs and their densities')
    print('3. Car ownership in the city of sydney')
    while True:
        data_choice = input('Choose between 1 and 2 to choose dataset')
        if data_choice == '1':
            print('You are viewing NSW train patronage')
            break
        elif data_choice == '2':
            print('You are viewing VIC patronage')
            break
        elif data_choice == '3':
            print('You are now looking at city of sydney car ownership')
            break
        else:
            print('error, press either one, two or three')


def thesis_question():
    print('\n === Main Thesis question: ===')
    print('"How does population density affect public transport usage and car ownership in Australian suburbs?"')
    print('\n This thesis statement shows...')
    while True:
        choice = input('press 1 to move onto dataset list and press 2 to exit')
        if choice == '1':
            print('going to dataset list...')
            dataset_home
            break
        elif choice == '2':
            Title_Screen()
            break
        else:
            print('error, press either one or 2')
        


def Title_Screen():
    print('\n === Main Menu === ')
    print('1. View thesis question')
    print('2. View dataset list')
    print('3. Exit')

    choice = input('Choose between 1, 2 and 3 to choose next destination')
    if choice == '1':
        thesis_question()
    elif choice == '2':
        dataset_home()
    else:
        print('error')


    
# Title_Screen()
NSW_patronage()

