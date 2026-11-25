import io
import unittest
from pathlib import Path
from unittest.mock import patch

from app.server import Handler, DASHBOARD


class DashboardTests(unittest.TestCase):
    def test_dashboard_exists_and_has_accessible_status(self):
        html = DASHBOARD.read_text()
        self.assertIn("<h1>SiteScout</h1>", html)
        self.assertIn('role="status"', html)
        self.assertIn("/api/health", html)

    def test_private_capture_job_controls_do_not_persist_bearer_tokens(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="queue-capture"', html)
        self.assertIn('id="check-capture-job"', html)
        self.assertIn('id="capture-job-id"', html)
        self.assertIn("fetch('/api/jobs'", html)
        self.assertIn("fetch('/api/jobs/'+id", html)
        self.assertIn("Private Docker operator token (not stored)", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)
        self.assertIn("results.textContent", html)

    def test_completed_private_results_are_owner_authenticated_and_text_rendered(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="view-capture-result"', html)
        self.assertIn("fetch('/api/jobs/'+id+'/result'", html)
        self.assertIn("Private Docker operator token (not stored)", html)
        self.assertIn("results.textContent=JSON.stringify(data.result,null,2)", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_recent_private_jobs_use_owner_authenticated_no_store_fetch(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="list-capture-jobs"', html)
        self.assertIn("fetch('/api/jobs',{headers:{'Authorization':'Bearer '+token},cache:'no-store'})", html)
        self.assertIn("results.textContent=JSON.stringify(data.jobs,null,2)", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_offline_site_report_upload_form_and_demo(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-report-form"', html)
        self.assertIn('id="site-report-json"', html)
        self.assertIn('id="site-report-demo"', html)
        self.assertIn("fetch('/api/site_report'", html)
        self.assertIn("output.textContent=JSON.stringify(response.ok?data.report:data,null,2)", html)
        self.assertIn("sampleSitePages", html)

    def test_site_report_manifest_import_and_download_are_available(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-report-file"', html)
        self.assertIn('accept=".json,application/json"', html)
        self.assertIn('id="site-report-export" disabled', html)
        self.assertIn("file.size>2100000", html)
        self.assertIn("siteReportExport.disabled=false", html)
        self.assertIn("URL.revokeObjectURL(url)", html)

    def test_form_checklist_csv_export_is_available_and_spreadsheet_safe(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-report-checklist-export" disabled', html)
        self.assertIn('function spreadsheetSafeCell(value)', html)
        self.assertIn('if(/^\\s*[=+\\-@]/.test(text))', html)
        self.assertIn('siteChecklistExport.disabled=false', html)
        self.assertIn('sitescout-form-verification-checklist.csv', html)

    def test_offline_completed_checklist_review_controls(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-checklist-file"', html)
        self.assertIn('id="review-site-checklist"', html)
        self.assertIn('id="site-checklist-review-results"', html)
        self.assertIn("fetch('/api/checklist_review'", html)
        self.assertIn("output.textContent=JSON.stringify(response.ok?data.review:data,null,2)", html)

    def test_site_report_overview_is_evidence_based_and_resets_on_edit(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-report-highlights"', html)
        self.assertIn("function showSiteReportHighlights(report)", html)
        self.assertIn("showSiteReportHighlights(data.report)", html)
        self.assertIn("live behavior remain unverified", html)
        self.assertIn("siteReportHighlights.textContent='Analyze saved pages", html)

    def test_site_remediation_ui_is_text_only_and_clears_on_input(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-remediation-findings"', html)
        self.assertIn("function showRemediationFindings(report)", html)
        self.assertIn("showRemediationFindings(data.report)", html)
        self.assertIn("detail.textContent=", html)
        self.assertIn("remediationFindings.replaceChildren()", html)
        self.assertIn("Live behavior still needs verification", html)

    def test_prioritized_remediation_action_plan_csv_is_safe(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-remediation-export" disabled', html)
        self.assertIn("function exportRemediationCSV(report)", html)
        self.assertIn("rows.map(row=>row.map(spreadsheetSafeCell)", html)
        self.assertIn("remediationExport.disabled=false", html)
        self.assertIn("remediationExport.disabled=true", html)
        self.assertIn("sitescout-remediation-action-plan.csv", html)

    def test_printable_customer_report_is_self_contained_and_escaped(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-printable-export" disabled', html)
        self.assertIn('function printableSiteReport(report)', html)
        self.assertIn('function safeReportText(value)', html)
        self.assertIn('Content-Security-Policy', html)
        self.assertIn('site-printable-export', html)
        self.assertIn('sitescout-printable-client-report.html', html)
        self.assertIn('printableReportExport.disabled=false', html)
        self.assertIn('printableReportExport.disabled=true', html)

    def test_human_remediation_review_import_is_offline_and_bounded(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="site-remediation-review-file"', html)
        self.assertIn('id="review-site-remediation"', html)
        self.assertIn('id="site-remediation-review-results"', html)
        self.assertIn("fetch('/api/remediation_review'", html)
        self.assertIn("output.textContent=JSON.stringify(response.ok?data.review:data,null,2)", html)

    def test_url_first_analysis_and_advanced_saved_html_mode(self):
        html = DASHBOARD.read_text()
        self.assertIn('id="url-analysis-form"', html)
        self.assertIn('id="website-url"', html)
        self.assertIn('id="url-authorized"', html)
        self.assertIn('id="advanced-html-analysis"', html)
        self.assertIn("fetch('/api/url_report'", html)
        self.assertIn("body:JSON.stringify(request)", html)
        self.assertIn("const request={url,authorized:true}", html)
        self.assertIn("clearSiteReport()", html)
        self.assertIn("showSiteReportHighlights(data.report)", html)
        self.assertIn("showRemediationFindings(data.report)", html)
        self.assertIn("This host requires a private capture token", html)
        self.assertNotIn("localStorage", html)

    def test_docker_routes(self):
        for route, expected in (("/", b"SiteScout"), ("/health", b'"status": "ok"'), ("/api/health", b'"status": "ok"')):
            instance = Handler.__new__(Handler)
            instance.path = route
            instance.wfile = io.BytesIO()
            instance.send_response = lambda code: self.assertEqual(code, 200)
            instance.send_header = lambda *args: None
            instance.end_headers = lambda: None
            instance.do_GET()
            self.assertIn(expected, instance.wfile.getvalue())

    def test_vercel_config(self):
        import json
        config = json.loads(Path("vercel.json").read_text())
        self.assertEqual(config["rewrites"][0]["destination"], "/api/health")
