/**
 * Hook to track time spent on a lesson and automatically check for completion.
 *
 * This hook:
 * - Tracks time spent viewing a lesson
 * - Periodically sends updates to the backend (every 10 seconds)
 * - Automatically marks lessons complete when time-based criteria are met
 */

import { useEffect, useRef, useState } from 'react';
import { updateLessonTimeProgressCoursesCourseIdLessonsTimePost } from '../api/generated';

interface UseLessonTimeTrackingOptions {
  courseId: string;
  lessonIndex: number;
  enabled: boolean; // Only track if course is started
  onProgressUpdate?: (newProgress: any) => void;
}

export function useLessonTimeTracking({
  courseId,
  lessonIndex,
  enabled,
  onProgressUpdate,
}: UseLessonTimeTrackingOptions) {
  const [timeSpent, setTimeSpent] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastSyncRef = useRef(0);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) {
      // Clear tracking if disabled
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      startTimeRef.current = null;
      return;
    }

    // Start tracking when lesson becomes visible
    startTimeRef.current = Date.now();

    // Update time every second
    intervalRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const currentTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setTimeSpent(currentTime);
      }
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      startTimeRef.current = null;
    };
  }, [enabled, lessonIndex]);

  // Send update to backend every 10 seconds
  useEffect(() => {
    if (!enabled || timeSpent === 0) return;

    const shouldSync = timeSpent - lastSyncRef.current >= 10;

    if (shouldSync) {
      lastSyncRef.current = timeSpent;

      updateLessonTimeProgressCoursesCourseIdLessonsTimePost({
        path: { course_id: courseId },
        body: {
          lesson_index: lessonIndex,
          time_spent_seconds: timeSpent,
        },
      })
        .then((response) => {
          if (response.data && onProgressUpdate) {
            onProgressUpdate(response.data);
          }
        })
        .catch((error) => {
          console.error('Failed to update lesson time:', error);
        });
    }
  }, [timeSpent, enabled, courseId, lessonIndex, onProgressUpdate]);

  return {
    timeSpent,
  };
}
