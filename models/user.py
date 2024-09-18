import hashlib

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = self._hash_password(password)
        self.role = role

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password == self._hash_password(password)

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, "admin")

class Manager(User):
    def __init__(self, username, password):
        super().__init__(username, password, "manager")

class Student(User):
    def __init__(self, username, password, student_id, contact_info, gender, department, year):
        super().__init__(username, password, "student")
        self.student_id = student_id
        self.contact_info = contact_info
        self.gender = gender
        self.department = department
        self.year = year
        self.room = None

    def edit_profile(self, contact_info=None, gender=None, department=None, year=None):
        if contact_info:
            self.contact_info = contact_info
        if gender:
            self.gender = gender
        if department:
            self.department = department
        if year:
            self.year = year
