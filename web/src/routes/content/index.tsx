/**
 * Content loading page
 */
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { loadContentContentLoadPost, listContentContentGet } from '../../api/generated';
import { useAuth } from '../../contexts/AuthContext';
import { useTaskProgress } from '../../hooks/useTaskProgress';
import '../../lib/api-client';

export const Route = createFileRoute('/content/')({
  component: ContentPage,
});

function ContentPage() {
  const { user } = useAuth();
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);

  const { status, progressPercent, currentStep, result, error: taskError, isComplete, isFailed, connected } = useTaskProgress(taskId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await loadContentContentLoadPost({
        body: { url },
      });

      if (response.data) {
        setTaskId(response.data.task_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start content loading');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTaskId(null);
    setUrl('');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Load Content</h1>
          <p className="mt-2 text-sm text-gray-600">
            Enter a URL to load content from (YouTube, PDF, article, etc.)
          </p>
        </div>

        {!taskId ? (
          <div className="bg-white shadow-md rounded-lg p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="text-sm text-red-700">{error}</div>
                </div>
              )}

              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                  Content URL
                </label>
                <input
                  id="url"
                  name="url"
                  type="url"
                  required
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Supported: YouTube videos, PDFs, articles, and more
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Starting...' : 'Load Content'}
              </button>
            </form>
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg p-6">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Loading Content</h2>
              <p className="text-sm text-gray-600">Task ID: {taskId}</p>
            </div>

            <div className="space-y-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div
                  className={`h-3 w-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
                />
                <span className="text-sm text-gray-600">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-sm text-gray-700 mb-1">
                  <span>{status}</span>
                  <span>{progressPercent}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full ${
                      isFailed ? 'bg-red-600' : isComplete ? 'bg-green-600' : 'bg-blue-600'
                    }`}
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              {/* Current Step */}
              {currentStep && (
                <div className="text-sm text-gray-600">
                  <strong>Current step:</strong> {currentStep}
                </div>
              )}

              {/* Error */}
              {taskError && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="text-sm text-red-700">{taskError}</div>
                </div>
              )}

              {/* Success */}
              {isComplete && result && (
                <div className="rounded-md bg-green-50 p-4">
                  <div className="text-sm text-green-700">
                    Content loaded successfully!
                    <br />
                    Content ID: {result.content_id}
                  </div>
                </div>
              )}

              {/* Actions */}
              {(isComplete || isFailed) && (
                <button
                  onClick={handleReset}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Load Another URL
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
