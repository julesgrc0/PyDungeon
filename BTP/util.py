import uuid, os, pickle


class Storage:
    def __init__(self, id = None) -> None:
        self.id =  (str(uuid.uuid4()) if id is None else id) + '.dat'
        self._state = None
        
        if os.path.exists(self.id):
            file = open(self.id, 'rb') 
            self._state = pickle.load(file)
            file.close()

    def reset_state(self, obj):
        if len(dir(obj)) != len(dir(self._state)):
            self._state = obj
            file = open(self.id, 'wb') 
            pickle.dump(self._state, file)
            file.close()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        file = open(self.id, 'wb') 
        pickle.dump(self._state, file)
        file.close()
