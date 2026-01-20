// StaffModelTraining.jsx
// Controls local model training and FL participation for this bank.
// Implements: Train → Upload to Server → Poll for New Model → Auto-Download
// Shows real-time FL status and automatic model updates.

import React, { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const StaffModelTraining = () => {
  // Training state
  const [trainingStatus, setTrainingStatus] = useState('idle'); // idle, training, completed, error
  const [trainingOutput, setTrainingOutput] = useState('');
  
  // FL status state
  const [flStatus, setFlStatus] = useState(null);
  const [modelUpdateAvailable, setModelUpdateAvailable] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  
  // Local model state
  const [localModelInfo, setLocalModelInfo] = useState(null);
  const [downloadingModel, setDownloadingModel] = useState(false);
  
  // Model selection state
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [activeModelName, setActiveModelName] = useState('');
  
  // Error state
  const [error, setError] = useState(null);

  // New applications count
  const [newApplicationsCount, setNewApplicationsCount] = useState(0);

  // Refs for cleanup
  const pollIntervalRef = useRef(null);

  // Fetch available models
  const fetchAvailableModels = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/list-models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models || []);
        setActiveModelName(data.active_model || 'Base Model');
      }
    } catch (err) {
      console.error('Failed to fetch models:', err);
    }
  }, []);

  // Fetch FL status from server
  const fetchFLStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/fl-status`);
      if (response.ok) {
        const data = await response.json();
        setFlStatus(data);
        setError(null);
      }
    } catch (err) {
      console.error('Failed to fetch FL status:', err);
    }
  }, []);

  // Fetch local model info
  const fetchLocalModelInfo = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/local-model-info`);
      if (response.ok) {
        const data = await response.json();
        setLocalModelInfo(data);
      }
    } catch (err) {
      console.error('Failed to fetch local model info:', err);
    }
  }, []);

  // Fetch new applications count
  const fetchNewApplicationsCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/staff/applications/count`);
      if (response.ok) {
        const data = await response.json();
        setNewApplicationsCount(data.count || 0);
      }
    } catch (err) {
      console.error('Failed to fetch new applications count:', err);
    }
  }, []);

  // Download and activate new model
  const downloadAndActivateModel = useCallback(async () => {
    setDownloadingModel(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/download-and-activate`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('New model activated:', data);
        setModelUpdateAvailable(false);
        await fetchLocalModelInfo();
        await fetchFLStatus();
        
        // Show success notification
        setTrainingOutput(prev => 
          prev + `\n\n✅ NEW MODEL ACTIVATED (Round ${data.round})\nSize: ${data.size_mb.toFixed(2)} MB`
        );
      }
    } catch (err) {
      console.error('Failed to download model:', err);
      setError('Failed to download new model');
    } finally {
      setDownloadingModel(false);
    }
  }, [fetchLocalModelInfo, fetchFLStatus]);

  // Check for model updates
  const checkForModelUpdate = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/check-model-update`);
      if (response.ok) {
        const data = await response.json();
        
        if (data.has_new_model) {
          setModelUpdateAvailable(true);
          // Auto-download new model
          await downloadAndActivateModel();
        }
        
        return data;
      }
    } catch (err) {
      console.error('Failed to check for model update:', err);
    }
    return null;
  }, [downloadAndActivateModel]);

  // Start polling for model updates
  const startPolling = useCallback(() => {
    if (pollIntervalRef.current) return;
    
    setIsPolling(true);
    console.log('Started polling for model updates...');
    
    // Poll every 5 seconds
    pollIntervalRef.current = setInterval(async () => {
      await checkForModelUpdate();
      await fetchFLStatus();
    }, 5000);
  }, [checkForModelUpdate, fetchFLStatus]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setIsPolling(false);
    console.log('Stopped polling for model updates');
  }, []);

  // Train local model
  const handleTrainLocal = async () => {
    setTrainingStatus('training');
    setTrainingOutput('Starting FL training...\n');
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/train`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bank_id: 'bank_a',
          epochs: 10,
          batch_size: 256,
          learning_rate: 0.001
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setTrainingStatus('completed');

        const mergedMsg = data.merged_applications > 0
          ? `\n${data.merged_applications} new applications merged into training dataset.\n`
          : '';

        setTrainingOutput(prev =>
          prev + `\n✅ Training Complete!\n` +
          `Bank: ${data.bank_id}\n` +
          `Epochs: ${data.epochs}\n` +
          `Status: ${data.status}\n` +
          mergedMsg +
          `\nWeights uploaded to FL server.\n` +
          `Waiting for other banks to complete training...\n\n` +
          `Output:\n${data.output || 'No output'}`
        );

        // Start polling for aggregated model
        startPolling();

        // Refresh status and application count
        await fetchFLStatus();
        await fetchLocalModelInfo();
        await fetchNewApplicationsCount();
      } else {
        const errorData = await response.json();
        setTrainingStatus('error');
        setTrainingOutput(prev => prev + `\n❌ Training Failed: ${errorData.detail || 'Unknown error'}`);
        setError(errorData.detail || 'Training failed');
      }
    } catch (err) {
      setTrainingStatus('error');
      setTrainingOutput(prev => prev + `\n❌ Error: ${err.message}`);
      setError(err.message);
    }
  };

  // Manual download trigger
  const handleManualDownload = async () => {
    await downloadAndActivateModel();
  };

  // Switch model
  const handleSwitchModel = async (modelId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/fl/switch-model?model_id=${modelId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const data = await response.json();
        setActiveModelName(data.active_model);
        await fetchLocalModelInfo();
        await fetchAvailableModels();
        alert(`✅ Switched to ${data.active_model}`);
      }
    } catch (err) {
      console.error('Failed to switch model:', err);
      alert('Failed to switch model');
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchFLStatus();
    fetchLocalModelInfo();
    fetchAvailableModels();
    fetchNewApplicationsCount();

    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [fetchFLStatus, fetchLocalModelInfo, fetchAvailableModels, fetchNewApplicationsCount, stopPolling]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Model Training & Federated Learning</h1>
        
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="grid gap-6">
          {/* FL Server Status */}
          <div className="card bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">FL Server Status</h2>
              <div className="flex items-center gap-2">
                {isPolling && (
                  <span className="text-sm text-green-600 flex items-center gap-1">
                    <span className="animate-pulse">●</span> Listening for updates
                  </span>
                )}
                <button 
                  onClick={fetchFLStatus}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Refresh
                </button>
              </div>
            </div>
            
            {flStatus ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <p className="text-xl font-bold text-green-600">{flStatus.status}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Current Round</p>
                  <p className="text-xl font-bold">{flStatus.current_round}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Pending Banks</p>
                  <p className="text-xl font-bold">{flStatus.clients_connected}/{flStatus.aggregation_threshold}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Aggregations</p>
                  <p className="text-xl font-bold">{flStatus.total_aggregations}</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Connecting to FL server...</p>
            )}
            
            {flStatus?.pending_updates?.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">Waiting for banks:</p>
                <div className="flex gap-2 mt-2">
                  {flStatus.pending_updates.map((bank, i) => (
                    <span key={i} className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                      {bank}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Local Model Info */}
          <div className="card bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Local Model</h2>
            {localModelInfo ? (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Current Round</p>
                  <p className="text-2xl font-bold text-primary-600">{localModelInfo.local_round}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Training Status</p>
                  <p className="text-2xl font-bold">
                    {localModelInfo.training_in_progress ? (
                      <span className="text-yellow-600">In Progress</span>
                    ) : (
                      <span className="text-green-600">Ready</span>
                    )}
                  </p>
                </div>
                {localModelInfo.active_model && (
                  <>
                    <div>
                      <p className="text-sm text-gray-600">Active Model Size</p>
                      <p className="text-lg font-semibold">{localModelInfo.active_model.size_mb.toFixed(2)} MB</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Last Updated</p>
                      <p className="text-lg font-semibold">
                        {new Date(localModelInfo.active_model.modified).toLocaleString()}
                      </p>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <p className="text-gray-500">Loading model info...</p>
            )}
          </div>

          {/* Model Selector */}
          {availableModels.length > 0 && (
            <div className="card bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Switch Active Model</h2>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-2">
                    Active: <span className="text-primary-600 font-semibold">{activeModelName}</span>
                  </label>
                  <select 
                    className="input-field"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    <option value="">Select a model...</option>
                    {availableModels.map(model => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.size_mb} MB)
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={() => selectedModel && handleSwitchModel(selectedModel)}
                  disabled={!selectedModel}
                  className="btn-primary mt-6"
                >
                  Switch Model
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Available models: {availableModels.length} | Switch to use a different FL round model for scoring
              </p>
            </div>
          )}

          {/* New Model Alert */}
          {modelUpdateAvailable && (
            <div className="card bg-green-50 border-2 border-green-400 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-green-800">🎉 New Aggregated Model Available!</h3>
                  <p className="text-green-700">A new global model has been created from federated learning.</p>
                </div>
                <button
                  onClick={handleManualDownload}
                  disabled={downloadingModel}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {downloadingModel ? 'Downloading...' : 'Download Now'}
                </button>
              </div>
            </div>
          )}

          {/* New Applications Status */}
          {newApplicationsCount > 0 && (
            <div className="card bg-blue-50 border-2 border-blue-400 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-blue-800">📋 New Applications Ready</h3>
                  <p className="text-blue-700">
                    {newApplicationsCount} new {newApplicationsCount === 1 ? 'application' : 'applications'} will be merged into training dataset when FL training starts.
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">{newApplicationsCount}</div>
                  <div className="text-sm text-blue-600">Pending</div>
                </div>
              </div>
            </div>
          )}

          {/* Training Actions */}
          <div className="card bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Training Actions</h2>
            {newApplicationsCount > 0 && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Starting FL training will automatically merge {newApplicationsCount} new {newApplicationsCount === 1 ? 'application' : 'applications'} into the training dataset.
                </p>
              </div>
            )}
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleTrainLocal}
                  disabled={trainingStatus === 'training'}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                >
                  {trainingStatus === 'training' ? (
                    <>
                      <span className="animate-spin inline-block mr-2">⟳</span>
                      Training...
                    </>
                  ) : (
                    '🚀 Start FL Training'
                  )}
                </button>
                
                {isPolling && (
                  <button
                    onClick={stopPolling}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                  >
                    Stop Polling
                  </button>
                )}
                
                {!isPolling && trainingStatus === 'completed' && (
                  <button
                    onClick={startPolling}
                    className="px-4 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200"
                  >
                    Resume Polling
                  </button>
                )}
              </div>
              
              <p className="text-sm text-gray-600">
                Training will: Load local dataset → Fine-tune model → Upload weights to FL server → Wait for aggregation
              </p>
            </div>
          </div>

          {/* Training Output */}
          {trainingOutput && (
            <div className="card bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Training Output</h2>
              <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre-wrap max-h-96 overflow-y-auto">
                {trainingOutput}
              </pre>
            </div>
          )}

          {/* How It Works */}
          <div className="card bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">How Federated Learning Works</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">1</span>
                <div>
                  <p className="font-semibold">Local Training</p>
                  <p className="text-gray-600 text-sm">Your bank trains the model on its private data. Data never leaves your system.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">2</span>
                <div>
                  <p className="font-semibold">Upload Weights</p>
                  <p className="text-gray-600 text-sm">Only model weights (not data) are sent to the FL server.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">3</span>
                <div>
                  <p className="font-semibold">FedAvg Aggregation</p>
                  <p className="text-gray-600 text-sm">Server combines weights from all banks using weighted averaging.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold">4</span>
                <div>
                  <p className="font-semibold">Auto-Update</p>
                  <p className="text-gray-600 text-sm">New global model is automatically downloaded and activated when ready.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffModelTraining;
