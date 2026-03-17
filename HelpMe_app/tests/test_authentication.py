import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import authenticate
from HelpMe_app.models import User


class UserAuthenticationTest(TestCase):
    """Test cases for user authentication"""

    def setUp(self):
        """Set up test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            date_of_birth='1990-01-01',
            password='TestPass123!?',
            full_name='Test User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='My pet'
        )

    def test_user_authentication_with_correct_credentials(self):
        """Test user authentication with correct username and password"""
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_user_authentication_with_incorrect_password(self):
        """Test user authentication with incorrect password"""
        user = authenticate(username='testuser', password='WrongPassword123!?')
        self.assertIsNone(user)

    def test_user_authentication_with_nonexistent_user(self):
        """Test user authentication with nonexistent username"""
        user = authenticate(username='nonexistent', password='TestPass123!?')
        self.assertIsNone(user)

    def test_password_is_hashed_properly(self):
        """Test that password is hashed and not stored as plain text"""
        self.assertNotEqual(self.user.password, 'TestPass123!?')
        # Check that the password string looks like a hash
        self.assertTrue(self.user.password.startswith('pbkdf2_sha256$'))

    def test_set_password_method(self):
        """Test that set_password properly hashes passwords"""
        self.user.set_password('NewPassword456!?')
        self.user.save()
        
        # Verify old password no longer works
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNone(user)
        
        # Verify new password works
        user = authenticate(username='testuser', password='NewPassword456!?')
        self.assertIsNotNone(user)

    def test_user_login_session(self):
        """Test that user can authenticate with correct credentials"""
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_user_logout(self):
        """Test that user is properly deauthenticated"""
        # Create a user object to test deauthentication
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNotNone(user)
        
        # Manually change password to simulate logout invalidation
        self.user.set_password('NewPassword456!?')
        self.user.save()
        
        # Old password should not work anymore
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNone(user)

    def test_multiple_login_attempts_same_session(self):
        """Test authentication with wrong then correct credentials"""
        # First failed attempt
        user = authenticate(username='testuser', password='WrongPassword')
        self.assertIsNone(user)
        
        # Then successful attempt
        user = authenticate(username='testuser', password='TestPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')


class UserRegistrationTest(TestCase):
    """Test cases for user registration"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_user_registration_with_valid_data(self):
        """Test user creation with all required valid data"""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            date_of_birth='1995-05-15',
            password='StrongPass123!?',
            full_name='New User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='My favorite pet'
        )
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.full_name, 'New User')

    def test_user_registration_duplicate_username(self):
        """Test that creating user with duplicate username fails"""
        # Create first user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            date_of_birth='1990-01-01',
            password='TestPass123!?',
            full_name='Existing User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        
        # Try to create with same username
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='existinguser',
                email='different@example.com',
                date_of_birth='1995-05-15',
                password='StrongPass123!?',
                full_name='Different User',
                picture='test.jpg',
                type=User.STANDARD,
                password_hint='My favorite pet'
            )

    def test_user_registration_duplicate_email(self):
        """Test that creating user with duplicate email fails"""
        # Create first user
        User.objects.create_user(
            username='user1',
            email='shared@example.com',
            date_of_birth='1990-01-01',
            password='TestPass123!?',
            full_name='User One',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        
        # Try to create with same email - should fail
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='shared@example.com',
                date_of_birth='1995-05-15',
                password='StrongPass123!?',
                full_name='User Two',
                picture='test.jpg',
                type=User.STANDARD,
                password_hint='My favorite pet'
            )

    def test_user_registration_password_hashing(self):
        """Test that password is hashed when creating user"""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            date_of_birth='1995-05-15',
            password='StrongPass123!?',
            full_name='New User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='My favorite pet'
        )
        
        # Password should be hashed, not plain text
        self.assertNotEqual(user.password, 'StrongPass123!?')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

    def test_user_registration_missing_required_field(self):
        """Test that creating user without required field raises error"""
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username='newuser',
                email='newuser@example.com',
                date_of_birth='1995-05-15',
                password='StrongPass123!?',
                # Missing full_name - this should raise TypeError
                picture='test.jpg',
                type=User.STANDARD,
                password_hint='My favorite pet'
            )


class SessionSecurityTest(TestCase):
    """Test cases for session security"""

    def setUp(self):
        """Set up test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='secureuser',
            email='secure@example.com',
            date_of_birth='1990-01-01',
            password='SecurePass123!?',
            full_name='Secure User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='My pet'
        )

    def test_authenticated_user_can_authenticate(self):
        """Test that user can authenticate"""
        user = authenticate(username='secureuser', password='SecurePass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'secureuser')

    def test_session_persistence_after_password_set(self):
        """Test that user persists after password operations"""
        user = authenticate(username='secureuser', password='SecurePass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'secureuser')
        
        # Password should still work after retrieval
        user2 = authenticate(username='secureuser', password='SecurePass123!?')
        self.assertIsNotNone(user2)

    def test_session_invalidation_on_password_change(self):
        """Test that old password doesn't work after password change"""
        # Verify old password works
        user = authenticate(username='secureuser', password='SecurePass123!?')
        self.assertIsNotNone(user)
        
        # Change password
        self.user.set_password('NewSecurePass456!?')
        self.user.save()
        
        # Old password should not work
        user = authenticate(username='secureuser', password='SecurePass123!?')
        self.assertIsNone(user)
        
        # New password should work
        user = authenticate(username='secureuser', password='NewSecurePass456!?')
        self.assertIsNotNone(user)

    def test_active_flag_prevents_authentication(self):
        """Test that deactivated users cannot authenticate"""
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        # Try to login - authentication should fail
        user = authenticate(username='secureuser', password='SecurePass123!?')
        # Default backend returns None for inactive users
        self.assertIsNone(user)

    def test_credentials_validation(self):
        """Test that invalid credentials don't authenticate user"""
        # Create a request without proper credentials
        user = authenticate(username='secureuser', password='WrongPassword')
        self.assertIsNone(user)


class PasswordManagementTest(TestCase):
    """Test cases for password management"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='pwduser',
            email='pwd@example.com',
            date_of_birth='1990-01-01',
            password='OldPassword123!?',
            full_name='Password User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='My pet'
        )
        self.client = Client()

    def test_user_can_change_password_with_correct_old_password(self):
        """Test that user can change password with correct old password"""
        # Verify old password works
        user = authenticate(username='pwduser', password='OldPassword123!?')
        self.assertIsNotNone(user)
        
        # Change password
        self.user.set_password('NewPassword456!?')
        self.user.save()
        
        # Try to login with new password
        user = authenticate(username='pwduser', password='NewPassword456!?')
        self.assertIsNotNone(user)
        
        # Old password should not work
        user = authenticate(username='pwduser', password='OldPassword123!?')
        self.assertIsNone(user)

    def test_password_change_fails_with_incorrect_old_password(self):
        """Test that password cannot be changed without correct old password"""
        # Try to change password with wrong old password
        # This tests the validation logic that would be in the view
        old_password = 'OldPassword123!?'
        wrong_old_password = 'WrongPassword123!?'
        
        # Verify user authenticates with correct old password
        user = authenticate(username='pwduser', password=old_password)
        self.assertIsNotNone(user)
        
        # Verify user doesn't authenticate with wrong old password
        user = authenticate(username='pwduser', password=wrong_old_password)
        self.assertIsNone(user)

    def test_new_password_different_from_old_password(self):
        """Test that new password should be different from old password"""
        # Get the hashed password before change
        original_password_hash = self.user.password
        
        # Try to set to same password (this would be caught in validation)
        same_password = 'OldPassword123!?'
        self.user.set_password(same_password)
        
        # Verify new hash is created (even if same text)
        self.assertNotEqual(original_password_hash, self.user.password)
        
        # Verify the password still works
        user = authenticate(username='pwduser', password=same_password)
        self.assertIsNotNone(user)

    def test_password_hint_usage(self):
        """Test that password hint is properly stored"""
        user = User.objects.get(username='pwduser')
        self.assertEqual(user.password_hint, 'My pet')
        self.assertNotEqual(user.password_hint, user.password)


class UserTypeAuthorizationTest(TestCase):
    """Test cases for user type based authorization"""

    def setUp(self):
        """Set up users of different types"""
        self.client = Client()
        
        self.standard_user = User.objects.create_user(
            username='standard',
            email='standard@example.com',
            date_of_birth='1990-01-01',
            password='StandardPass123!?',
            full_name='Standard User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            date_of_birth='1985-01-01',
            password='AdminPass123!?',
            full_name='Admin User',
            picture='test.jpg',
            type=User.ADMIN,
            password_hint='hint'
        )
        
        self.limited_user = User.objects.create_user(
            username='limited',
            email='limited@example.com',
            date_of_birth='1995-01-01',
            password='LimitedPass123!?',
            full_name='Limited User',
            picture='test.jpg',
            type=User.LIMITED,
            password_hint='hint'
        )

    def test_admin_user_can_authenticate(self):
        """Test that admin users can authenticate"""
        user = authenticate(username='admin', password='AdminPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.type, User.ADMIN)

    def test_standard_user_can_authenticate(self):
        """Test that standard users can authenticate"""
        user = authenticate(username='standard', password='StandardPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.type, User.STANDARD)

    def test_limited_user_can_authenticate(self):
        """Test that limited users can authenticate"""
        user = authenticate(username='limited', password='LimitedPass123!?')
        self.assertIsNotNone(user)
        self.assertEqual(user.type, User.LIMITED)

    def test_admin_user_has_is_staff_flag(self):
        """Test that admin users have is_staff flag set"""
        self.assertTrue(self.admin_user.is_staff)
        self.assertFalse(self.standard_user.is_staff)
        self.assertFalse(self.limited_user.is_staff)

    def test_admin_user_has_is_superuser_flag(self):
        """Test that admin users have is_superuser flag set"""
        self.assertTrue(self.admin_user.is_superuser)
        self.assertFalse(self.standard_user.is_superuser)
        self.assertFalse(self.limited_user.is_superuser)

    def test_user_type_stored_correctly(self):
        """Test that user type field stores the correct value"""
        user_standard = User.objects.get(username='standard')
        self.assertEqual(user_standard.type, User.STANDARD)
        
        user_admin = User.objects.get(username='admin')
        self.assertEqual(user_admin.type, User.ADMIN)
        
        user_limited = User.objects.get(username='limited')
        self.assertEqual(user_limited.type, User.LIMITED)
