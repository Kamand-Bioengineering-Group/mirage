"""
XPECTO Epidemic 2.0 Competition System
"""
from .competition_manager import CompetitionManager
from .data.enhanced_storage import EnhancedLocalStorageProvider

# Import testing utilities
from .testing.engine_adapter import MockEngine

# For testing purposes, we can optionally replace EngineV1 with our MockEngine
import importlib.util
import sys

# Setup patch for EngineV1
def setup_testing_mode():
    """
    Setup testing mode by patching EngineV1 with MockEngine.
    This is useful for testing without the full engine requirements.
    """
    import sys
    
    # Create a mock module for src.mirage.engines.base
    from types import ModuleType
    mock_module = ModuleType('src.mirage.engines.base')
    setattr(mock_module, 'EngineV1', MockEngine)
    
    # Add the mock module to sys.modules
    sys.modules['src.mirage.engines.base'] = mock_module
    
    print("Testing mode enabled: EngineV1 replaced with MockEngine")
    return True

# Check if we're in a test environment
def is_in_test_environment():
    """Check if we're in a test environment (like notebooks)."""
    return 'ipykernel' in sys.modules

# Auto-setup testing mode if in notebook
if is_in_test_environment():
    setup_testing_mode()

__all__ = ['CompetitionManager', 'EnhancedLocalStorageProvider', 'MockEngine', 'setup_testing_mode'] 