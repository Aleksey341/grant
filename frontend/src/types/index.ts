export interface Grant {
  id: number; source_name: string; source_url: string | null;
  who_can_apply: string | null; age_restrictions: string | null;
  max_amount: number | null; max_amount_text: string | null;
  window_schedule: string | null; typical_docs: string | null;
  reporting: string | null; critical_notes: string | null; submission_target: string | null;
  category: 'individual' | 'nko' | 'business'; is_active: boolean;
  last_scraped_at: string | null; created_at: string;
  deadlines: GrantDeadline[]; nearest_deadline?: string | null; deadline_label?: string | null;
}
export interface GrantDeadline { id: number; deadline_date: string | null; window_label: string | null; is_confirmed: boolean; source: string; }
export interface User { id: number; email: string; full_name: string | null; is_admin: boolean; notify_email: boolean; notify_telegram: boolean; notify_push: boolean; telegram_chat_id: string | null; created_at: string; }
export interface Application { id: number; grant_id: number; user_id: number; status: string; current_step: number; wizard_data: Record<string, any>; ai_hints: Record<string, any>; created_at: string; updated_at: string | null; }
