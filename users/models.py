from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Avoids conflicts
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Avoids conflicts
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class Service(models.Model):
    CATEGORY_CHOICES = (
        ('auto_repair', 'Auto Repair'),
        ('auto_body', 'Auto Body'),
        ('auto_detailing', 'Auto Detailing'),
        ('tire_services', 'Tire Services'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.category} - {self.name}"


# MechanicProfile (For Users Acting as Mechanics)
class MechanicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mechanic_profile")
    services = models.ManyToManyField('Service')
    operation_hours = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    experience = models.IntegerField()
    is_mobile = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

# CustomerProfile (For Users Acting as Customers)
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    vehicle_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.email

class QuoteRequest(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='quote_requests')
    services = models.ManyToManyField(Service)  # Allowing the customer to select multiple services
    vehicle_info = models.CharField(max_length=255)
    preferred_time = models.DateTimeField()
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quote {self.id} - {self.customer.user.email}"


class Estimate(models.Model):
    quote_request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name='estimates')
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE)
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    service_time_estimate = models.CharField(max_length=50)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estimate {self.id} - {self.mechanic.user.email}"

class Appointment(models.Model):
    estimate = models.OneToOneField(Estimate, on_delete=models.CASCADE, related_name='appointment')
    appointment_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='scheduled')

    def __str__(self):
        return f"Appointment {self.id} for {self.estimate.mechanic.user.email}"

class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    payment_method = models.CharField(max_length=50)  # e.g., credit card, cash, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment.id}"
