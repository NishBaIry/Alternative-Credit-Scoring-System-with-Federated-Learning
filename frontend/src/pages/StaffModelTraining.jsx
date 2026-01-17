// StaffModelTraining.jsx
// Controls local model training and FL participation for this bank.
// Shows dataset stats and last training metrics from /staff/model/status.
// Buttons: "Train local model" and "Send update to FL server" (two API calls).
// Displays global vs local AUC and current FL round, plus privacy budget epsilon.
// Great place to visually explain federated learning to judges.

import React, { useState } from 'react';

const StaffModelTraining = () => {
  const [trainingStatus, setTrainingStatus] = useState('idle');

  const modelInfo = {
    localRecords: 1234,
    goodBadRatio: '70:30',
    lastTraining: '2 days ago',
    localAuc: 0.94,
    globalRound: 12,
    globalAuc: 0.95,
    privacyBudget: 0.7,
  };

  const handleTrainLocal = () => {
    setTrainingStatus('training');
    // TODO: Call API to train local model
    setTimeout(() => setTrainingStatus('completed'), 3000);
  };

  const handleSendToFL = () => {
    // TODO: Send update to FL server
    alert('Model update sent to FL server');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Model Training & Federated Learning</h1>
        
        <div className="grid gap-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Local Dataset Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Records</p>
                <p className="text-2xl font-bold">{modelInfo.localRecords}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Good:Bad Ratio</p>
                <p className="text-2xl font-bold">{modelInfo.goodBadRatio}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Training</p>
                <p className="text-2xl font-bold">{modelInfo.lastTraining}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Model Performance</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Local Model AUC</p>
                <p className="text-3xl font-bold text-primary-600">{modelInfo.localAuc}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Global Model AUC</p>
                <p className="text-3xl font-bold text-secondary-600">{modelInfo.globalAuc}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Training Actions</h2>
            <div className="space-y-4">
              <div>
                <button
                  onClick={handleTrainLocal}
                  disabled={trainingStatus === 'training'}
                  className="btn-primary"
                >
                  {trainingStatus === 'training' ? 'Training...' : 'Train Local Model'}
                </button>
                {trainingStatus === 'completed' && (
                  <p className="text-green-600 mt-2">✓ Training completed successfully</p>
                )}
              </div>
              
              <div>
                <button onClick={handleSendToFL} className="btn-secondary">
                  Send Update to FL Server
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Federated Learning Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>Global Round:</span>
                <span className="font-semibold">{modelInfo.globalRound}</span>
              </div>
              <div className="flex justify-between">
                <span>Privacy Budget (ε):</span>
                <span className="font-semibold">{modelInfo.privacyBudget}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffModelTraining;
