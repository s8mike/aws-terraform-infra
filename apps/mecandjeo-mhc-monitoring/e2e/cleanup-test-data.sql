-- Removes the data left behind by the browser smoke test (Playwright), and ONLY rows named "E2E":
-- cranes whose MHC number starts with E2E- and users whose email starts with e2e-, plus everything they own.
-- Safe to run more than once. Deletes run children first so no relationship is broken.
begin;

delete from delay_logs where task_log_id in (
  select t.id from task_logs t join shifts s on s.id = t.shift_id where s.mhc_number like 'E2E-%'
);
delete from performance_snapshots where shift_id in (select id from shifts where mhc_number like 'E2E-%');
delete from task_logs where shift_id in (select id from shifts where mhc_number like 'E2E-%');
delete from working_conditions where shift_id in (select id from shifts where mhc_number like 'E2E-%');
delete from shifts where mhc_number like 'E2E-%';
delete from report_exports where requested_by_id in (select id from users where email like 'e2e-%');
delete from audit_logs where actor_id in (select id from users where email like 'e2e-%');
delete from users where email like 'e2e-%';
delete from cranes where mhc_number like 'E2E-%';

commit;