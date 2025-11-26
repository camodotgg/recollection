import { createFileRoute, Link } from '@tanstack/react-router';
import { BookOpen, Video, FileText, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const Route = createFileRoute('/')({ component: HomePage });

function HomePage() {
  const { user, isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to Recollection
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Transform any content into structured courses with AI
          </p>

          {isAuthenticated ? (
            <div className="space-x-4">
              <Link
                to="/content"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Load Content
              </Link>
              <Link
                to="/courses"
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                View Courses
              </Link>
            </div>
          ) : (
            <div className="space-x-4">
              <Link
                to="/auth/register"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Get Started
              </Link>
              <Link
                to="/auth/login"
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Sign In
              </Link>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <FeatureCard
            icon={<Video className="w-12 h-12 text-blue-500" />}
            title="YouTube Videos"
            description="Extract and summarize content from YouTube videos automatically"
          />
          <FeatureCard
            icon={<FileText className="w-12 h-12 text-blue-500" />}
            title="PDFs & Articles"
            description="Load content from PDFs, articles, and documents"
          />
          <FeatureCard
            icon={<Sparkles className="w-12 h-12 text-blue-500" />}
            title="AI-Powered"
            description="Generate structured courses using advanced AI models"
          />
          <FeatureCard
            icon={<BookOpen className="w-12 h-12 text-blue-500" />}
            title="Structured Courses"
            description="Get organized lessons with topics, takeaways, and more"
          />
        </div>

        {/* How It Works */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <StepCard
              number="1"
              title="Load Content"
              description="Paste a URL from YouTube, a PDF, or any article"
            />
            <StepCard
              number="2"
              title="AI Processing"
              description="Our AI extracts and summarizes the key information"
            />
            <StepCard
              number="3"
              title="Generate Course"
              description="Transform the content into a structured course with lessons"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function StepCard({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="relative">
      <div className="flex flex-col items-center">
        <div className="flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-4">
          {number}
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 text-center">{description}</p>
      </div>
    </div>
  );
}
