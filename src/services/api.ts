/** API service for connecting to the Story Intelligence Dashboard backend */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Story {
  id: string;
  headline: string;
  source: string;
  platform: "X" | "Facebook" | "News" | "Instagram" | "TikTok";
  engagement: number;
  velocity: "high" | "medium" | "low";
  reason: string;
  timestamp: string;
  credibility: number;
  url: string;
}

export interface StoriesQueryParams {
  limit?: number;
  min_score?: number;
  platform?: string;
  hours_back?: number;
}

/**
 * Fetch trending stories from the backend API
 */
export async function fetchStories(params: StoriesQueryParams = {}): Promise<Story[]> {
  const queryParams = new URLSearchParams();
  
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.min_score) queryParams.append('min_score', params.min_score.toString());
  if (params.platform) queryParams.append('platform', params.platform);
  if (params.hours_back) queryParams.append('hours_back', params.hours_back.toString());

  const url = `${API_BASE_URL}/api/stories${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching stories:', error);
    throw error;
  }
}

/**
 * Fetch a single story by ID
 */
export async function fetchStory(storyId: string): Promise<Story> {
  const url = `${API_BASE_URL}/api/stories/${storyId}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching story:', error);
    throw error;
  }
}

/**
 * Trigger scraping for a specific source
 */
export async function triggerScrape(sourceId: number): Promise<any> {
  const url = `${API_BASE_URL}/api/scrape/${sourceId}`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error triggering scrape:', error);
    throw error;
  }
}

/**
 * Fetch all active sources
 */
export async function fetchSources(): Promise<any[]> {
  const url = `${API_BASE_URL}/api/sources`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching sources:', error);
    throw error;
  }
}

/**
 * Health check
 */
export async function healthCheck(): Promise<boolean> {
  const url = `${API_BASE_URL}/api/health`;
  
  try {
    const response = await fetch(url);
    return response.ok;
  } catch (error) {
    return false;
  }
}
