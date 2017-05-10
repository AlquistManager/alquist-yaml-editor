import os

from states.state import State



class text_test(State):
    # execute state
    def execute(self, request_data) -> dict:
        #os.chdir(r'C:\Users\Izemir\Desktop\alquist-yaml-editor-master\bots\Cities\states')



        request_data['context'].update({'result': str('true'), 'result_user': str('false')})

        user_city = request_data['context']['text_user']

        user_city = user_city.lower()

        bot_last_letter = request_data['context']['bot_last_letter']

        bot_last_letter = bot_last_letter[0]

        if bot_last_letter is user_city[:1]:





            user_want_control = request_data['context']['control']

            if(str(user_want_control) == 'True'):



                city_exists = False

                with open(os.getcwd() + '/bots/Cities/data/cities.txt') as f:
                    cities = f.read().splitlines()



                for line in cities:
                    line2 = line.split(',')
                    if str(line2[1]).lower() == str(user_city):
                        city_exists = True
            else:

                city_exists = True

            if city_exists:
                request_data['context'].update({'result_user': str('true')})
                request_data['context'].update({'user_last_letter': str(user_city[-1:])})
                request_data['context'].update({'user_big_letter': str((user_city[-1:]).upper())})




        request_data.update({'next_state': self.transitions.get('next_state', False)})
        return request_data
