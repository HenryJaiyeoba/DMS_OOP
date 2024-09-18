class Payment:
    def __init__(self, student, amount, due_date):
        self.student = student
        self.amount = amount
        self.due_date = due_date
        self.paid = False

    def mark_as_paid(self):
        self.paid = True
