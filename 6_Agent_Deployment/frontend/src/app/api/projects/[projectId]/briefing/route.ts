// pages/api/projects/[projectId]/briefing.ts
import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const SYNTHESIS_PROMPT = `
You are an elite business strategist and project manager. I will provide you with individual insights extracted from meeting transcripts for a specific project. Your job is to synthesize these into an executive briefing format.

Analyze the insights and create a structured briefing with these sections:

1. EXECUTIVE SUMMARY
- Status (on-track/at-risk/critical)
- Headline (one sentence capturing the current situation)
- Key point (2-3 sentences explaining what leadership needs to know)

2. CURRENT STATE
- Momentum (strong/mixed/weak)
- Description (what's happening right now)
- Key developments (4-6 bullet points from the insights)

3. RISK ASSESSMENT
- Level (low/medium/high/critical)
- Primary concern (the biggest risk)
- Details (explanation of the risk)
- Potential impact (business consequences)

4. ACTIVE RESPONSE
- Approach (our strategy)
- Actions (what we're doing - from insights marked as actions)
- Next milestone (upcoming key date/deliverable)

5. LEADERSHIP ITEMS
- Items requiring decisions or awareness
- Urgency level for each

Focus on business impact, not technical details. Be concise but comprehensive. 
If there are conflicting insights, note the tension and recommend resolution.

Return ONLY a JSON object with this structure:
{
  "executiveSummary": {
    "status": "at-risk",
    "headline": "...",
    "keyPoint": "..."
  },
  "currentState": {
    "momentum": "mixed",
    "description": "...",
    "keyDevelopments": ["...", "..."]
  },
  "riskAssessment": {
    "level": "high",
    "primaryConcern": "...",
    "details": "...",
    "potentialImpact": "..."
  },
  "activeResponse": {
    "approach": "...",
    "actions": ["...", "..."],
    "nextMilestone": "..."
  },
  "leadershipItems": [
    {
      "type": "decision-needed",
      "item": "...",
      "urgency": "This week"
    }
  ]
}
`;

interface ProjectInsight {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  priority: string;
  confidence_score: number;
  source_document_id: string;
  metadata: any;
  created_at: string;
  meeting_title?: string;
  meeting_date?: string;
  participants?: string[];
}

export async function GET(
  request: NextRequest,
  { params }: { params: { projectId: string } }
) {
  const { projectId } = params;

  try {
    // 1. Get all insights for this project
    const { data: insights, error: insightsError } = await supabase
      .from('insights')
      .select(`
        *,
        meetings!inner(
          title,
          date,
          participants
        )
      `)
      .eq('project_id', projectId)
      .order('created_at', { ascending: false })
      .limit(50); // Get recent insights

    if (insightsError) {
      throw insightsError;
    }

    if (!insights || insights.length === 0) {
      return NextResponse.json({ error: 'No insights found for this project' }, { status: 404 });
    }

    // 2. Format insights for AI analysis
    const formattedInsights = insights.map((insight: any) => ({
      type: insight.insight_type,
      title: insight.title,
      description: insight.description,
      priority: insight.priority,
      confidence: insight.confidence_score,
      date: insight.created_at,
      meeting: insight.meetings?.title || 'Unknown Meeting',
      meetingDate: insight.meetings?.date,
      participants: insight.meetings?.participants || []
    }));

    // 3. Create the prompt for AI synthesis
    const analysisPrompt = `
${SYNTHESIS_PROMPT}

PROJECT INSIGHTS TO ANALYZE:
${JSON.stringify(formattedInsights, null, 2)}

Synthesize these insights into the executive briefing format described above.
`;

    // 4. Call OpenAI to synthesize insights
    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are an expert business strategist who synthesizes project data into executive briefings.'
          },
          {
            role: 'user',
            content: analysisPrompt
          }
        ],
        temperature: 0.3,
        max_tokens: 2000
      })
    });

    if (!openaiResponse.ok) {
      throw new Error(`OpenAI API error: ${openaiResponse.statusText}`);
    }

    const aiResult = await openaiResponse.json();
    let synthesizedBriefing;

    try {
      synthesizedBriefing = JSON.parse(aiResult.choices[0].message.content);
    } catch (parseError) {
      console.error('Failed to parse AI response:', aiResult.choices[0].message.content);
      throw new Error('Failed to parse AI synthesis response');
    }

    // 5. Enhance with drill-down data
    const enhancedBriefing = {
      ...synthesizedBriefing,
      lastUpdated: new Date().toISOString(),
      insightCount: insights.length,
      rawInsights: insights.map(insight => ({
        id: insight.id,
        type: insight.insight_type,
        title: insight.title,
        description: insight.description,
        priority: insight.priority,
        confidence: insight.confidence_score,
        meetingId: insight.source_document_id,
        meetingTitle: insight.meetings?.title,
        meetingDate: insight.meetings?.date,
        participants: insight.meetings?.participants,
        timestamp: insight.created_at
      }))
    };

    return NextResponse.json(enhancedBriefing);

  } catch (error) {
    console.error('Error generating project briefing:', error);
    return NextResponse.json({ 
      error: 'Failed to generate project briefing',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
