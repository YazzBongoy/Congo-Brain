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
