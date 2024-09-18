from models.user import User, Admin, Manager, Student

class Authenticator:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.users = self.load_users()

    def load_users(self):
        users = []
        for user_data in self.data_manager.get_users():
            if user_data['role'] == 'admin':
                user = Admin(user_data['username'], user_data['password'])
            elif user_data['role'] == 'manager':
                user = Manager(user_data['username'], user_data['password'])
            elif user_data['role'] == 'student':
                user = Student(user_data['username'], user_data['password'],
                               user_data['student_id'], user_data['contact_info'],
                               user_data['gender'], user_data['department'], user_data['year'])
            else:
                continue
            users.append(user)
        return users

    def register_user(self, username, password, role, **kwargs):
        if any(user.username == username for user in self.users):
            raise ValueError("Username already exists")

        if role == "admin":
            user = Admin(username, password)
        elif role == "manager":
            user = Manager(username, password)
        elif role == "student":
            user = Student(username, password, **kwargs)
        else:
            raise ValueError("Invalid role")
        
        self.users.append(user)
        self.data_manager.add_user(user)
        return user

    def login(self, username, password):
        for user in self.users:
            if user.username == username and user.check_password(password):
                return user
        return None

    def change_password(self, user, old_password, new_password):
        if user.check_password(old_password):
            user.password = user._hash_password(new_password)
            self.data_manager.update_data('users', user.username, {'password': user.password})
            return True
        return False

    def get_user_by_id(self, student_id):
        for user in self.users:
            if isinstance(user, Student) and user.student_id == student_id:
                return user
        return None