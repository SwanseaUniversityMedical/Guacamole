{{/*
Define the image configs for containers
EXAMPLE USAGE: {{ include "image" (dict "image" .Values.image) }}
*/}}
{{- define "guacamole.image" }}
image: {{ .image.repository }}:{{ .image.tag }}
imagePullPolicy: {{ .image.pullPolicy }}
securityContext:
    runAsUser: {{ .image.uid }}
    runAsGroup: {{ .image.gid }}
{{- end }}

{{/*
Construct the base name for all resources in this chart.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "guacamole.fullname" -}}
{{- printf "%s" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Construct the service name for the guacd endpoint.
*/}}
{{- define "guacamole.guacd.service" -}}
{{ include "guacamole.fullname" . }}-guacd.{{ .Release.Namespace }}.svc.cluster.local
{{- end -}}

{{/*
Construct the service name for the web endpoint.
*/}}
{{- define "guacamole.web.service" -}}
{{ include "guacamole.fullname" . }}-web.{{ .Release.Namespace }}.svc.cluster.local
{{- end -}}

{{/*
Construct the service name for the client endpoint.
*/}}
{{- define "guacamole.database.service" -}}
{{ include "guacamole.fullname" . }}-database-rw.{{ .Release.Namespace }}.svc.cluster.local
{{- end -}}

{{/*
Construct the configmap name for the client schema script.
*/}}
{{- define "guacamole.initdb.configmap" -}}
{{ include "guacamole.fullname" . }}-database-initdb
{{- end -}}

{{/*
Construct the secret name for the client endpoint.
*/}}
{{- define "guacamole.database.secret" -}}
{{ .Values.database.secret | default (printf "%s-database-auth" (include "guacamole.fullname" .)) }}
{{- end -}}

{{/*
Construct the secret name for the client endpoint.
*/}}
{{- define "guacamole.ldap.secret" -}}
{{ .Values.ldap.secret | default (printf "%s-ldap-auth" (include "guacamole.fullname" .)) }}
{{- end -}}

{{/*
Construct the secret name for the controller to access the web rest api.
*/}}
{{- define "guacamole.controller.secret" -}}
{{ .Values.controller.secret | default (printf "%s-controller-auth" (include "guacamole.fullname" .)) }}
{{- end -}}

{{/*
Construct the `labels.app` for used by all resources in this chart.
*/}}
{{- define "guacamole.labels.app" -}}
{{- printf "%s" .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Construct the `labels.chart` for used by all resources in this chart.
*/}}
{{- define "guacamole.labels.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Define the nodeSelector for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.nodeSelector" (dict "Release" .Release "Values" .Values "nodeSelector" $nodeSelector) }}
*/}}
{{- define "guacamole.podNodeSelector" }}
{{- .nodeSelector | default .Values.defaultNodeSelector | toYaml }}
{{- end }}

{{/*
Define the Affinity for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.podAffinity" (dict "Release" .Release "Values" .Values "affinity" $affinity) }}
*/}}
{{- define "guacamole.podAffinity" }}
{{- .affinity | default .Values.defaultAffinity | toYaml }}
{{- end }}

{{/*
Define the Tolerations for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.podTolerations" (dict "Release" .Release "Values" .Values "tolerations" $tolerations) }}
*/}}
{{- define "guacamole.podTolerations" }}
{{- .tolerations | default .Values.defaultTolerations | toYaml }}
{{- end }}

{{/*
Define the PodSecurityContext for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.podSecurityContext" (dict "Release" .Release "Values" .Values "securityContext" $securityContext) }}
*/}}
{{- define "guacamole.podSecurityContext" }}
{{- .securityContext | default .Values.defaultSecurityContext | toYaml }}
{{- end }}

{{/*
The list of `volumeMounts` for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.volumeMounts" (dict "Release" .Release "Values" .Values "extraVolumeMounts" $extraVolumeMounts) }}
*/}}
{{- define "guacamole.volumeMounts" }}
{{- /* user-defined (global) */ -}}
{{- if .Values.extraVolumeMounts }}
{{ toYaml .Values.extraVolumeMounts }}
{{- end }}

{{- /* user-defined */ -}}
{{- if .extraVolumeMounts }}
{{ toYaml .extraVolumeMounts }}
{{- end }}
{{- end }}

{{/*
The list of `volumes` for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.volumes" (dict "Release" .Release "Values" .Values "extraVolumes" $extraVolumes) }}
*/}}
{{- define "guacamole.volumes" }}
{{- /* user-defined (global) */ -}}
{{- if .Values.extraVolumes }}
{{ toYaml .Values.extraVolumes }}
{{- end }}

{{- /* user-defined */ -}}
{{- if .extraVolumes }}
{{ toYaml .extraVolumes }}
{{- end }}
{{- end }}

{{/*
The list of `env` vars for guacamole pods
EXAMPLE USAGE: {{ include "guacamole.env" (dict "Release" .Release "Values" .Values "extraEnv" $extraEnv) }}
*/}}
{{- define "guacamole.env" }}
{{- /* user-defined (global) */ -}}
{{- if .Values.extraEnv }}
{{ toYaml .Values.extraEnv }}
{{- end }}

{{- /* user-defined */ -}}
{{- if .extraEnv }}
{{ toYaml .extraEnv }}
{{- end }}
{{- end }}
