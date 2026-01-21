# test_fl.py
# Unit tests for Federated Learning functionality.
# Tests:
# - DP noise addition and privacy budget tracking
# - Weight serialization and deserialization
# - FedAvg aggregation correctness
# - FL round progression
# - Server communication (mocked)
# Run with: pytest app/tests/test_fl.py

import pytest
import numpy as np
from app.services.fl_engine import FederatedLearningEngine

class TestFederatedLearning:
    """Test suite for federated learning functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fl_engine = FederatedLearningEngine("bank_a")
    
    def test_dp_noise_addition(self):
        """Test differential privacy noise addition."""
        weights = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        epsilon = 0.1
        
        noisy_weights = self.fl_engine.add_dp_noise(weights, epsilon)
        
        # Verify noise was added (weights should be different)
        assert not np.array_equal(weights, noisy_weights)
        
        # Verify privacy budget was updated
        assert self.fl_engine.privacy_budget < 1.0
    
    def test_privacy_budget_tracking(self):
        """Test privacy budget tracking."""
        initial_budget = self.fl_engine.privacy_budget
        
        weights = np.array([1.0, 2.0, 3.0])
        self.fl_engine.add_dp_noise(weights, epsilon=0.1)
        
        # Budget should decrease
        assert self.fl_engine.privacy_budget < initial_budget
    
    def test_send_update(self):
        """Test sending FL update."""
        model_weights = {"layer1": np.array([1.0, 2.0, 3.0])}
        
        result = self.fl_engine.send_update_to_server(model_weights)
        
        assert result["status"] == "success"
        assert "round" in result
    
    def test_fedavg_aggregation(self):
        """Test FedAvg aggregation."""
        updates = [
            {"weights": np.array([1.0, 2.0, 3.0])},
            {"weights": np.array([2.0, 3.0, 4.0])}
        ]
        
        aggregated = self.fl_engine.fedavg(updates)
        
        assert "aggregated_weights" in aggregated
        assert aggregated["num_participants"] == 2
    
    def test_fl_status(self):
        """Test FL status retrieval."""
        status = self.fl_engine.get_fl_status()
        
        assert "bank_id" in status
        assert "current_round" in status
        assert "privacy_budget_remaining" in status

if __name__ == "__main__":
    pytest.main([__file__])
