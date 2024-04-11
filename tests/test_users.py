from django.test import TestCase
from users.models import User, Cashier, Consultant, Booker


class UserTestCase(TestCase):
    def test_user_role_default(self):
        user = User.objects.create(username="testuser")
        self.assertEqual(user.role, User.Role.USER)

    def test_cashier_welcome_message(self):
        cashier = Cashier.objects.create(username="cashier")
        self.assertEqual(cashier.welcome(), "Only for Cashiers")

    def test_consultant_welcome_message(self):
        consultant = Consultant.objects.create(username="consultant")
        self.assertEqual(consultant.welcome(), "Only for consultants")

    def test_booker_welcome_message(self):
        booker = Booker.objects.create(username="booker")
        self.assertEqual(booker.welcome(), "Only for bookers")


class ManagerTestCase(TestCase):
    def test_cashier_manager(self):
        cashier1 = Cashier.objects.create(username="cashier1")
        cashier2 = Cashier.objects.create(username="cashier2")
        self.assertEqual(list(Cashier.cashier.all()), [cashier1, cashier2])

    def test_consultant_manager(self):
        consultant1 = Consultant.objects.create(username="consultant1")
        consultant2 = Consultant.objects.create(username="consultant2")
        self.assertEqual(list(Consultant.consultant.all()), [consultant1, consultant2])

    def test_booker_manager(self):
        booker1 = Booker.objects.create(username="booker1")
        booker2 = Booker.objects.create(username="booker2")
        self.assertEqual(list(Booker.booker.all()), [booker1, booker2])
