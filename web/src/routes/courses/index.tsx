/**
 * Courses listing and generation page
 */
import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { useState, useEffect } from 'react';
import {
  listCoursesCoursesGet,
  listContentContentGet,
  generateCourseCoursesGeneratePost,
} from '../../api/generated';
import type { CourseResponse, ContentResponse } from '../../api/generated';
import { useAuth } from '../../contexts/AuthContext';
import { useTaskProgress } from '../../hooks/useTaskProgress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { BookOpen, Plus, Sparkles, FileText } from 'lucide-react';
import '../../lib/api-client';

export const Route = createFileRoute('/courses/')({
  component: CoursesPage,
});

function CoursesPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [courses, setCourses] = useState<CourseResponse[]>([]);
  const [content, setContent] = useState<ContentResponse[]>([]);
  const [selectedContent, setSelectedContent] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [showGenerator, setShowGenerator] = useState(false);

  const {
    status,
    progressPercent,
    currentStep,
    result,
    error: taskError,
    isComplete,
    isFailed,
    connected,
  } = useTaskProgress(taskId);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (isComplete && result) {
      // Course generation complete, reload courses
      loadData();
      setTaskId(null);
      setShowGenerator(false);
      setSelectedContent([]);
    }
  }, [isComplete, result]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [coursesRes, contentRes] = await Promise.all([
        listCoursesCoursesGet(),
        listContentContentGet(),
      ]);

      if (coursesRes.data) {
        setCourses(coursesRes.data);
      }
      if (contentRes.data) {
        setContent(contentRes.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCourse = async () => {
    if (selectedContent.length === 0) {
      setError('Please select at least one content item');
      return;
    }

    setError('');
    setGenerating(true);

    try {
      const response = await generateCourseCoursesGeneratePost({
        body: { content_ids: selectedContent },
      });

      if (response.data) {
        setTaskId(response.data.task_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start course generation');
    } finally {
      setGenerating(false);
    }
  };

  const toggleContentSelection = (contentId: string) => {
    setSelectedContent((prev) =>
      prev.includes(contentId)
        ? prev.filter((id) => id !== contentId)
        : [...prev, contentId]
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Courses</h1>
            <p className="mt-2 text-sm text-gray-600">
              Generate structured courses from your loaded content
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => navigate({ to: '/content' })}
              className="flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Load Content
            </Button>
            <Button
              onClick={() => setShowGenerator(!showGenerator)}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              {showGenerator ? 'Cancel' : 'Generate Course'}
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}

        {/* Course Generator */}
        {showGenerator && !taskId && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Generate New Course
              </CardTitle>
              <CardDescription>
                Select content items to generate a course
              </CardDescription>
            </CardHeader>
            <CardContent>
              {content.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No content available. <Link to="/content" className="text-blue-600 hover:underline">Load some content</Link> first.
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid gap-4">
                    {content.map((item) => (
                      <div
                        key={item.id}
                        onClick={() => toggleContentSelection(item.id)}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                          selectedContent.includes(item.id)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">
                              {item.source_origin || item.source_link}
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              {item.source_format} • {new Date(item.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <input
                            type="checkbox"
                            checked={selectedContent.includes(item.id)}
                            onChange={() => toggleContentSelection(item.id)}
                            className="mt-1"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button
                    onClick={handleGenerateCourse}
                    disabled={generating || selectedContent.length === 0}
                    className="w-full"
                  >
                    {generating ? 'Starting...' : `Generate Course from ${selectedContent.length} item(s)`}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Course Generation Progress */}
        {taskId && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Generating Course</CardTitle>
              <CardDescription>Task ID: {taskId}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <div
                  className={`h-3 w-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
                />
                <span className="text-sm text-gray-600">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              <div>
                <div className="flex justify-between text-sm text-gray-700 mb-1">
                  <span>{status}</span>
                  <span>{progressPercent}%</span>
                </div>
                <Progress value={progressPercent} />
              </div>

              {currentStep && (
                <div className="text-sm text-gray-600">
                  <strong>Current step:</strong> {currentStep}
                </div>
              )}

              {taskError && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="text-sm text-red-700">{taskError}</div>
                </div>
              )}

              {isComplete && result && (
                <div className="rounded-md bg-green-50 p-4">
                  <div className="text-sm text-green-700">
                    Course generated successfully!
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Courses List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No courses yet
              </h3>
              <p className="text-gray-600 mb-4">
                Generate your first course from loaded content
              </p>
              {content.length > 0 ? (
                <Button onClick={() => setShowGenerator(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Generate Course
                </Button>
              ) : (
                <Button onClick={() => navigate({ to: '/content' })}>
                  Load Content First
                </Button>
              )}
            </div>
          ) : (
            courses.map((course) => (
              <Card
                key={course.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate({ to: `/courses/${course.id}` })}
              >
                <CardHeader>
                  <CardTitle className="text-xl">{course.title}</CardTitle>
                  <CardDescription>{course.genre}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {course.description}
                  </p>
                  <div className="text-xs text-gray-500">
                    <div>Difficulty: {course.difficulty_level}</div>
                    <div>
                      Duration: {Math.floor(course.estimated_duration_seconds / 60)} minutes
                    </div>
                    <div>
                      Created: {new Date(course.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
