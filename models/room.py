class Room:
    def __init__(self, room_number, capacity):
        self.room_number = room_number
        self.capacity = capacity
        self.occupants = []

    def add_occupant(self, student):
        if len(self.occupants) < self.capacity:
            self.occupants.append(student)
            student.room = self
            return True
        return False

    def remove_occupant(self, student):
        if student in self.occupants:
            self.occupants.remove(student)
            student.room = None
            return True
        return False

    @property
    def is_vacant(self):
        return len(self.occupants) < self.capacity