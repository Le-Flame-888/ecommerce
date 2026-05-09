from django.test import TestCase
from django.utils import timezone
from .models import Coupon
from datetime import timedelta

class CouponModelTests(TestCase):
    def test_coupon_validity(self):
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='SAVE10',
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
            discount=10,
            active=True
        )
        self.assertEqual(str(coupon), 'SAVE10')
        self.assertTrue(coupon.active)
        self.assertLess(coupon.valid_from, now)
        self.assertGreater(coupon.valid_to, now)
