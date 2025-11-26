/**
 * Course detail viewer page
 */
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState, useEffect } from 'react';
import {
  getCourseCoursesCourseIdGet,
  deleteCourseCoursesCourseIdDelete,
  getCourseProgressProgressCoursesCourseIdGet,
  startCourseProgressCoursesStartPost,
  markLessonCompleteProgressCoursesCourseIdLessonsCompletePost,
} from '../../api/generated';
import type { CourseDetailResponse, CourseProgressResponse } from '../../api/generated';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { BookOpen, CheckCircle, Clock, Target, Trash2, ArrowLeft, Play, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLessonTimeTracking } from '../../hooks/useLessonTimeTracking';
import '../../lib/api-client';

export const Route = createFileRoute('/courses/$courseId')({
  component: CourseDetailPage,
});

function CourseDetailPage() {
  const { courseId } = Route.useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [course, setCourse] = useState<CourseDetailResponse | null>(null);
  const [progress, setProgress] = useState<CourseProgressResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [startingCourse, setStartingCourse] = useState(false);
  const [markingComplete, setMarkingComplete] = useState<number | null>(null);
  const [expandedLesson, setExpandedLesson] = useState<number | null>(null);

  // Track time for expanded lesson
  useLessonTimeTracking({
    courseId,
    lessonIndex: expandedLesson ?? 0,
    enabled: expandedLesson !== null && progress !== null,
    onProgressUpdate: (newProgress) => {
      setProgress(newProgress);
    },
  });

  useEffect(() => {
    loadCourseAndProgress();
  }, [courseId]);

  const loadCourseAndProgress = async () => {
    setLoading(true);
    setError('');
    try {
      const courseResponse = await getCourseCoursesCourseIdGet({
        path: { course_id: courseId },
      });

      if (courseResponse.data) {
        setCourse(courseResponse.data);
      }

      // Try to load progress
      try {
        const progressResponse = await getCourseProgressProgressCoursesCourseIdGet({
          path: { course_id: courseId },
        });
        if (progressResponse.data) {
          setProgress(progressResponse.data);
        }
      } catch (progressErr: any) {
        // Progress not found is okay - course not started yet
        if (progressErr.response?.status !== 404) {
          console.error('Error loading progress:', progressErr);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const handleStartCourse = async () => {
    setStartingCourse(true);
    setError('');
    try {
      const response = await startCourseProgressCoursesStartPost({
        body: { course_id: courseId },
      });
      if (response.data) {
        setProgress(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start course');
    } finally {
      setStartingCourse(false);
    }
  };

  const handleToggleLessonComplete = async (lessonIndex: number, isCurrentlyComplete: boolean) => {
    if (isCurrentlyComplete) {
      // Don't allow un-marking for now (could implement unmark endpoint later)
      return;
    }

    setMarkingComplete(lessonIndex);
    setError('');
    try {
      const response = await markLessonCompleteProgressCoursesCourseIdLessonsCompletePost({
        path: { course_id: courseId },
        body: {
          lesson_index: lessonIndex,
          manually: true,
        },
      });
      if (response.data) {
        setProgress(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark lesson complete');
    } finally {
      setMarkingComplete(null);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this course?')) {
      return;
    }

    setDeleting(true);
    try {
      await deleteCourseCoursesCourseIdDelete({
        path: { course_id: courseId },
      });
      navigate({ to: '/courses' });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete course');
      setDeleting(false);
    }
  };

  const getLessonProgress = (lessonIndex: number) => {
    return progress?.lesson_progress?.find((lp) => lp.lesson_index === lessonIndex);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 flex items-center justify-center">
        <div className="text-gray-600">Loading course...</div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error || 'Course not found'}</div>
          <Button onClick={() => navigate({ to: '/courses' })}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Courses
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate({ to: '/courses' })}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Courses
          </Button>

          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                {course.title}
              </h1>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  {course.genre}
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  {course.difficulty_level}
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                  <Clock className="w-3 h-3 mr-1" />
                  {Math.floor(course.estimated_duration_seconds / 60)} min
                </span>
                {progress?.is_completed && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Completed
                  </span>
                )}
                {progress && !progress.is_completed && progress.is_started && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                    In Progress
                  </span>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              {!progress && (
                <Button
                  onClick={handleStartCourse}
                  disabled={startingCourse}
                  className="flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  {startingCourse ? 'Starting...' : 'Start Course'}
                </Button>
              )}
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={deleting}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                {deleting ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {progress && (
          <Card className="mb-8">
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-700">
                  <span className="font-medium">Course Progress</span>
                  <span>{progress.completion_percent}%</span>
                </div>
                <Progress value={progress.completion_percent} />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>
                    {progress.lesson_progress?.filter((lp) => lp.is_completed).length || 0} of{' '}
                    {course.lessons.length} lessons completed
                  </span>
                  {progress.completed_at && (
                    <span>Completed: {new Date(progress.completed_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Course Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Course Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-600">{course.description}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Objective
              </h3>
              <p className="text-gray-600">{course.objective}</p>
            </div>
          </CardContent>
        </Card>

        {/* Lessons */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BookOpen className="w-6 h-6" />
            Lessons ({course.lessons.length})
          </h2>
          <div className="space-y-4">
            {course.lessons.map((lesson: any, index: number) => {
              const lessonProgress = getLessonProgress(index);
              const isCompleted = lessonProgress?.is_completed || false;
              const isMarking = markingComplete === index;
              const isExpanded = expandedLesson === index;

              return (
                <Card
                  key={index}
                  className={isCompleted ? 'border-green-200 bg-green-50/30' : ''}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div
                        className="flex-1 cursor-pointer"
                        onClick={() => setExpandedLesson(isExpanded ? null : index)}
                      >
                        <CardTitle className="text-xl flex items-center gap-2">
                          {isCompleted && (
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                          )}
                          {isExpanded ? (
                            <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                          )}
                          Lesson {index + 1}: {lesson.title}
                        </CardTitle>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                          {lesson.estimated_duration_seconds && (
                            <CardDescription>
                              {Math.floor(lesson.estimated_duration_seconds / 60)} minutes
                            </CardDescription>
                          )}
                          {lessonProgress?.completed_manually && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              Manual
                            </span>
                          )}
                          {lessonProgress?.completed_automatically && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                              Auto
                            </span>
                          )}
                        </div>
                      </div>
                      {progress && (
                        <Button
                          variant={isCompleted ? 'outline' : 'default'}
                          size="sm"
                          onClick={() => handleToggleLessonComplete(index, isCompleted)}
                          disabled={isCompleted || isMarking}
                          className="flex items-center gap-2 flex-shrink-0"
                        >
                          {isCompleted ? (
                            <>
                              <Check className="w-4 h-4" />
                              Completed
                            </>
                          ) : isMarking ? (
                            'Marking...'
                          ) : (
                            <>
                              <Check className="w-4 h-4" />
                              Mark Complete
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  {isExpanded && (
                <CardContent className="space-y-4">
                  {lesson.description && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Description</h4>
                      <p className="text-gray-600">{lesson.description}</p>
                    </div>
                  )}

                  {lesson.objectives && lesson.objectives.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Objectives</h4>
                      <ul className="list-disc list-inside space-y-1 text-gray-600">
                        {lesson.objectives.map((objective: string, i: number) => (
                          <li key={i}>{objective}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {lesson.content_sections && lesson.content_sections.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Content</h4>
                      <div className="space-y-4">
                        {lesson.content_sections.map((section: any, i: number) => (
                          <div key={i} className="prose prose-sm max-w-none text-gray-600">
                            {section.title && section.title !== lesson.title && (
                              <h5 className="font-medium text-gray-800 mb-1">{section.title}</h5>
                            )}
                            <div className="whitespace-pre-wrap">{section.body}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {lesson.key_takeaways && lesson.key_takeaways.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Key Takeaways</h4>
                      <ul className="space-y-1">
                        {lesson.key_takeaways.map((takeaway: any, i: number) => {
                          const text = typeof takeaway === 'string' ? takeaway : (takeaway.name || takeaway.description || '');
                          return (
                            <li key={i} className="flex items-start gap-2 text-gray-600">
                              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                              <span>{text}</span>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}
                </CardContent>
                  )}
              </Card>
              );
            })}
          </div>
        </div>

        {/* Course Takeaways */}
        {course.takeaways && course.takeaways.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Course Takeaways</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {course.takeaways.map((takeaway: any, index: number) => {
                  const text = typeof takeaway === 'string' ? takeaway : (takeaway.text || takeaway.description || JSON.stringify(takeaway));
                  return (
                    <li key={index} className="flex items-start gap-2 text-gray-600">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span>{text}</span>
                    </li>
                  );
                })}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Topics */}
        {course.topics && course.topics.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Topics Covered</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {course.topics.map((topic: any, index: number) => {
                  const name = typeof topic === 'string' ? topic : (topic.name || topic.description || JSON.stringify(topic));
                  return (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                    >
                      {name}
                    </span>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Completion Criteria */}
        {course.completion_criteria && (
          <Card>
            <CardHeader>
              <CardTitle>Completion Criteria</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {typeof course.completion_criteria === 'string'
                  ? course.completion_criteria
                  : JSON.stringify(course.completion_criteria, null, 2)}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
