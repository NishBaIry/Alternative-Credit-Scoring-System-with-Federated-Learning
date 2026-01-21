import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Activity,
  Download,
  RefreshCw,
  Play,
  Pause,
  Server,
  FileText,
  CheckCircle,
  AlertCircle,
  Zap,
  Upload,
  Users
} from 'lucide-react';

import { API_BASE_URL } from '../lib/constants';

const StaffModelTraining = () => {
  // Training state
  const [trainingStatus, setTrainingStatus] = useState('idle');
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
          bank_id: import.meta.env.VITE_BANK_ID || 'bank_a',
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

        startPolling();

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

    return () => {
      stopPolling();
    };
  }, [fetchFLStatus, fetchLocalModelInfo, fetchAvailableModels, fetchNewApplicationsCount, stopPolling]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold mb-8 text-gray-900"
        >
          Model Training & Federated Learning
        </motion.h1>
        
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold">Error:</strong> {error}
            </div>
          </motion.div>
        )}

        <div className="grid gap-6">
          {/* FL Server Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Server className="w-5 h-5 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">FL Server Status</h2>
              </div>
              <div className="flex items-center gap-3">
                {isPolling && (
                  <span className="text-sm text-green-600 flex items-center gap-2 bg-green-50 px-3 py-1.5 rounded-full">
                    <Activity className="w-4 h-4 animate-pulse" />
                    <span>Listening for updates</span>
                  </span>
                )}
                <button 
                  onClick={fetchFLStatus}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>
            
            {flStatus ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Status</p>
                  <p className="text-xl font-bold text-green-600">{flStatus.status}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Current Round</p>
                  <p className="text-xl font-bold text-gray-900">{flStatus.current_round}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Pending Banks</p>
                  <p className="text-xl font-bold text-gray-900">{flStatus.clients_connected}/{flStatus.aggregation_threshold}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Total Aggregations</p>
                  <p className="text-xl font-bold text-gray-900">{flStatus.total_aggregations}</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Connecting to FL server...</p>
            )}
            
            {flStatus?.pending_updates?.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600 font-medium mb-2">Waiting for banks:</p>
                <div className="flex gap-2 flex-wrap">
                  {flStatus.pending_updates.map((bank, i) => (
                    <span key={i} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                      {bank}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </motion.div>

          {/* Local Model Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <Brain className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Local Model</h2>
            </div>
            {localModelInfo ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Current Round</p>
                  <p className="text-2xl font-bold text-purple-600">{localModelInfo.local_round}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-600 mb-1 font-medium">Training Status</p>
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
                    <div className="p-4 bg-gray-50 rounded-xl">
                      <p className="text-sm text-gray-600 mb-1 font-medium">Active Model Size</p>
                      <p className="text-lg font-semibold text-gray-900">{localModelInfo.active_model.size_mb.toFixed(2)} MB</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-xl">
                      <p className="text-sm text-gray-600 mb-1 font-medium">Last Updated</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {new Date(localModelInfo.active_model.modified).toLocaleString()}
                      </p>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <p className="text-gray-500">Loading model info...</p>
            )}
          </motion.div>

          {/* Model Selector */}
          {availableModels.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
            >
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Switch Active Model</h2>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-semibold mb-2 text-gray-700">
                    Active: <span className="text-purple-600">{activeModelName}</span>
                  </label>
                  <select 
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
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
                  className="mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  Switch Model
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-3">
                Available models: {availableModels.length} | Switch to use a different FL round model for scoring
              </p>
            </motion.div>
          )}

          {/* New Model Alert */}
          {modelUpdateAvailable && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-green-50 border-2 border-green-400 rounded-2xl shadow-sm p-6"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Zap className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-green-800">New Aggregated Model Available!</h3>
                    <p className="text-green-700">A new global model has been created from federated learning.</p>
                  </div>
                </div>
                <button
                  onClick={handleManualDownload}
                  disabled={downloadingModel}
                  className="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold"
                >
                  {downloadingModel ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Downloading...</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-5 h-5" />
                      <span>Download Now</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}

          {/* New Applications Status */}
          {newApplicationsCount > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-blue-50 border-2 border-blue-400 rounded-2xl shadow-sm p-6"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-blue-800">New Applications Ready</h3>
                    <p className="text-blue-700">
                      {newApplicationsCount} new {newApplicationsCount === 1 ? 'application' : 'applications'} will be merged into training dataset when FL training starts.
                    </p>
                  </div>
                </div>
                <div className="text-center ml-6">
                  <div className="text-4xl font-bold text-blue-600">{newApplicationsCount}</div>
                  <div className="text-sm text-blue-600 font-medium">Pending</div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Training Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
          >
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Training Actions</h2>
            {newApplicationsCount > 0 && (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-sm text-blue-800">
                  <strong className="font-semibold">Note:</strong> Starting FL training will automatically merge {newApplicationsCount} new {newApplicationsCount === 1 ? 'application' : 'applications'} into the training dataset.
                </p>
              </div>
            )}
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleTrainLocal}
                  disabled={trainingStatus === 'training'}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-semibold flex items-center gap-2"
                >
                  {trainingStatus === 'training' ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Training...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Start FL Training</span>
                    </>
                  )}
                </button>
                
                {isPolling && (
                  <button
                    onClick={stopPolling}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors flex items-center gap-2 font-medium"
                  >
                    <Pause className="w-4 h-4" />
                    <span>Stop Polling</span>
                  </button>
                )}
                
                {!isPolling && trainingStatus === 'completed' && (
                  <button
                    onClick={startPolling}
                    className="px-4 py-2 bg-green-100 text-green-700 rounded-xl hover:bg-green-200 transition-colors flex items-center gap-2 font-medium"
                  >
                    <Play className="w-4 h-4" />
                    <span>Resume Polling</span>
                  </button>
                )}
              </div>
              
              <p className="text-sm text-gray-600">
                Training will: Load local dataset → Fine-tune model → Upload weights to FL server → Wait for aggregation
              </p>
            </div>
          </motion.div>

          {/* Training Output */}
          {trainingOutput && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
            >
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Training Output</h2>
              <pre className="bg-gray-900 text-green-400 p-4 rounded-xl overflow-x-auto text-sm font-mono whitespace-pre-wrap max-h-96 overflow-y-auto">
                {trainingOutput}
              </pre>
            </motion.div>
          )}

          {/* How It Works */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="bg-white rounded-2xl shadow-sm p-6 border border-gray-200"
          >
            <h2 className="text-xl font-semibold mb-6 text-gray-900">How Federated Learning Works</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <span className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center font-bold text-lg">1</span>
                <div>
                  <p className="font-semibold text-gray-900">Local Training</p>
                  <p className="text-gray-600 text-sm mt-1">Your bank trains the model on its private data. Data never leaves your system.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center font-bold text-lg">2</span>
                <div>
                  <p className="font-semibold text-gray-900">Upload Weights</p>
                  <p className="text-gray-600 text-sm mt-1">Only model weights (not data) are sent to the FL server.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center font-bold text-lg">3</span>
                <div>
                  <p className="font-semibold text-gray-900">FedAvg Aggregation</p>
                  <p className="text-gray-600 text-sm mt-1">Server combines weights from all banks using weighted averaging.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="flex-shrink-0 w-10 h-10 bg-green-100 text-green-600 rounded-xl flex items-center justify-center font-bold text-lg">4</span>
                <div>
                  <p className="font-semibold text-gray-900">Auto-Update</p>
                  <p className="text-gray-600 text-sm mt-1">New global model is automatically downloaded and activated when ready.</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default StaffModelTraining;