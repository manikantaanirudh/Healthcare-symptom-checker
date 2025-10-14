import React, { useState } from 'react';
import { Send, Loader2, AlertTriangle, CheckCircle, Clock, User, Calendar } from 'lucide-react';
import { SymptomCheckRequest, SymptomCheckResponse } from '../types/index.ts';
import { checkSymptoms } from '../services/api.ts';

const SymptomChecker: React.FC = () => {
  const [formData, setFormData] = useState<SymptomCheckRequest>({
    symptoms: '',
    age: undefined,
    sex: undefined,
    duration_days: undefined,
    severity: undefined,
    context: ''
  });
  
  const [response, setResponse] = useState<SymptomCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof SymptomCheckRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await checkSymptoms(formData);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while analyzing symptoms');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (type: string) => {
    switch (type) {
      case 'urgent_care':
        return 'text-danger-600 bg-danger-50 border-danger-200';
      case 'see_physician':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'self_care':
        return 'text-medical-600 bg-medical-50 border-medical-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (type: string) => {
    switch (type) {
      case 'urgent_care':
        return <AlertTriangle className="h-4 w-4" />;
      case 'see_physician':
        return <Clock className="h-4 w-4" />;
      case 'self_care':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-8">
      {/* Input Form */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Describe Your Symptoms
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Symptoms Description */}
          <div>
            <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-2">
              Symptoms Description *
            </label>
            <textarea
              id="symptoms"
              value={formData.symptoms}
              onChange={(e) => handleInputChange('symptoms', e.target.value)}
              placeholder="Describe your symptoms in detail (e.g., 'I have been experiencing chest pain for 2 days, it gets worse when I breathe deeply')"
              className="input-field h-32 resize-none"
              required
            />
          </div>

          {/* Additional Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Age */}
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-2">
                Age (optional)
              </label>
              <input
                type="number"
                id="age"
                value={formData.age || ''}
                onChange={(e) => handleInputChange('age', e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="e.g., 35"
                min="0"
                max="120"
                className="input-field"
              />
            </div>

            {/* Sex */}
            <div>
              <label htmlFor="sex" className="block text-sm font-medium text-gray-700 mb-2">
                Sex (optional)
              </label>
              <select
                id="sex"
                value={formData.sex || ''}
                onChange={(e) => handleInputChange('sex', e.target.value || undefined)}
                className="input-field"
              >
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Duration */}
            <div>
              <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
                Duration (days) (optional)
              </label>
              <input
                type="number"
                id="duration"
                value={formData.duration_days || ''}
                onChange={(e) => handleInputChange('duration_days', e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="e.g., 3"
                min="0"
                max="3650"
                className="input-field"
              />
            </div>

            {/* Severity */}
            <div>
              <label htmlFor="severity" className="block text-sm font-medium text-gray-700 mb-2">
                Severity (optional)
              </label>
              <select
                id="severity"
                value={formData.severity || ''}
                onChange={(e) => handleInputChange('severity', e.target.value || undefined)}
                className="input-field"
              >
                <option value="">Select...</option>
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </div>
          </div>

          {/* Additional Context */}
          <div>
            <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Context (optional)
            </label>
            <textarea
              id="context"
              value={formData.context}
              onChange={(e) => handleInputChange('context', e.target.value)}
              placeholder="Any additional information that might be relevant (e.g., recent travel, medications, allergies)"
              className="input-field h-20 resize-none"
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || !formData.symptoms.trim()}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Analyze Symptoms</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="alert-danger flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-danger-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium text-danger-800">Error</h3>
            <p className="text-sm text-danger-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {response && (
        <div className="space-y-6">
          {/* Disclaimer */}
          <div className="alert-info">
            <p className="text-sm font-medium">{response.disclaimer}</p>
          </div>

          {/* Red Flags */}
          {response.red_flags.length > 0 && (
            <div className="alert-danger">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-danger-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-danger-800">Red Flags Detected</h3>
                  <ul className="text-sm text-danger-700 mt-2 space-y-1">
                    {response.red_flags.map((flag, index) => (
                      <li key={index}>• {flag}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Probable Conditions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Probable Conditions
            </h3>
            <div className="space-y-4">
              {response.probable_conditions.map((condition, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">{condition.condition}</h4>
                    <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                      {Math.round(condition.confidence * 100)}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{condition.rationale}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Next Steps */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Recommended Next Steps
            </h3>
            <div className="space-y-3">
              {response.recommended_next_steps.map((step, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${getSeverityColor(step.type)}`}
                >
                  <div className="flex items-start space-x-3">
                    {getSeverityIcon(step.type)}
                    <div>
                      <h4 className="font-medium capitalize">
                        {step.type.replace('_', ' ')}
                      </h4>
                      <p className="text-sm mt-1">{step.text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SymptomChecker;
