"use client";

import { useState, useEffect, useCallback } from "react";
import CourseCard from "./components/CourseCard";
import LearningQuiz, { QuizPreferences } from "./components/LearningQuiz";

export type Course = {
  title: string;
  url: string;
  thumbnail_url?: string;
  provider: string;
  partner_institution?: string;
  category?: string;
  match_score?: number;
  // --- Fields from your scored_courses JSON ---
  scores?: {
    beginner_friendly: number;
    hands_on: number;
  };
  features?: {
    beginner_friendly?: number;
    hands_on?: number;
    summary?: string; // Some courses use this
  };
  featured_review?: {
    text: string;
  };
  vibe_summary?: string; // Fallback key
  reasoning?: string; // Fallback key
};

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showQuiz, setShowQuiz] = useState(true);
  const [quizPrefs, setQuizPrefs] = useState<QuizPreferences | null>(null);

  // AIRTIGHT LOGIC: Only personalized if quiz was taken AND choices weren't "any"
  const isPersonalized =
    !!quizPrefs && (quizPrefs.budget !== "any" || quizPrefs.time !== "any");

  const fetchSmartResults = useCallback(
    async (query: string, prefs: QuizPreferences | null) => {
      setIsLoading(true);
      const budget = prefs?.budget || "any";
      const time = prefs?.time || "any";
      const url = `http://localhost:8000/api/recommend?q=${encodeURIComponent(query)}&budget=${budget}&time=${time}`;

      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("Backend connection failed");
        const data = await res.json();
        setCourses(data);
      } catch (error) {
        console.error("Fetch error:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchSmartResults(searchQuery, quizPrefs);
    }, 400);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, quizPrefs, fetchSmartResults]);

  const handleQuizComplete = (prefs: QuizPreferences) => {
    setQuizPrefs(prefs);
    setShowQuiz(false);
  };

  const handleResetQuiz = () => {
    setQuizPrefs(null);
    setShowQuiz(true);
  };

  return (
    <main className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* HEADER */}
        <div className="mb-12 text-center sm:text-left">
          <h1 className="text-5xl font-black text-slate-900 tracking-tight mb-3">
            Course <span className="text-blue-600">Aggregator</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl font-medium">
            Find the right course for your schedule and budget.
          </p>
        </div>

        {/* QUIZ OR OPTIMIZATION BAR */}
        {showQuiz ? (
          <div className="mb-16">
            <LearningQuiz onComplete={handleQuizComplete} />
          </div>
        ) : (
          <div className="mb-8 flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
            {!isPersonalized ? (
              <div className="flex items-center gap-3">
                <div className="bg-slate-400 text-white p-2 rounded-lg">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <p className="text-sm font-bold text-slate-600 uppercase tracking-wide">
                  General Search Results
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="bg-blue-600 text-white p-2 rounded-lg">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <p className="text-sm font-bold text-blue-800 uppercase tracking-wide">
                  Optimized:{" "}
                  <span className="text-blue-600">
                    {quizPrefs?.budget === "free"
                      ? "Free Only"
                      : "Paid/Certificates"}{" "}
                    •{quizPrefs?.time === "snack" && " Snack-sized"}
                    {quizPrefs?.time === "weekend" && " Weekend Project"}
                    {quizPrefs?.time === "cert" && " Certification Path"}
                    {quizPrefs?.time === "mastery" && " Full Mastery"}
                  </span>
                </p>
              </div>
            )}
            <button
              onClick={handleResetQuiz}
              className="text-sm font-bold text-blue-600 hover:text-blue-800"
            >
              Reset Quiz
            </button>
          </div>
        )}

        {/* SEARCH BAR */}
        <div className="mb-12">
          <input
            type="text"
            placeholder="Search for a skill or topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full max-w-2xl p-5 bg-white border-2 border-slate-200 rounded-2xl shadow-sm focus:border-blue-500 outline-none text-slate-900 text-lg font-medium transition-all"
          />
        </div>

        {/* RESULTS GRID */}
        {isLoading ? (
          <div className="text-center py-24">
            <div className="inline-block animate-spin h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
            <p className="text-slate-500 font-bold tracking-widest text-sm uppercase">
              Curating path...
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
            {courses.map((course, index) => (
              <CourseCard
                key={`${course.url}-${index}`}
                course={course}
                isPersonalized={isPersonalized}
              />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
