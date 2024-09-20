from auth.authenticator import Authenticator
from models.room import Room
from models.maintenance import MaintenanceRequest
from models.payment import Payment
from storage.data_manager import DataManager
from datetime import datetime
from models.user import Student, Admin, Manager


class DormitoryManagementSystem:
    """Some docstring here."""
    def __init__(self, data_file_path):
        self.data_manager = DataManager(data_file_path)
        self.authenticator = Authenticator(self.data_manager)
        self.rooms = self.load_rooms()
        self.maintenance_requests = self.load_maintenance_requests()
        self.payments = self.load_payments()
        self.current_user = None

    def load_rooms(self):
        rooms = []
        for room_data in self.data_manager.get_rooms():
            room = Room(room_data['room_number'], room_data['capacity'])
            rooms.append(room)
        return rooms

    def load_maintenance_requests(self):
        requests = []
        for request_data in self.data_manager.get_maintenance_requests():
            student = self.authenticator.get_user_by_id(request_data['student'])
            request = MaintenanceRequest(student, request_data['description'])
            request.id = request_data['id']
            request.status = request_data['status']
            request.created_at = datetime.fromisoformat(request_data['created_at'])
            requests.append(request)
        return requests

    def load_payments(self):
        payments = []
        for payment_data in self.data_manager.get_payments():
            student = self.authenticator.get_user_by_id(payment_data['student'])
            payment = Payment(student, payment_data['amount'], 
                              datetime.fromisoformat(payment_data['due_date']))
            payment.paid = payment_data['paid']
            payments.append(payment)
        return payments

    def register_user(self, username, password, role, **kwargs):
        return self.authenticator.register_user(username, password, role, **kwargs)

    def login(self, username, password):
        user = self.authenticator.login(username, password)
        if user:
            self.current_user = user
            return True
        return False

    def logout(self):
        self.current_user = None

    def change_password(self, old_password, new_password):
        if self.current_user:
            return self.authenticator.change_password(self.current_user, old_password, new_password)
        return False

    def add_room(self, room_number, capacity):
        room = Room(room_number, capacity)
        self.rooms.append(room)
        self.data_manager.add_room(room)

    def allocate_room(self, student, room):
        if isinstance(self.current_user, (Admin, Manager)):
            if room.add_occupant(student):
                self.data_manager.update_data('rooms', room.room_number, 
                                              {'occupants': [o.student_id for o in room.occupants]})
                self.data_manager.update_data('users', student.student_id, {'room': room.room_number})
                return True
        return False

    def search_student(self, student_id):
        return self.authenticator.get_user_by_id(student_id)

    def search_vacant_rooms(self):
        return [room for room in self.rooms if room.is_vacant]

    def create_maintenance_request(self, description):
        if isinstance(self.current_user, Student):
            request = MaintenanceRequest(self.current_user, description)
            self.maintenance_requests.append(request)
            self.data_manager.add_maintenance_request(request)
            return request
        return None

    def update_maintenance_request(self, request_id, new_status):
        if isinstance(self.current_user, (Admin, Manager)):
            for request in self.maintenance_requests:
                if request.id == request_id:
                    request.update_status(new_status)
                    self.data_manager.update_data('maintenance_requests', request_id, {'status': new_status})
                    return True
        return False

    def create_payment(self, student, amount, due_date):
        if isinstance(self.current_user, (Admin, Manager)):
            payment = Payment(student, amount, due_date)
            self.payments.append(payment)
            self.data_manager.add_payment(payment)
            return payment
        return None

    def check_payment_due(self, student):
        for payment in self.payments:
            if payment.student == student and not payment.paid and payment.due_date <= datetime.now():
                return payment
        return None

    def run(self):
        while True:
            if not self.current_user:
                print("\n1. Login")
                print("2. Register")
                print("3. Exit")
                choice = input("Enter your choice: ")

                if choice == "1":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    if self.login(username, password):
                        print("Login successful")
                    else:
                        print("Invalid credentials")
                elif choice == "2":
                    self.register_user_cli()
                elif choice == "3":
                    break
                else:
                    print("Invalid choice")
            else:
                if isinstance(self.current_user, Admin):
                    self.admin_menu()
                elif isinstance(self.current_user, Manager):
                    self.manager_menu()
                elif isinstance(self.current_user, Student):
                    self.student_menu()

    def register_user_cli(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        role = input("Enter role (admin/manager/student): ")
        
        if role == "student":
            student_id = input("Enter student ID: ")
            contact_info = input("Enter contact info: ")
            gender = input("Enter gender: ")
            department = input("Enter department: ")
            year = input("Enter year: ")
            
            try:
                self.register_user(username, password, role, 
                                   student_id=student_id, 
                                   contact_info=contact_info, 
                                   gender=gender, 
                                   department=department, 
                                   year=year)
                print("Student registered successfully")
            except ValueError as e:
                print(f"Registration failed: {str(e)}")
        else:
            try:
                self.register_user(username, password, role)
                print(f"{role.capitalize()} registered successfully")
            except ValueError as e:
                print(f"Registration failed: {str(e)}")
                
    def admin_menu(self):
        while True:
            print("\nAdmin Menu")
            print("1. Add Room")
            print("2. Allocate Room")
            print("3. View Maintenance Requests")
            print("4. Update Maintenance Request")
            print("5. Create Payment")
            print("6. View Payments")
            print("7. Logout")
            choice = input("Enter your choice: ")

            if choice == "1":
                room_number = input("Enter room number: ")
                capacity = int(input("Enter room capacity: "))
                self.add_room(room_number, capacity)
                print("Room added successfully")
            elif choice == "2":
                student_id = input("Enter student ID: ")
                room_number = input("Enter room number: ")
                student = self.search_student(student_id)
                room = next((r for r in self.rooms if r.room_number == room_number), None)
                if student and room:
                    if self.allocate_room(student, room):
                        print("Room allocated successfully")
                    else:
                        print("Failed to allocate room")
                else:
                    print("Invalid student or room")
            elif choice == "3":
                for request in self.maintenance_requests:
                    print(f"ID: {request.id}, Student: {request.student.username}, "
                          f"Description: {request.description}, Status: {request.status}")
            elif choice == "4":
                request_id = input("Enter request ID: ")
                new_status = input("Enter new status: ")
                if self.update_maintenance_request(request_id, new_status):
                    print("Maintenance request updated successfully")
                else:
                    print("Failed to update maintenance request")
            elif choice == "5":
                student_id = input("Enter student ID: ")
                amount = float(input("Enter payment amount: "))
                due_date = input("Enter due date (YYYY-MM-DD): ")
                student = self.search_student(student_id)
                if student:
                    due_date = datetime.strptime(due_date, "%Y-%m-%d")
                    self.create_payment(student, amount, due_date)
                    print("Payment created successfully")
                else:
                    print("Invalid student ID")
            elif choice == "6":
                for payment in self.payments:
                    print(f"Student: {payment.student.username}, Amount: {payment.amount}, "
                          f"Due Date: {payment.due_date}, Paid: {payment.paid}")
            elif choice == "7":
                self.logout()
                break
            else:
                print("Invalid choice")

    def manager_menu(self):
        while True:
            print("\nManager Menu")
            print("1. View Rooms")
            print("2. View Students")
            print("3. View Maintenance Requests")
            print("4. Update Maintenance Request")
            print("5. Logout")
            choice = input("Enter your choice: ")

            if choice == "1":
                for room in self.rooms:
                    print(f"Room: {room.room_number}, Capacity: {room.capacity}, "
                          f"Occupants: {len(room.occupants)}")
            elif choice == "2":
                for user in self.authenticator.users:
                    if isinstance(user, Student):
                        print(f"ID: {user.student_id}, Name: {user.username}, "
                              f"Department: {user.department}, Year: {user.year}")
            elif choice == "3":
                for request in self.maintenance_requests:
                    print(f"ID: {request.id}, Student: {request.student.username}, "
                          f"Description: {request.description}, Status: {request.status}")
            elif choice == "4":
                request_id = input("Enter request ID: ")
                new_status = input("Enter new status: ")
                if self.update_maintenance_request(request_id, new_status):
                    print("Maintenance request updated successfully")
                else:
                    print("Failed to update maintenance request")
            elif choice == "5":
                self.logout()
                break
            else:
                print("Invalid choice")

    def student_menu(self):
        while True:
            print("\nStudent Menu")
            print("1. View Profile")
            print("2. Edit Profile")
            print("3. View Room")
            print("4. Create Maintenance Request")
            print("5. View Maintenance Requests")
            print("6. View Payments")
            print("7. Logout")
            choice = input("Enter your choice: ")

            if choice == "1":
                print(f"ID: {self.current_user.student_id}")
                print(f"Name: {self.current_user.username}")
                print(f"Contact Info: {self.current_user.contact_info}")
                print(f"Gender: {self.current_user.gender}")
                print(f"Department: {self.current_user.department}")
                print(f"Year: {self.current_user.year}")
            elif choice == "2":
                contact_info = input("Enter new contact info (or press enter to skip): ")
                gender = input("Enter new gender (or press enter to skip): ")
                department = input("Enter new department (or press enter to skip): ")
                year = input("Enter new year (or press enter to skip): ")
                self.current_user.edit_profile(contact_info, gender, department, year)
                self.data_manager.update_data('users', self.current_user.student_id, 
                                              self.current_user.__dict__)
                print("Profile updated successfully")
            elif choice == "3":
                if self.current_user.room:
                    print(f"Room Number: {self.current_user.room.room_number}")
                    print(f"Capacity: {self.current_user.room.capacity}")
                    print(f"Occupants: {len(self.current_user.room.occupants)}")
                else:
                    print("You are not allocated to a room yet")
            elif choice == "4":
                description = input("Enter maintenance request description: ")
                request = self.create_maintenance_request(description)
                if request:
                    print("Maintenance request created successfully")
                else:
                    print("Failed to create maintenance request")
            elif choice == "5":
                for request in self.maintenance_requests:
                    if request.student == self.current_user:
                        print(f"ID: {request.id}, Description: {request.description}, "
                              f"Status: {request.status}")
            elif choice == "6":
                for payment in self.payments:
                    if payment.student == self.current_user:
                        print(f"Amount: {payment.amount}, Due Date: {payment.due_date}, "
                              f"Paid: {payment.paid}")
            elif choice == "7":
                self.logout()
                break
            else:
                print("Invalid choice")
