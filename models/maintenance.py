import uuid
from datetime import datetime

class MaintenanceRequest:
    def __init__(self, student, description):
        self.id = str(uuid.uuid4())
        self.student = student
        self.description = description
        self.status = "Pending"
        self.created_at = datetime.now()

    def update_status(self, new_status):
        self.status = new_status