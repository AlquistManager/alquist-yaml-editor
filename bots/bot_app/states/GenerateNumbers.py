from states.state import State
import random


class GenerateNumbers(State):
    # execute state
    def execute(self, request_data) -> dict:
        number1 = random.randint(0,100)
        number2 = random.randint(0,100)
        request_data['context'].update({'number1': number1, 'number2': number2, 'sum': number1 + number2,
                                        'substraction': number1 - number2})
        request_data.update({'next_state': self.transitions.get('next_state', False)})
        print(request_data)
        return request_data
