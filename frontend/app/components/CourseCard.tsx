type CourseProps = {
  course: {
    title: string;
    url?: string;
    thumbnail_url?: string;
    provider?: string;
    partner_institution?: string;
    category?: string;
    raw_data?: string[];
  };
};

export default function CourseCard({ course }: CourseProps) {
  // Removed the 'p-5' from the main wrapper so the image can stretch edge-to-edge
  return (
    <article className="flex flex-col h-full border border-gray-200 rounded-xl bg-white shadow-sm hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      {/* The Thumbnail Image */}
      {course.thumbnail_url ? (
        <div className="w-full h-40 bg-gray-100 overflow-hidden">
          <img
            src={course.thumbnail_url}
            alt={course.title}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="w-full h-40 bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center">
          {/* A fallback colored box just in case an image fails to load */}
          <span className="text-white font-bold text-lg opacity-50">
            {course.provider}
          </span>
        </div>
      )}

      {/* The Text Content Container */}
      <div className="p-5 flex flex-col flex-grow justify-between">
        <div>
          <p className="text-xs font-bold tracking-wider text-gray-500 uppercase mb-2">
            {course.provider}
          </p>
          <h3 className="text-lg font-bold text-gray-900 leading-tight mb-2 line-clamp-2">
            {course.title}
          </h3>
          {course.partner_institution && (
            <p className="text-sm text-gray-600 mb-4 line-clamp-1">
              {course.partner_institution}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          {course.category ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 line-clamp-1">
              {course.category}
            </span>
          ) : (
            <span className="text-xs text-gray-400">Standard Course</span>
          )}

          <a
            href={course.url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-blue-600 hover:text-blue-800 whitespace-nowrap ml-2"
          >
            View Details →
          </a>
        </div>
      </div>
    </article>
  );
}
