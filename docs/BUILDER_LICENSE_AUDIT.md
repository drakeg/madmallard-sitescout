# SS-005 — Builder and model integration license gate

Reviewed **2026-11-24** against upstream default-branch `LICENSE`, `README.md`, and configuration/docs as linked below. The companion machine-readable registry is [builder-candidates.json](builder-candidates.json). This is a **source-license and service-prerequisite screening**, not legal advice, a complete transitive dependency or model-weight license audit, or proof that any candidate works in SiteScout. No new hosted services or paid accounts are authorized.

## Decision matrix

| Candidate | Upstream code license | Unpaid local starting point | External requirements / restrictions | Preliminary decision |
|---|---|---|---|---|
| [OpenPage](https://github.com/buildingopen/openpage) | [MIT](https://github.com/buildingopen/openpage/blob/master/LICENSE) | Visual editor: documented `npm install && npm run dev` | AI site generation requires a Gemini API key; optional Pexels/Vercel integrations need separate credentials. Exported HTML may use Tailwind CDN / Google Fonts. | **First local builder UI benchmark**; leave hosted AI/deploy disabled |
| [Open Lovable](https://github.com/firecrawl/open-lovable) | [MIT](https://github.com/firecrawl/open-lovable/blob/main/LICENSE) | Development UI can be started locally; **full workflow is not offline** | Documented Firecrawl key, AI provider key and Vercel Sandbox or E2B credentials. Verify their costs, subscriptions, usage limits, content rights and data flows independently. | **Defer** as default free/local builder; benchmark only with explicit allowed providers |
| [Onlook](https://github.com/onlook-dev/onlook) | [Apache-2.0](https://github.com/onlook-dev/onlook/blob/main/LICENSE) for source | Local-first Mac source build; external agent for AI edits | **Critical asset exclusion**: licensed Central Icons, brand/wordmarks, DMG art, sounds and idea images cannot simply be redistributed in a fork. Replace them; preserve third-party NOTICE. Source builds can opt out of telemetry via `STUDIO_TELEMETRY=0`. | Candidate for local design workflow **only after asset replacement**, source build and license review |
| [OpenCode](https://github.com/anomalyco/opencode) | [MIT](https://github.com/anomalyco/opencode/blob/dev/LICENSE) | Coding agent can be evaluated separately from SiteScout | Commercial rights, costs and processing depend on the configured LLM runtime/provider. No specific model/provider approved. | **Local-agent evaluation candidate**, not a production default |
| [Astro](https://github.com/withastro/astro) | [MIT](https://github.com/withastro/astro/blob/main/LICENSE) (check LICENSE; GitHub license metadata may be NOASSERTION) | Source-code output framework | Audit selected themes/integrations, assets and hosting separately. | **Preferred benchmark output target**, contingent on reproducible build tests |
| [Ollama](https://github.com/ollama/ollama) | [MIT](https://github.com/ollama/ollama/blob/main/LICENSE) for runtime | Local inference runtime | **Model weights are separately licensed.** Verify each proposed model's usage, commercialization, attribution and redistribution terms. Confirm hardware/performance first. | Evaluate as optional inference runtime; **no model preapproved** |

## Commercial-use gate

1. **Source license and attribution.** Preserve MIT notices or Apache-2.0 license and NOTICE obligations, depending on the component. Verify every selected transitive dependency and generated-code template; the top-level license alone is insufficient.
2. **Bundled assets.** Exclude/relicense restricted brand marks, Onlook Central Icons and other non-open-source assets. Confirm fonts, stock imagery, imported customer graphics and generated-site assets have rights appropriate for commercial delivery.
3. **AI/model terms.** Review each specific model provider or model-weight license and generated-output policies, not just the orchestrator's code license. Inference cost and customer content retention are unknown until concrete provider/model selection.
4. **Hosting and costs.** OpenPage's editor can be tested locally. Keep Gemini, Pexels, Firecrawl, Vercel sandbox/deploy, E2B, other hosted integrations and paid APIs **off** unless specifically authorized. Validate whether exported websites load third-party assets and document those runtime dependencies.
5. **Security and tenancy.** No candidate may receive customer site content or credentials until sandbox/network boundaries, data retention and authorization are reviewed. Do not execute unreviewed generated code in the host's privileged environment.
6. **Benchmarks next.** Use **three identical fictional SMB briefs** (service contractor, café, and RV repair), target responsive pages and a synthetic inquiry form, and record build reproducibility, manual effort, functional completeness, mobile accessibility, external service dependencies, and **measured** costs. A pretty preview is not a working customer delivery.

## Source references and verification snapshot

The registry records the observed `LICENSE` blob SHA for each upstream repository, allowing a later check to detect source license changes. Sources checked:

- [OpenPage README](https://github.com/buildingopen/openpage/blob/master/README.md) and [environment example](https://github.com/buildingopen/openpage/blob/master/.env.example)
- [Open Lovable README](https://github.com/firecrawl/open-lovable/blob/main/README.md) and [environment example](https://github.com/firecrawl/open-lovable/blob/main/.env.example)
- [Onlook README](https://github.com/onlook-dev/onlook/blob/main/README.md), [asset rights](https://github.com/onlook-dev/onlook/blob/main/ASSETS.md) and [NOTICE](https://github.com/onlook-dev/onlook/blob/main/NOTICE)
- [OpenCode README](https://github.com/anomalyco/opencode/blob/dev/README.md)
- [Astro README](https://github.com/withastro/astro/blob/main/README.md)
- [Ollama README](https://github.com/ollama/ollama/blob/main/README.md)

**Still open for SS-005 completion:** per-package dependency license scan, generated asset/template rights, model-by-model commercial terms, documented hosting/privacy impact, and actual local-build verification. Candidate selection is provisional until those are checked.
