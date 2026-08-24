{{/*
Common labels
*/}}
{{- define "congo-brain.labels" -}}
app.kubernetes.io/name: congo-brain
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "congo-brain.selectorLabels" -}}
app.kubernetes.io/name: congo-brain
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
App full name
*/}}
{{- define "congo-brain.appName" -}}
{{ .Release.Name }}-app
{{- end }}

{{/*
Frontend full name
*/}}
{{- define "congo-brain.frontendName" -}}
{{ .Release.Name }}-frontend
{{- end }}

{{/* Render only immutable image references: sha256 digest or full Git SHA tag. */}}
{{- define "congo-brain.image" -}}
{{- $repository := required "image repository is required" .repository -}}
{{- if .digest -}}
{{- if not (mustRegexMatch "^sha256:[a-f0-9]{64}$" .digest) -}}
{{- fail "image digest must match sha256:<64 lowercase hex characters>" -}}
{{- end -}}
{{- printf "%s@%s" $repository .digest -}}
{{- else -}}
{{- $tag := required "image tag or digest is required" .tag -}}
{{- if not (mustRegexMatch "^sha-[a-f0-9]{40}$" $tag) -}}
{{- fail "image tag must match sha-<40 lowercase Git SHA hex characters>" -}}
{{- end -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end -}}
{{- end }}
