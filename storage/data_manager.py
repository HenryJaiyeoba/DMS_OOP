import json
import os

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {"users": [], "rooms": [], "maintenance_requests": [], "payments": []}

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=2)

    def add_user(self, user):
        user_data = user.__dict__.copy()
        user_data['role'] = user.__class__.__name__.lower()
        if 'room' in user_data:
            user_data['room'] = user_data['room'].room_number if user_data['room'] else None
        self.data['users'].append(user_data)
        self.save_data()

    def get_users(self):
        return self.data['users']

    def add_room(self, room):
        room_data = room.__dict__.copy()
        room_data['occupants'] = [occupant.student_id for occupant in room.occupants]
        self.data['rooms'].append(room_data)
        self.save_data()

    def get_rooms(self):
        return self.data['rooms']

    def add_maintenance_request(self, request):
        request_data = request.__dict__.copy()
        request_data['student'] = request.student.student_id
        request_data['created_at'] = request.created_at.isoformat()
        self.data['maintenance_requests'].append(request_data)
        self.save_data()

    def get_maintenance_requests(self):
        return self.data['maintenance_requests']

    def add_payment(self, payment):
        payment_data = payment.__dict__.copy()
        payment_data['student'] = payment.student.student_id
        payment_data['due_date'] = payment.due_date.isoformat()
        self.data['payments'].append(payment_data)
        self.save_data()

    def get_payments(self):
        return self.data['payments']

    def update_data(self, category, item_id, updates):
        for item in self.data[category]:
            if item['id'] == item_id:
                item.update(updates)
                self.save_data()
                return True
        return False