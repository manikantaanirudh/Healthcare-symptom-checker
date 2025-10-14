import React, { useState } from 'react';
import { AlertTriangle, Heart, Stethoscope, History } from 'lucide-react';
import SymptomChecker from './components/SymptomChecker.tsx';
import QueryHistory from './components/QueryHistory.tsx';

type TabType = 'checker' | 'history';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('checker');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-medical-600 p-2 rounded-lg">
                <Stethoscope className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Healthcare Symptom Checker
                </h1>
                <p className="text-sm text-gray-600">
                  Educational Purpose Only
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Heart className="h-4 w-4" />
              <span>Not for Medical Diagnosis</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('checker')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'checker'
                  ? 'border-medical-500 text-medical-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Stethoscope className="h-4 w-4 inline mr-2" />
              Symptom Checker
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-medical-500 text-medical-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <History className="h-4 w-4 inline mr-2" />
              Query History
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Educational Disclaimer */}
        <div className="mb-8">
          <div className="alert-warning flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-warning-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-warning-800">
                Educational Purpose Only
              </h3>
              <p className="text-sm text-warning-700 mt-1">
                This tool is for educational purposes only and is NOT a substitute for professional medical advice, 
                diagnosis, or treatment. Always consult with a qualified healthcare professional for proper medical care.
              </p>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'checker' && <SymptomChecker />}
        {activeTab === 'history' && <QueryHistory />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              Healthcare Symptom Checker - Educational Tool Only
            </p>
            <p className="mt-1">
              Not for medical diagnosis or treatment. Always consult healthcare professionals.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
