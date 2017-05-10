from states.state import State

import random

import os




class random_city(State):
    # execute state
    def execute(self, request_data) -> dict:



        bot_city = request_data['context']['bot_city']
        cities = []
        good_cities = []
        countries = []

        last_letter = request_data['context']['user_big_letter']

        last_letter = last_letter[0]

        print(os.getcwd())


        with open(os.getcwd()+'/bots/Cities/data/cities.txt') as f:
            cities = f.read().splitlines()

        for line in cities:
            line2 = line.split(',')
            if line2[1][:1] is str(last_letter):
                good_cities.append(line2[1])
                countries.append(line2[0])

        size = len(good_cities)

        request_data['context'].update({'result_bot': str('false')})

        if size!=0:
            request_data['context'].update({'result_bot': str('true')})
            index = random.randint(0,size-1)

            bot_city = good_cities[index]
            country = countries[index]

            request_data['context'].update({'bot_city': str(bot_city)})
            request_data['context'].update({'country': str(country)})
            request_data['context'].update({'bot_last_letter': str(bot_city[-1:])})
            request_data['context'].update({'bot_big_letter': str((bot_city[-1:]).upper())})

        request_data.update({'next_state': self.transitions.get('next_state', False)})
        return request_data
