from states.state import State



class write(State):
    # execute state
    def execute(self, request_data) -> dict:

        #city =







        request_data.update({'next_state': self.transitions.get('next_state', False)})
        return request_data
