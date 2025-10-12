'use client';

import { useUser } from '@clerk/nextjs';
import { useQuery } from '@tanstack/react-query';
import DreamCard from '../../components/DreamCard';
import { apiFetch } from '../../lib/api';
import { Dream } from '../../types/dream';

export default function JournalPage() {
  const { user } = useUser();

  const { data: dreams, isLoading, error } = useQuery({
    queryKey: ['dreams', user?.id],
    queryFn: async () => {
      const response = await apiFetch('/api/dreams');
      return response.dreams as Dream[];
    },
    enabled: !!user,
  });

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Please sign in to view your dreams</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dreams...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-600">Error loading dreams. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dream Journal
        </h1>
        <p className="text-gray-600">
          Your symbolic journey through the subconscious
        </p>
      </div>

      <div className="space-y-6">
        {dreams && dreams.length > 0 ? (
          dreams.map((dream) => (
            <DreamCard key={dream.sceneId} dream={dream} />
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No dreams yet</p>
            <p className="text-sm text-gray-500">
              Visit the Oracle Chat to generate your first dream
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
