-- MerchLab private first-party on-site analytics: insert-only client, private owner report.
create table if not exists public.merchlab_site_events (
 id bigint generated always as identity primary key,
 occurred_at timestamptz not null default now(),
 visitor_id text not null check(length(visitor_id) between 8 and 80),
 session_id text not null check(length(session_id) between 8 and 80),
 event_name text not null check (event_name in ('session_start','page_view','product_view','category_view','search','add_to_bag','remove_from_bag','cart_qty_change','bag_view','shopee_handoff_view','outbound_shopee')),
 path text not null check(length(path)<=190 and (path='/merchlab' or path='/merchlab/' or path like '/merchlab/p/%' or path like '/merchlab/c/%')),
 product_id text check(product_id is null or product_id ~ '^[0-9]{5,18}$'),
 category text check(category is null or length(category)<=50),
 search_term text check(search_term is null or length(search_term)<=80),
 quantity integer check(quantity is null or quantity between 1 and 99),
 traffic_source text check(traffic_source is null or length(traffic_source)<=120),
 utm_campaign text check(utm_campaign is null or length(utm_campaign)<=140)
);
create index if not exists merchlab_site_events_occurred on public.merchlab_site_events(occurred_at);
create index if not exists merchlab_site_events_item on public.merchlab_site_events(product_id,occurred_at) where product_id is not null;
alter table public.merchlab_site_events enable row level security;
revoke all on table public.merchlab_site_events from public,anon,authenticated;
grant insert on table public.merchlab_site_events to anon,authenticated;
do $$ begin
if not exists(select 1 from pg_policies where schemaname='public' and tablename='merchlab_site_events' and policyname='merchlab_anonymous_write_only')
then create policy "merchlab_anonymous_write_only" on public.merchlab_site_events for insert to anon,authenticated with check (true); end if;
end $$;
grant usage on sequence public.merchlab_site_events_id_seq to anon,authenticated;
create or replace function public.merchlab_dashboard_snapshot(p_days integer,p_token text)
returns jsonb language plpgsql security definer set search_path=public,pg_temp as $fn$
declare since_time timestamptz; result jsonb;
begin
if p_days not in (7,30,90) then raise exception 'Invalid reporting window' using errcode='22023'; end if;
if p_token is null or not public.astra_analytics_session_is_valid(p_token)
 then raise exception 'Unauthorized' using errcode='42501'; end if;
since_time:=(date_trunc('day',now() at time zone 'Asia/Manila')-(p_days-1)*interval '1 day') at time zone 'Asia/Manila';
select jsonb_build_object(
 'period_days',p_days,'report_through',now(),
 'first_event',(select min(occurred_at) from public.merchlab_site_events),
 'kpis',(select jsonb_build_object(
   'visitors',count(distinct visitor_id),
   'sessions',count(distinct session_id) filter(where event_name='session_start'),
   'page_views',count(*) filter(where event_name='page_view'),
   'product_views',count(*) filter(where event_name='product_view'),
   'category_views',count(*) filter(where event_name='category_view'),
   'searches',count(*) filter(where event_name='search'),
   'add_to_bag',count(*) filter(where event_name='add_to_bag'),
   'bag_views',count(*) filter(where event_name='bag_view'),
   'shopee_handoffs',count(*) filter(where event_name='shopee_handoff_view'),
   'outbound_shopee',count(*) filter(where event_name='outbound_shopee')
 ) from public.merchlab_site_events where occurred_at>=since_time),
 'daily',(select coalesce(jsonb_agg(to_jsonb(d) order by d.day),'[]'::jsonb) from (
    select to_char(occurred_at at time zone 'Asia/Manila','YYYY-MM-DD') AS day,
    count(*) filter(where event_name='page_view') page_views,
    count(distinct visitor_id) visitors,
    count(distinct session_id) filter(where event_name='session_start') sessions,
    count(*) filter(where event_name='product_view') product_views,
    count(*) filter(where event_name='add_to_bag') add_to_bag,
    count(*) filter(where event_name='outbound_shopee') outbound_shopee
    from public.merchlab_site_events where occurred_at>=since_time group by 1 order by 1 desc limit 90
 ) d),
 'top_products',(select coalesce(jsonb_agg(to_jsonb(p) order by p.product_views desc,p.shopee_clicks desc),'[]'::jsonb) from (
    select product_id,count(*) filter(where event_name='product_view') product_views,
    count(*) filter(where event_name='add_to_bag') add_to_bag,
    count(*) filter(where event_name='outbound_shopee') shopee_clicks
    from public.merchlab_site_events where occurred_at>=since_time and product_id is not null
    group by product_id order by product_views desc,shopee_clicks desc limit 20
 ) p),
 'sources',(select coalesce(jsonb_agg(to_jsonb(s) order by s.sessions desc),'[]'::jsonb) from (
    select coalesce(traffic_source,'unknown') source,
    count(distinct session_id) filter(where event_name='session_start') sessions,
    count(*) filter(where event_name='page_view') page_views
    from public.merchlab_site_events where occurred_at>=since_time
    group by 1 order by sessions desc limit 15
 ) s),
 'search_terms',(select coalesce(jsonb_agg(to_jsonb(s) order by s.searches desc),'[]'::jsonb) from (
    select search_term,count(*) searches from public.merchlab_site_events
    where occurred_at>=since_time and event_name='search' and search_term is not null
    group by 1 order by 2 desc limit 15
 ) s)
) into result;
return result;
end;$fn$;
revoke all on function public.merchlab_dashboard_snapshot(integer,text) from public;
grant execute on function public.merchlab_dashboard_snapshot(integer,text) to anon,authenticated;
