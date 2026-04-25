// frontend/src/app/components/CourseCard.tsx

type CourseProps = {
  course: {
    title: string;
    url?: string;
    thumbnail_url?: string;
    provider?: string;
    partner_institution?: string;
    category?: string;
    match_score?: number;
    reasoning?: string;

    // ✅ MOVED THESE UP: They are top-level properties of the course
    vibe_summary?: string;
    features?: {
      beginner_friendly?: number;
      hands_on?: number;
      summary?: string;
    };
    scores?: {
      beginner_friendly?: number;
      hands_on?: number;
    };

    // featured_review now only contains its own specific properties
    featured_review?: {
      description?: string;
      author?: string;
      rating?: number;
    };
  };
  isPersonalized: boolean;
};

export default function CourseCard({ course, isPersonalized }: CourseProps) {
  // DATA NORMALIZATION
  const displayQuote =
    course.vibe_summary ||
    course.featured_review?.description ||
    course.features?.summary ||
    course.reasoning;

  const quoteAuthor = course.featured_review?.author || "Course Insight";

  const beginnerScore =
    course.scores?.beginner_friendly ?? course.features?.beginner_friendly;
  const handsOnScore = course.scores?.hands_on ?? course.features?.hands_on;

  const matchPercentage = course.match_score
    ? Math.min(99, 75 + course.match_score / 4)
    : null;

  return (
    <article className="relative flex flex-col h-full border border-gray-200 rounded-xl bg-white shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden">
      {/* MATCH BADGE */}
      {isPersonalized && matchPercentage && (
        <div className="absolute top-3 right-3 z-10 bg-green-600 text-white text-[10px] font-black px-2.5 py-1.5 rounded-lg shadow-md border border-green-400">
          {Math.round(matchPercentage)}% MATCH
        </div>
      )}

      {/* THUMBNAIL */}
      <div className="w-full h-40 bg-gray-100 overflow-hidden relative border-b border-gray-50">
        {course.thumbnail_url ? (
          <img
            src={course.thumbnail_url}
            alt={course.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center">
            <span className="text-white font-bold text-lg opacity-30 uppercase tracking-tighter">
              {course.provider}
            </span>
          </div>
        )}
      </div>

      <div className="p-6 flex flex-col flex-grow">
        <div className="mb-auto">
          <p className="text-[10px] font-black tracking-widest text-blue-600 uppercase mb-1">
            {course.provider}
          </p>

          <h3 className="text-xl font-bold text-gray-900 leading-tight mb-2">
            {course.title}
          </h3>

          {course.partner_institution && (
            <p className="text-sm text-gray-500 mb-6 font-medium">
              {course.partner_institution}
            </p>
          )}

          {/* EXPANDED VIBE SECTION */}
          {displayQuote && (
            <div className="relative mt-4 mb-8">
              <div className="absolute -left-4 top-0 bottom-0 w-1 bg-blue-500 rounded-full opacity-20"></div>
              <p className="text-[15px] italic text-gray-700 leading-relaxed">
                {`“${displayQuote}”`}
              </p>
              <p className="mt-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                — {quoteAuthor}
              </p>
            </div>
          )}
        </div>

        {/* NUMERICAL CATEGORIES */}
        <div className="grid grid-cols-2 gap-6 mb-6 py-4 border-y border-gray-50 bg-gray-50/50 -mx-6 px-6">
          <div className="flex flex-col">
            <span className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">
              Beginner
            </span>
            <span className="text-2xl font-black text-blue-600">
              {beginnerScore ?? "—"}
              <span className="text-xs text-blue-300 ml-0.5">/10</span>
            </span>
          </div>
          <div className="flex flex-col border-l border-gray-200 pl-6">
            <span className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">
              Hands-On
            </span>
            <span className="text-2xl font-black text-emerald-600">
              {handsOnScore ?? "—"}
              <span className="text-xs text-emerald-300 ml-0.5">/10</span>
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="px-2 py-1 rounded text-[10px] font-bold bg-slate-100 text-slate-600 uppercase">
            {course.category || "Course"}
          </span>
          <a
            href={course.url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-bold text-blue-600 hover:underline transition-all"
          >
            Full Syllabus →
          </a>
        </div>
      </div>
    </article>
  );
}
