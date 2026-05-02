import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_project.settings')
django.setup()

# Test the email function
from orders.emails import send_order_confirmation_email
from orders.models import Order

# Create a test order (you would normally get this from your database)
# This is just to verify the function imports correctly
print("Email function imported successfully!")
print("To test with actual data, you would need to:")
print("1. Create an order in the database")
print("2. Call send_order_confirmation_email(order)")
print("3. Check console output (since we're using console backend)")