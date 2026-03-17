from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model to handle Roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('partner_admin', 'Partner Admin'),
        ('contractor', 'Contractor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='contractor')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

# 2. Tender Model
class Tender(models.Model):
    CATEGORY_CHOICES = (
        ('construction', 'Construction'),
        ('electrical', 'Electrical'),
        ('consultancy', 'Consultancy'),
        ('transport', 'Transport'),
        ('medical', 'Medical Supply'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft (Pending)'),
        ('active', 'Active (Live)'),
        ('closed', 'Closed'),
        ('awarded', 'Awarded'),
    )

    title = models.CharField(max_length=200)
    # The partner company who posted this
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenders')
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    
    budget = models.DecimalField(max_digits=15, decimal_places=2)  # up to 9 Trillion
    location = models.CharField(max_length=100)
    
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Document Upload (Simulated path for now or real usage)
    document = models.FileField(upload_to='tender_docs/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

# 3. Bid Application Model
class Bid(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bid_set')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_bids')
    
    bid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    proposal_text = models.TextField()
    proposal_document = models.FileField(upload_to='bid_docs/', blank=True, null=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Status of the application
    status = models.CharField(max_length=20, default='pending', choices=(
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ))

    def __str__(self):
        return f"{self.bidder.username} -> {self.tender.title}"

# 4. Favorite/Archive Model
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only favorite a tender once
        unique_together = ('user', 'tender')

    def __str__(self):
        return f"{self.user.username} favorited {self.tender.title}"
