"use client";

import { useState } from "react";

export type QuizPreferences = {
  budget: "free" | "paid" | "any";
  time: "snack" | "weekend" | "cert" | "mastery" | "any";
  goal?: string;
};

export default function LearningQuiz({
  onComplete,
}: {
  onComplete: (prefs: QuizPreferences) => void;
}) {
  const [step, setStep] = useState(0);
  const [prefs, setPrefs] = useState<QuizPreferences>({
    budget: "any",
    time: "any",
  });

  const questions = [
    {
      id: "budget" as const,
      label: "What is your budget?",
      options: [
        { text: "Strictly Free", value: "free" },
        { text: "Willing to pay for Certificate", value: "paid" },
      ],
    },
    {
      id: "time" as const,
      label: "How much time can you commit?",
      options: [
        { text: "Snack-sized (< 45 mins)", value: "snack" },
        { text: "Weekend Project (1-5 hours)", value: "weekend" },
        { text: "Skill Certification (10-40 hours)", value: "cert" },
        { text: "Full Mastery (40+ hours)", value: "mastery" },
      ],
    },
  ];

  const handleSelect = (val: string) => {
    const currentQuestionId = questions[step].id;
    const newPrefs = { ...prefs, [currentQuestionId]: val };
    setPrefs(newPrefs);

    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      onComplete(newPrefs as QuizPreferences);
    }
  };

  const progress = ((step + 1) / questions.length) * 100;

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-3xl border border-blue-100 shadow-xl text-center">
      <div className="w-full bg-gray-100 h-2 rounded-full mb-8 overflow-hidden">
        <div
          className="bg-blue-500 h-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <span className="text-blue-500 font-bold text-xs uppercase tracking-widest mb-2 block">
        Question {step + 1} of {questions.length}
      </span>

      <h2 className="text-3xl font-extrabold text-gray-900 mb-8">
        {questions[step].label}
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {questions[step].options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => handleSelect(opt.value)}
            className="group relative p-6 bg-white border-2 border-gray-100 rounded-2xl text-lg font-bold text-gray-700 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200 shadow-sm"
          >
            {opt.text}
          </button>
        ))}
      </div>

      {/* ONLY ONE SKIP BUTTON NOW */}
      <button
        onClick={() => onComplete({ budget: "any", time: "any" })}
        className="mt-8 text-slate-400 hover:text-slate-600 text-sm font-semibold underline underline-offset-4 block w-full text-center"
      >
        Skip quiz and see all results
      </button>
    </div>
  );
}
