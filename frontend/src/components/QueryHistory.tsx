import React, { useState, useEffect } from 'react';
import { History, Trash2, Eye, Calendar, User, Clock } from 'lucide-react';
import { QueryHistory as QueryHistoryType } from '../types/index.ts';
import { getQueryHistory, deleteQuery } from '../services/api.ts';

const QueryHistory: React.FC = () => {
  const [history, setHistory] = useState<QueryHistoryType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedQuery, setSelectedQuery] = useState<QueryHistoryType | null>(null);

  const pageSize = 10;

  useEffect(() => {
    loadHistory();
  }, [page]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getQueryHistory(page, pageSize);
      setHistory(response.queries);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load query history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this query?')) {
      return;
    }

    try {
      await deleteQuery(id);
      loadHistory(); // Reload the history
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete query');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <History className="h-5 w-5 mr-2" />
            Query History
          </h2>
          <span className="text-sm text-gray-600">
            {total} total queries
          </span>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading history...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-danger-600">{error}</p>
            <button
              onClick={loadHistory}
              className="btn-primary mt-4"
            >
              Try Again
            </button>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8">
            <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No queries found</p>
            <p className="text-sm text-gray-500 mt-1">
              Start by analyzing some symptoms to see your history here
            </p>
          </div>
        ) : (
          <>
            {/* History List */}
            <div className="space-y-4">
              {history.map((query) => (
                <div key={query.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                        <span className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(query.created_at)}
                        </span>
                        {query.age && (
                          <span className="flex items-center">
                            <User className="h-4 w-4 mr-1" />
                            Age {query.age}
                          </span>
                        )}
                        {query.duration_days && (
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {query.duration_days} days
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900 font-medium mb-2">
                        {query.symptoms.length > 100 
                          ? `${query.symptoms.substring(0, 100)}...` 
                          : query.symptoms
                        }
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {query.response.probable_conditions.slice(0, 2).map((condition, index) => (
                          <span
                            key={index}
                            className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                          >
                            {condition.condition}
                          </span>
                        ))}
                        {query.response.probable_conditions.length > 2 && (
                          <span className="text-xs text-gray-500">
                            +{query.response.probable_conditions.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => setSelectedQuery(query)}
                        className="text-medical-600 hover:text-medical-700 p-1"
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(query.id)}
                        className="text-danger-600 hover:text-danger-700 p-1"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center space-x-2 mt-6">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Query Detail Modal */}
      {selectedQuery && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Query Details
                </h3>
                <button
                  onClick={() => setSelectedQuery(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              {/* Original Query */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Original Symptoms</h4>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                  {selectedQuery.symptoms}
                </p>
                <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-600">
                  {selectedQuery.age && <span>Age: {selectedQuery.age}</span>}
                  {selectedQuery.sex && <span>Sex: {selectedQuery.sex}</span>}
                  {selectedQuery.duration_days && <span>Duration: {selectedQuery.duration_days} days</span>}
                  {selectedQuery.severity && <span>Severity: {selectedQuery.severity}</span>}
                </div>
              </div>

              {/* Response */}
              <div className="space-y-6">
                {/* Red Flags */}
                {selectedQuery.response.red_flags.length > 0 && (
                  <div className="alert-danger">
                    <h4 className="font-medium mb-2">Red Flags</h4>
                    <ul className="text-sm space-y-1">
                      {selectedQuery.response.red_flags.map((flag, index) => (
                        <li key={index}>• {flag}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Probable Conditions */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Probable Conditions</h4>
                  <div className="space-y-3">
                    {selectedQuery.response.probable_conditions.map((condition, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-medium">{condition.condition}</h5>
                          <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                            {Math.round(condition.confidence * 100)}%
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{condition.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Next Steps */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Recommended Next Steps</h4>
                  <div className="space-y-2">
                    {selectedQuery.response.recommended_next_steps.map((step, index) => (
                      <div
                        key={index}
                        className={`border rounded-lg p-3 ${getSeverityColor(step.type)}`}
                      >
                        <h5 className="font-medium capitalize">
                          {step.type.replace('_', ' ')}
                        </h5>
                        <p className="text-sm mt-1">{step.text}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="alert-info">
                  <p className="text-sm">{selectedQuery.response.disclaimer}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryHistory;
