# Guacamole

## Development

### Values for local deployment on docker-for-windows
```yaml
ldap:
  hostname: "ldap.example.com"
  port: "636"
  userBaseDn: "OU=users,DC=ldap,DC=example,DC=com"
  groupBaseDn: "OU=groups,DC=ldap,DC=example,DC=com"
  pagedSize: 100
  
  # For dev only. Don't let the chart make the secrets like this in production!
  createSecret:
    create: true
    username: "CN=readonly,OU=service,DC=ldap,DC=example,DC=com"
    password: "password"

controller:
  enabled: true

  # Use the 0.0.0 tag with pullPolicy Never so that local 
  # docker-for-windows kubernetes can access the local image
  # without trying to pull it from a registry
  image:
    repository: controller
    tag: 0.0.0
    pullPolicy: Never

  createSecret:
    create: true
    username: guaccontroller
    password: password

guacd:
  enabled: true

web:
  enabled: true

ingress:
  enabled: false

database:
  enabled: true

  createSecret:
    create: true
    password: password

  storage:
    size: 1Gi
```

### Install Cloud Native PG
```bash
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.1.yaml
```

### Build the Guacamole Controller container

Tagged as controller:0.0.0 so that docker-for-windows kubernetes can access it without trying to pull it.
```bash
docker build -f containers\controller\Dockerfile -t controller:0.0.0 containers\controller
```

### Install the Guacamole CRDs chart
```bash
helm upgrade \
  guacamole-crds \
  --install \
  --force \
  --create-namespace \
  --namespace guacamole \
  charts\guacamole-crds
```

### Install the Guacamole chart
```bash
helm upgrade \
  guacamole \
  --install \
  --create-namespace \
  --namespace guacamole \
  --values local/values.yaml \
  charts\guacamole
```