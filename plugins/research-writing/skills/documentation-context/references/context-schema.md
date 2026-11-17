# Context schema

Every packet is a JSON object with `schema_version`, `mode`, `query`, `sources`, `claims`, `definitions`,
`assumptions`, `interfaces`, `examples`, `failure_modes`, `citations`, `unresolved_questions`, and
`recommended_next_reads`. Each citation contains `path`, `line_start`, `line_end`, `authority`, and
`confidence`. No packet may contain a source outside the approved scope.
