"""
Tests for database seeding functionality.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.core.seed_data import seed_database
from app.models.user import User


class TestSeedDatabase:
    """Tests for seed_database function."""

    def test_seed_database_creates_users_when_empty(self):
        """Test that seed_database creates admin and demo users when database is empty."""
        # Mock SessionLocal
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        
        MockSessionLocal = MagicMock(return_value=mock_session)
        
        # Call seed_database
        seed_database(MockSessionLocal)
        
        # Verify users were added
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_seed_database_skips_when_users_exist(self):
        """Test that seed_database skips seeding when users already exist."""
        # Mock SessionLocal with existing users
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 5
        
        MockSessionLocal = MagicMock(return_value=mock_session)
        
        # Call seed_database
        seed_database(MockSessionLocal)
        
        # Verify no users were added
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
        mock_session.close.assert_called_once()

    def test_seed_database_handles_error(self):
        """Test that seed_database handles errors gracefully."""
        # Mock SessionLocal that raises an error
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        mock_session.commit.side_effect = Exception("Database error")
        
        MockSessionLocal = MagicMock(return_value=mock_session)
        
        # Call seed_database and expect exception
        with pytest.raises(Exception, match="Database error"):
            seed_database(MockSessionLocal)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_seed_database_creates_correct_user_data(self):
        """Test that seed_database creates users with correct data."""
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        
        MockSessionLocal = MagicMock(return_value=mock_session)
        
        # Call seed_database
        seed_database(MockSessionLocal)
        
        # Get the users that were added
        add_calls = mock_session.add.call_args_list
        assert len(add_calls) == 2
        
        # First user should be admin
        admin_user = add_calls[0][0][0]
        assert admin_user.username == "admin"
        assert admin_user.is_admin is True
        assert admin_user.is_active is True
        
        # Second user should be demo
        demo_user = add_calls[1][0][0]
        assert demo_user.username == "demo"
        assert demo_user.is_admin is False
        assert demo_user.is_active is True
