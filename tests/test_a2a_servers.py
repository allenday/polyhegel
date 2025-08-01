"""
Tests for A2A server applications

Tests server creation, configuration, and basic functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from polyhegel.servers import create_leader_server, create_follower_server
from polyhegel.strategic_techniques import StrategyDomain


class TestA2AServerCreation:
    """Test A2A server application creation"""

    @patch("polyhegel.servers.leader_server.ModelManager")
    def test_leader_server_creation(self, mock_model_manager):
        """Test leader server creation with default configuration"""
        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        server = create_leader_server(host="127.0.0.1", port=9001, model_name="claude-3-haiku-20240307", max_themes=3)

        # Verify server was created
        assert server is not None

        # Verify model manager was called correctly
        mock_model_manager.return_value.get_model.assert_called_once_with("claude-3-haiku-20240307")

    @patch("polyhegel.servers.follower_server.ModelManager")
    def test_follower_server_creation(self, mock_model_manager):
        """Test follower server creation with specialization"""
        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        server = create_follower_server(
            host="127.0.0.1",
            port=9002,
            model_name="claude-3-haiku-20240307",
            specialization_domain=StrategyDomain.RESOURCE_ACQUISITION,
        )

        # Verify server was created
        assert server is not None

        # Verify model manager was called correctly
        mock_model_manager.return_value.get_model.assert_called_once_with("claude-3-haiku-20240307")

    @patch("polyhegel.servers.follower_server.ModelManager")
    def test_general_follower_server_creation(self, mock_model_manager):
        """Test general follower server creation without specialization"""
        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        server = create_follower_server(
            host="127.0.0.1",
            port=9003,
            model_name="claude-3-haiku-20240307",
            specialization_domain=None,  # General agent
        )

        # Verify server was created
        assert server is not None

        # Verify model manager was called correctly
        mock_model_manager.return_value.get_model.assert_called_once_with("claude-3-haiku-20240307")

    def test_server_configuration_validation(self):
        """Test server configuration validation"""
        # Test with various domain configurations
        domains_to_test = [
            StrategyDomain.RESOURCE_ACQUISITION,
            StrategyDomain.STRATEGIC_SECURITY,
            StrategyDomain.VALUE_CATALYSIS,
            None,  # General
        ]

        with patch("polyhegel.servers.follower_server.ModelManager") as mock_model_manager:
            mock_model = MagicMock()
            mock_model_manager.return_value.get_model.return_value = mock_model

            for domain in domains_to_test:
                server = create_follower_server(specialization_domain=domain)
                assert server is not None


class TestA2AServerIntegration:
    """Integration tests for A2A servers"""

    @pytest.mark.asyncio
    @patch("polyhegel.servers.leader_server.ModelManager")
    async def test_leader_server_agent_card(self, mock_model_manager):
        """Test that leader server creates valid agent card"""
        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        server = create_leader_server(host="localhost", port=8001, model_name="claude-3-haiku-20240307")

        # The server should have an agent card
        app = server.build()

        # Verify the server app was built successfully
        assert app is not None

    @pytest.mark.asyncio
    @patch("polyhegel.servers.follower_server.ModelManager")
    async def test_follower_server_agent_card(self, mock_model_manager):
        """Test that follower server creates valid agent card"""
        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        server = create_follower_server(
            host="localhost",
            port=8002,
            model_name="claude-3-haiku-20240307",
            specialization_domain=StrategyDomain.STRATEGIC_SECURITY,
        )

        # The server should have an agent card
        app = server.build()

        # Verify the server app was built successfully
        assert app is not None


class TestServerEnvironmentConfiguration:
    """Test server configuration from environment variables"""

    @patch.dict(
        "os.environ",
        {
            "POLYHEGEL_LEADER_HOST": "0.0.0.0",
            "POLYHEGEL_LEADER_PORT": "7001",
            "POLYHEGEL_LEADER_MODEL": "claude-3-sonnet-20240229",
            "POLYHEGEL_MAX_THEMES": "7",
        },
    )
    @patch("polyhegel.servers.leader_server.ModelManager")
    def test_leader_server_env_config(self, mock_model_manager):
        """Test leader server configuration from environment"""
        # Import after setting environment variables
        from polyhegel.servers.leader_server import main

        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        # Mock uvicorn.run to prevent actual server startup
        with patch("polyhegel.servers.leader_server.uvicorn.run"):
            with patch("polyhegel.servers.leader_server.create_leader_server") as mock_create_server:
                mock_server = MagicMock()
                mock_create_server.return_value = mock_server
                mock_server.build.return_value = MagicMock()

                # This would normally start the server, but we're mocking it
                try:
                    main()
                except SystemExit:
                    pass  # Expected when mocking

                # Verify server was created with env config
                mock_create_server.assert_called_once_with(
                    host="0.0.0.0",
                    port=7001,
                    model_name="claude-3-sonnet-20240229",
                    focus_domains=[],
                    max_themes=7,
                    enable_auth=True,
                )

    @patch.dict(
        "os.environ",
        {
            "POLYHEGEL_FOLLOWER_HOST": "127.0.0.1",
            "POLYHEGEL_FOLLOWER_PORT": "7002",
            "POLYHEGEL_FOLLOWER_MODEL": "claude-3-opus-20240229",
            "POLYHEGEL_SPECIALIZATION_DOMAIN": "value_catalysis",
        },
    )
    @patch("polyhegel.servers.follower_server.ModelManager")
    def test_follower_server_env_config(self, mock_model_manager):
        """Test follower server configuration from environment"""
        # Import after setting environment variables
        from polyhegel.servers.follower_server import main

        # Mock model manager
        mock_model = MagicMock()
        mock_model_manager.return_value.get_model.return_value = mock_model

        # Mock uvicorn.run to prevent actual server startup
        with patch("polyhegel.servers.follower_server.uvicorn.run"):
            with patch("polyhegel.servers.follower_server.create_follower_server") as mock_create_server:
                mock_server = MagicMock()
                mock_create_server.return_value = mock_server
                mock_server.build.return_value = MagicMock()

                # This would normally start the server, but we're mocking it
                try:
                    main()
                except SystemExit:
                    pass  # Expected when mocking

                # Verify server was created with env config
                mock_create_server.assert_called_once_with(
                    host="127.0.0.1",
                    port=7002,
                    model_name="claude-3-opus-20240229",
                    specialization_domain=StrategyDomain.VALUE_CATALYSIS,
                )


if __name__ == "__main__":
    pytest.main([__file__])
