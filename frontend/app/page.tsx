"use client";

import { useState, useEffect } from "react";
import CourseCard from "./components/CourseCard";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // This function talks to your new FastAPI backend
  const fetchCourses = async (query = "") => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/search?q=${query}`,
      );
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      console.error("Failed to fetch courses:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Run the fetch automatically when the page loads, and whenever the user stops typing
  useEffect(() => {
    // Add a small "debounce" so it doesn't spam the backend on every single keystroke
    const delayDebounceFn = setTimeout(() => {
      fetchCourses(searchQuery);
    }, 300); // Waits 300ms after you stop typing

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">
            Universal Course Aggregator
          </h1>
        </div>

        <div className="mb-10 relative">
          <input
            type="text"
            placeholder="Search for Python, Data Science..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:w-1/2 p-4 pl-10 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
          />
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">Searching...</div>
        ) : courses.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {courses.map((course, index) => (
              <CourseCard key={index} course={course} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white border border-gray-200 rounded-xl text-gray-500">
            No courses found
          </div>
        )}
      </div>
    </main>
  );
}
