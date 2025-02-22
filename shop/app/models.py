from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser

type_choices = (
    ('owner', 'Owner'),
    ('customer', 'Customer'),
)

class User(AbstractUser):
    user_type = models.CharField(max_length=10, choices=type_choices, default='customer')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2,default=100)  # Min balance 1000,default=1000
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True
    )

    def add_money(self, amount):
        self.wallet_balance += amount
        self.save()
    
    def spend_money(self, amount):
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            self.save()
            return True
        return False

    def earn_money(self, amount):
        self.total_earned += amount
        self.wallet_balance += amount
        self.save()


# Company Wallet Model
class CompanyWallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @classmethod
    def add_commission(cls, amount):
        company_wallet, created = cls.objects.get_or_create(id=1)  # Ensure a single wallet exists
        company_wallet.balance += amount
        company_wallet.save()

    def __str__(self):
        return f"Company Wallet Balance: {self.balance}"


# Product Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    total_sales = models.PositiveIntegerField(default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'owner'})
    created_at = models.DateTimeField(auto_now_add=True)
    sales_count = models.PositiveIntegerField(default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


# Sales Model (Includes Commission Logic)
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    COMMISSION_RATE = 0.05  # 5% commission to the company

    def save(self, *args, **kwargs):
        commission = self.amount * self.COMMISSION_RATE  # Calculate commission
        seller_earnings = self.amount - commission  # Amount after commission

        if self.customer.spend_money(self.amount):
            self.product.sales_count += 1
            self.product.total_earned += seller_earnings
            self.product.owner.earn_money(seller_earnings)

            # Update category earnings and sales count
            self.product.category.total_sales += 1
            self.product.category.total_earned += seller_earnings

            # Add commission to company wallet
            CompanyWallet.add_commission(commission)

            # Save all updates
            self.product.save()
            self.product.category.save()
            self.product.owner.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Insufficient funds")


# Screen Time Tracking
class ScreenTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0)  # in seconds
    last_active = models.DateTimeField(default=now)

    def update_time(self, duration):
        self.time_spent += duration
        self.last_active = now()
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.category.name if self.category else 'Overall'} - {self.product.name if self.product else 'General'}: {self.time_spent}s"


# Owner Dashboard Stats
class OwnerStats(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'owner'})
    daily_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    yearly_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_earnings(self, amount):
        self.daily_earnings += amount
        self.monthly_earnings += amount
        self.yearly_earnings += amount
        self.save()
