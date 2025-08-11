
import pandas as pd
NSW_train_patronage = pd.read_csv('NSW_Train_patronage_per_station.csv')
VIC_train_patronage = pd.read_csv('Victoria_Train_patronage_per_station.csv')



def thesis_question():
    print('\n === Main Thesis question: ===')
    print('"How does population density affect public transport usage and car ownership in Australian suburbs?"')
    print('\n This thesis statement shows...')
    while True:
        choice = input('press 1 to move onto dataset list and press 2 to exit')
        if choice == '1':
            print('going to dataset list...')
            break
        elif choice == '2':
            Title_Screen()
            break
        else:
            print('error, press either one or 2')



def Title_Screen():
    while True:
        print('\n === Main Menu === ')
        print('1. View thesis question')
        print('2. View dataset list')
        print('3. Exit')

        choice = input('Choose between 1, 2 and 3 to choose next destination')
        if choice == '1':
            thesis_question()

    
# Title_Screen()

print(NSW_train_patronage)

