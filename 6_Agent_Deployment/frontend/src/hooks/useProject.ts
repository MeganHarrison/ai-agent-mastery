import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Project, Meeting, ProjectInsight, ProjectWithMetrics } from '@/types/project.types';

export const useProject = (projectId: string | undefined) => {
  const [project, setProject] = useState<ProjectWithMetrics | null>(null);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [insights, setInsights] = useState<ProjectInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      setLoading(false);
      return;
    }

    const fetchProjectData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch project details
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('*')
          .eq('id', projectId)
          .single();

        if (projectError) throw projectError;

        // Fetch meetings for the project
        const { data: meetingsData, error: meetingsError } = await supabase
          .from('meetings')
          .select('*')
          .eq('project_id', projectId)
          .order('meeting_date', { ascending: false });

        if (meetingsError) console.error('Error fetching meetings:', meetingsError);

        // Fetch insights for the project
        const { data: insightsData, error: insightsError } = await supabase
          .from('project_insights')
          .select('*')
          .eq('project_id', projectId)
          .order('priority', { ascending: false })
          .order('created_at', { ascending: false });

        if (insightsError) console.error('Error fetching insights:', insightsError);

        setProject(projectData as ProjectWithMetrics);
        setMeetings(meetingsData || []);
        setInsights(insightsData || []);
      } catch (err) {
        console.error('Error fetching project data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load project data');
      } finally {
        setLoading(false);
      }
    };

    fetchProjectData();
  }, [projectId]);

  const updateProject = async (updates: Partial<Project>) => {
    if (!projectId) return;

    try {
      const { data, error } = await supabase
        .from('projects')
        .update(updates)
        .eq('id', projectId)
        .select()
        .single();

      if (error) throw error;

      setProject(prev => prev ? { ...prev, ...data } : data);
      return { data, error: null };
    } catch (err) {
      console.error('Error updating project:', err);
      return { data: null, error: err };
    }
  };

  const refreshData = async () => {
    if (!projectId) return;
    
    const fetchProjectData = async () => {
      try {
        setLoading(true);
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('*')
          .eq('id', projectId)
          .single();

        if (projectError) throw projectError;

        const { data: meetingsData } = await supabase
          .from('meetings')
          .select('*')
          .eq('project_id', projectId)
          .order('meeting_date', { ascending: false });

        const { data: insightsData } = await supabase
          .from('project_insights')
          .select('*')
          .eq('project_id', projectId)
          .order('priority', { ascending: false })
          .order('created_at', { ascending: false });

        setProject(projectData as ProjectWithMetrics);
        setMeetings(meetingsData || []);
        setInsights(insightsData || []);
      } catch (err) {
        console.error('Error refreshing project data:', err);
      } finally {
        setLoading(false);
      }
    };

    await fetchProjectData();
  };

  return {
    project,
    meetings,
    insights,
    loading,
    error,
    updateProject,
    refreshData,
  };
};

export const useProjects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        setError(null);

        const { data, error } = await supabase
          .from('projects')
          .select('*')
          .eq('is_archived', false)
          .order('priority', { ascending: false })
          .order('created_at', { ascending: false });

        if (error) throw error;

        setProjects(data || []);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError(err instanceof Error ? err.message : 'Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return {
    projects,
    loading,
    error,
  };
};