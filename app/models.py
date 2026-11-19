from django.db import models


CATEGORY_CHOICES = [
    # Income categories
    ('salary', 'Salary'),
    ('freelance', 'Freelance'),
    ('business', 'Business'),
    ('investment', 'Investment'),
    ('gift', 'Gift'),
    ('other_income', 'Other Income'),
    # Expense categories
    ('food', 'Food & Dining'),
    ('transport', 'Transport'),
    ('rent', 'Rent & Housing'),
    ('utilities', 'Utilities'),
    ('shopping', 'Shopping'),
    ('health', 'Health & Medical'),
    ('education', 'Education'),
    ('entertainment', 'Entertainment'),
    ('other_expense', 'Other Expense'),
]


class Transaction(models.Model):
    TYPE_CHOICES = [('income', 'Income'), ('expense', 'Expense')]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, blank=True)
    note = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type} - {self.title} - {self.amount}"