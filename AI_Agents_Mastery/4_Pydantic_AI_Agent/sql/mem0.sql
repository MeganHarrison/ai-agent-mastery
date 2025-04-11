-- Enable the vector extension
create extension if not exists vector;

-- Create the memories table
create table if not exists mem0_memories (
  id text primary key,
  embedding vector(1536), -- Replace with the dimensions for your embedding model like 768 for nomic-embed-text (Ollama)
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc', now()),
  updated_at timestamp with time zone default timezone('utc', now())
);

-- Create the vector similarity search function
create or replace function match_vectors(
  query_embedding vector(1536), -- Replace with the dimensions for your embedding model like 768 for nomic-embed-text (Ollama)
  match_count int,
  filter jsonb default '{}'::jsonb
)
returns table (
  id text,
  similarity float,
  metadata jsonb
)
language plpgsql
as $$
begin
  return query
  select
    t.id::text,
    1 - (t.embedding <=> query_embedding) as similarity,
    t.metadata
  from mem0_memories t
  where case
    when filter::text = '{}'::text then true
    else t.metadata @> filter
  end
  order by t.embedding <=> query_embedding
  limit match_count;
end;
$$;