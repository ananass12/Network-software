# Пакетный менеджер Helm

## Задача
Писать YAML-манифесты вручную утомительно. Копировать их для dev, stage и prod окружений — ошибка. Если нужно поменять версию имиджа, придется править 3 файла.
**Helm** — это "apt/yum/pip" для Кубернетиса. Он позволяет создать шаблон (Chart) и подставлять туда разные значения (Values).

## Ваш вариант
`variants/<GROUP>/<STUDENT_ID>/week-13.json`
Вам понадобится имя чарта (`k8s.app`).

## Что нужно сделать
1. **Создать Helm Chart**:
   - Структура: `Chart.yaml`, `values.yaml`, `templates/`.
   - В `templates/` перенесите ваши `deployment.yaml` и `service.yaml` из прошлой недели.
   - Замените жестко прописанные значения на переменные: `{{ .Values.image.repository }}`.
2. **Настроить Values**:
   - `values.yaml`: дефолтные значения.
   - `values-dev.yaml`: для разработки (1 реплика, лимиты поменьше).
   - `values-prod.yaml`: для прода (3 реплики, лимиты побольше).
3. **Проверить шаблонизацию**:
   - `helm template my-release ./chart -f values-dev.yaml` — посмотрите, какой YAML получается на выходе.

## Что сдавать
1. Папку с чартом.
2. Файлы overrides (`values-*.yaml`).
3. Ответы на вопросы.

## Как проверить
```bash
make test WEEK=13
```

helm template my-release . -f values-dev.yaml
---
# Source: bookings-app/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: bookings-svc-s18 
  labels:
    app: bookings-app
spec:
  type: ClusterIP
  selector:
    app: bookings-app
  ports:
    - protocol: TCP
      port: 8292
      targetPort: 8292
---
# Source: bookings-app/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookings-app
  labels:
    app: bookings-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: bookings-app
  template:
    metadata:
      labels:
        app: bookings-app
    spec:
      containers:
        - name: bookings-container
          image: "bookings-app:dev-latest"
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8292
          
          livenessProbe:
            httpGet:
              path: /
              port: 8292
            initialDelaySeconds: 10
            periodSeconds: 10
            
          readinessProbe:
            httpGet:
              path: /
              port: 8292
            initialDelaySeconds: 5
            periodSeconds: 5

          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 100m
              memory: 128Mi

helm template my-release . -f values-prod.yaml
---
# Source: bookings-app/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: bookings-svc-s18 
  labels:
    app: bookings-app
spec:
  type: ClusterIP
  selector:
    app: bookings-app
  ports:
    - protocol: TCP
      port: 8292
      targetPort: 8292
---
# Source: bookings-app/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookings-app
  labels:
    app: bookings-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bookings-app
  template:
    metadata:
      labels:
        app: bookings-app
    spec:
      containers:
        - name: bookings-container
          image: "bookings-app:v1.0.0-stable"
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8292
          
          livenessProbe:
            httpGet:
              path: /
              port: 8292
            initialDelaySeconds: 10
            periodSeconds: 10
            
          readinessProbe:
            httpGet:
              path: /
              port: 8292
            initialDelaySeconds: 5
            periodSeconds: 5

          resources:
            requests:
              cpu: 200m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
(venv) nastya@Ubuntu:~/Network software/weeks/week-13/chart$ 