# 金蝶云苍穹DevOps文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-001  
**创建时间**: 2026-03-20

---

## 📋 概述

金蝶云苍穹DevOps提供完整的持续集成、持续部署、自动化测试、容器编排等能力，支持敏捷开发和快速交付。

## 🚀 持续集成(CI)

### 1. CI/CD流水线

**GitLab CI配置（YAML）**:
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - package
  - deploy
  - verify

variables:
  DOCKER_REGISTRY: registry.kingdee.com
  DOCKER_IMAGE: k3cloud/app
  NAMESPACE: k3cloud
  KUBECONFIG: /etc/deploy/config

# 构建阶段
build:
  stage: build
  image: maven:3.8.6-openjdk-11
  script:
    - mvn clean compile -DskipTests
  artifacts:
    paths:
      - target/
    expire_in: 1 hour
  only:
    - branches
    - merge_requests

# 单元测试
unit_test:
  stage: test
  image: maven:3.8.6-openjdk-11
  script:
    - mvn test
    - mvn jacoco:report
  coverage: '/Total.*?([0-9]{1,3})%/'
  artifacts:
    reports:
      junit: target/surefire-reports/TEST-*.xml
      coverage_report:
        coverage_format: cobertura
        path: target/site/jacoco/jacoco.xml
  dependencies:
    - build
  only:
    - branches
    - merge_requests

# 集成测试
integration_test:
  stage: test
  image: maven:3.8.6-openjdk-11
  services:
    - mysql:5.7
    - redis:6.0
  variables:
    MYSQL_DATABASE: k3cloud_test
    MYSQL_ROOT_PASSWORD: password
    MYSQL_HOST: mysql
    REDIS_HOST: redis
  script:
    - mvn verify -DskipUnitTests
  dependencies:
    - build
  only:
    - branches
    - merge_requests

# 代码质量检查
sonarqube:
  stage: test
  image: sonarsource/sonar-scanner-cli
  script:
    - sonar-scanner 
      -Dsonar.host.url=$SONAR_HOST_URL 
      -Dsonar.login=$SONAR_TOKEN 
      -Dsonar.projectKey=k3cloud 
      -Dsonar.sources=src/
  dependencies:
    - build
  only:
    - branches
    - merge_requests

# 构建Docker镜像
docker_build:
  stage: package
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $DOCKER_REGISTRY
  script:
    - docker build -t $DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA
    - docker tag $DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA $DOCKER_REGISTRY/$DOCKER_IMAGE:latest
    - docker push $DOCKER_REGISTRY/$DOCKER_IMAGE:latest
  dependencies:
    - unit_test
  only:
    - main
    - tags

# 部署到测试环境
deploy_test:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_TEST
    - kubectl set image deployment/k3cloud-app k3cloud-app=$DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA -n $NAMESPACE-test
    - kubectl rollout status deployment/k3cloud-app -n $NAMESPACE-test
  dependencies:
    - docker_build
  environment:
    name: test
    url: https://test.k3cloud.com
  only:
    - main

# 部署到预发布环境
deploy_staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_STAGING
    - kubectl set image deployment/k3cloud-app k3cloud-app=$DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA -n $NAMESPACE-staging
    - kubectl rollout status deployment/k3cloud-app -n $NAMESPACE-staging
  dependencies:
    - docker_build
  environment:
    name: staging
    url: https://staging.k3cloud.com
  when: manual
  only:
    - main
    - tags

# 部署到生产环境
deploy_prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_PROD
    - kubectl set image deployment/k3cloud-app k3cloud-app=$DOCKER_REGISTRY/$DOCKER_IMAGE:$CI_COMMIT_SHA -n $NAMESPACE
    - kubectl rollout status deployment/k3cloud-app -n $NAMESPACE
  dependencies:
    - docker_build
  environment:
    name: production
    url: https://k3cloud.com
  when: manual
  only:
    - tags

# 生产环境验证
verify_prod:
  stage: verify
  image: curlimages/curl:latest
  script:
    - sleep 30  # 等待pod就绪
    - curl -f https://k3cloud.com/health || exit 1
    - curl -f https://k3cloud.com/api/health || exit 1
  dependencies:
    - deploy_prod
  only:
    - tags
```

### 2. GitHub Actions配置

**GitHub Actions工作流（YAML）**:
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ created ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
        cache: maven
    
    - name: Build with Maven
      run: mvn clean compile -DskipTests
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-artifacts
        path: target/

  test:
    needs: build
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:5.7
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: k3cloud_test
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
        cache: maven
    
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-artifacts
    
    - name: Run tests
      run: mvn test
      env:
        MYSQL_HOST: localhost
        MYSQL_DATABASE: k3cloud_test
        MYSQL_ROOT_PASSWORD: password
    
    - name: Generate test report
      run: mvn jacoco:report
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: target/surefire-reports/
    
    - name: Upload coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: target/site/jacoco/
    
    - name: Publish coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./target/site/jacoco/jacoco.xml

  docker:
    needs: [build, test]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-artifacts
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.DOCKER_REGISTRY }}
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:${{ github.sha }}
          ${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:latest
        cache-from: type=registry,ref=${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:buildcache
        cache-to: type=registry,ref=${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:buildcache,mode=max

  deploy_test:
    needs: docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to test environment
      run: |
        echo "Deploying to test environment..."
        kubectl set image deployment/k3cloud-app k3cloud-app=${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:${{ github.sha }} -n k3cloud-test
        kubectl rollout status deployment/k3cloud-app -n k3cloud-test
      env:
        KUBECONFIG: ${{ secrets.KUBE_CONFIG_TEST }}

  deploy_prod:
    needs: docker
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        kubectl set image deployment/k3cloud-app k3cloud-app=${{ secrets.DOCKER_REGISTRY }}/k3cloud/app:${{ github.sha }} -n k3cloud
        kubectl rollout status deployment/k3cloud-app -n k3cloud
      env:
        KUBECONFIG: ${{ secrets.KUBE_CONFIG_PROD }}
```

## 🧪 自动化测试

### 1. 单元测试

**JUnit测试（Java）**:
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("单据服务测试")
public class BillServiceTest {
    
    @Mock
    private BillRepository billRepository;
    
    @Mock
    private BillEntryRepository entryRepository;
    
    private BillService billService;
    
    @BeforeEach
    public void setUp() {
        billService = new BillService(billRepository, entryRepository);
    }
    
    @Test
    @DisplayName("创建单据成功")
    public void testCreateBill_Success() {
        // Arrange
        Bill bill = new Bill();
        bill.setBillNo("TEST001");
        bill.setBillDate(LocalDate.now());
        bill.setAmount(new BigDecimal("1000.00"));
        
        when(billRepository.save(any(Bill.class))).thenAnswer(invocation -> invocation.getArgument(0));
        
        // Act
        Bill result = billService.createBill(bill);
        
        // Assert
        assertNotNull(result);
        assertEquals("TEST001", result.getBillNo());
        assertEquals("draft", result.getStatus());
        assertNotNull(result.getCreateTime());
        
        verify(billRepository, times(1)).save(any(Bill.class));
    }
    
    @Test
    @DisplayName("创建单据失败-单据编号已存在")
    public void testCreateBill_BillNoExists() {
        // Arrange
        Bill bill = new Bill();
        bill.setBillNo("TEST001");
        
        when(billRepository.findByBillNo("TEST001")).thenReturn(Optional.of(new Bill()));
        
        // Act & Assert
        assertThrows(BusinessException.class, () -> billService.createBill(bill));
    }
    
    @Test
    @DisplayName("审核单据成功")
    public void testApproveBill_Success() {
        // Arrange
        Long billId = 1L;
        Bill bill = new Bill();
        bill.setId(billId);
        bill.setStatus("submitted");
        bill.setAmount(new BigDecimal("1000.00"));
        
        when(billRepository.findById(billId)).thenReturn(Optional.of(bill));
        when(billRepository.save(any(Bill.class))).thenAnswer(invocation -> invocation.getArgument(0));
        
        // Act
        Bill result = billService.approveBill(billId, "admin");
        
        // Assert
        assertEquals("approved", result.getStatus());
        assertNotNull(result.getApproveTime());
        assertEquals("admin", result.getApprover());
        
        verify(billRepository, times(1)).save(any(Bill.class));
    }
    
    @Test
    @DisplayName("审核单据失败-状态不是已提交")
    public void testApproveBill_NotSubmitted() {
        // Arrange
        Long billId = 1L;
        Bill bill = new Bill();
        bill.setId(billId);
        bill.setStatus("draft");
        
        when(billRepository.findById(billId)).thenReturn(Optional.of(bill));
        
        // Act & Assert
        assertThrows(BusinessException.class, () -> billService.approveBill(billId, "admin"));
    }
}
```

### 2. 集成测试

**Spring Boot集成测试**:
```java
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public class BillControllerIntegrationTest {
    
    @LocalServerPort
    private int port;
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    @DisplayName("创建单据API集成测试")
    public void testCreateBillAPI() {
        // Arrange
        String url = "http://localhost:" + port + "/api/bills";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer test-token");
        
        BillRequest request = new BillRequest();
        request.setBillNo("TEST001");
        request.setBillDate(LocalDate.now().toString());
        request.setAmount("1000.00");
        
        HttpEntity<BillRequest> entity = new HttpEntity<>(request, headers);
        
        // Act
        ResponseEntity<BillResponse> response = restTemplate.postForEntity(
            url,
            entity,
            BillResponse.class
        );
        
        // Assert
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("TEST001", response.getBody().getBillNo());
        assertEquals("draft", response.getBody().getStatus());
    }
}
```

### 3. 端到端测试

**Playwright E2E测试（TypeScript）**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('单据管理E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('https://k3cloud.com/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // 等待登录完成
    await page.waitForURL('https://k3cloud.com/dashboard');
  });

  test('创建单据流程', async ({ page }) => {
    // 导航到单据列表
    await page.click('text=单据管理');
    await page.click('text=自定义单据');
    
    // 等待页面加载
    await page.waitForSelector('.bill-list');
    
    // 点击创建单据
    await page.click('button:has-text("新建单据")');
    
    // 等待表单显示
    await page.waitForSelector('form');
    
    // 填写单据信息
    await page.fill('input[name="billNo"]', `TEST${Date.now()}`);
    await page.fill('input[name="amount"]', '1000.00');
    await page.fill('textarea[name="remarks"]', 'E2E测试单据');
    
    // 提交单据
    await page.click('button:has-text("提交")');
    
    // 等待成功提示
    await expect(page.locator('.ant-message-success')).toBeVisible();
    await expect(page.locator('.ant-message-success')).toContainText('提交成功');
    
    // 验证单据是否在列表中
    await page.click('button:has-text("刷新")');
    await expect(page.locator('.bill-list')).toContainText('E2E测试单据');
  });

  test('审批单据流程', async ({ page }) => {
    // 导航到待审批列表
    await page.click('text=审批中心');
    await page.click('text=待审批');
    
    // 选择第一条单据
    await page.click('.bill-list .bill-item:first-child');
    
    // 点击审批
    await page.click('button:has-text("审批")');
    
    // 填写审批意见
    await page.fill('textarea[name="approveRemarks"]', '同意');
    
    // 提交审批
    await page.click('button:has-text("确定")');
    
    // 等待成功提示
    await expect(page.locator('.ant-message-success')).toBeVisible();
    await expect(page.locator('.ant-message-success')).toContainText('审批成功');
  });
});
```

## 📦 容器编排

### 1. Kubernetes部署

**Kubernetes部署配置（YAML）**:
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k3cloud-app
  namespace: k3cloud
  labels:
    app: k3cloud-app
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: k3cloud-app
  template:
    metadata:
      labels:
        app: k3cloud-app
        version: v1.0.0
    spec:
      containers:
      - name: app
        image: registry.kingdee.com/k3cloud/app:latest
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: k3cloud-secrets
              key: db-host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: k3cloud-secrets
              key: db-password
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: k3cloud-service
  namespace: k3cloud
  labels:
    app: k3cloud-app
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: k3cloud-app
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: k3cloud-hpa
  namespace: k3cloud
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: k3cloud-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Helm Charts

**Helm Chart模板**:
```yaml
# Chart.yaml
apiVersion: v2
name: k3cloud
description: 金蝶云苍穹应用
type: application
version: 0.1.0
appVersion: "1.0.0"

---
# values.yaml
replicaCount: 3

image:
  repository: registry.kingdee.com/k3cloud/app
  pullPolicy: Always
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext: {}

securityContext: {}

service:
  type: ClusterIP
  port: 80

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

---
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "k3cloud.fullname" . }}
  labels:
    {{- include "k3cloud.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "k3cloud.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "k3cloud.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "k3cloud.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
```

## 📊 监控告警

### 1. Prometheus监控

**Prometheus配置**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'k3cloud'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  - job_name: 'k3cloud-app'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - k3cloud
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
```

**告警规则**:
```yaml
# alerts.yml
groups:
  - name: k3cloud_alerts
    interval: 30s
    rules:
      - alert: ApplicationDown
        expr: up{job="k3cloud-app"} == 0
        for: 1m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "K3Cloud应用服务宕机"
          description: "K3Cloud应用服务 {{ $labels.pod }} 已经宕机超过1分钟"
          
      - alert: HighErrorRate
        expr: rate(http_server_requests_total{job="k3cloud-app",status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "错误率超过阈值"
          description: "K3Cloud应用错误率 {{ $value | humanizePercentage }} 超过1%"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket{job="k3cloud-app"}[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "响应时间过长"
          description: "K3Cloud应用P95响应时间 {{ $value }}s 超过1秒"
          
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{job="k3cloud-app"} / container_spec_memory_limit_bytes > 0.85
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "内存使用率过高"
          description: "K3Cloud应用内存使用率 {{ $value | humanizePercentage }} 超过85%"
          
      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total{job="k3cloud-app"}[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "CPU使用率过高"
          description: "K3Cloud应用CPU使用率 {{ $value | humanizePercentage }} 超过80%"
```

## 📝 最佳实践

### 1. CI/CD最佳实践
- 快速反馈：每次提交都触发CI
- 分支策略：Git Flow或GitHub Flow
- 代码审查：强制Code Review
- 自动化测试：单元、集成、E2E测试

### 2. 容器化最佳实践
- 镜像优化：多阶段构建、镜像分层
- 安全扫描：定期扫描镜像漏洞
- 资源限制：设置CPU、内存限制
- 健康检查：配置liveness和readiness探针

### 3. 监控告警最佳实践
- 监控指标：覆盖率、阈值设置
- 告警策略：分级告警、告警收敛
- 告警通知：多渠道通知、值班轮换
- 故障处理：故障响应、复盘改进

## 📚 相关资源

- **DevOps文档**: https://developer.kingdee.com/devops
- **Kubernetes**: https://kubernetes.io
- **Prometheus**: https://prometheus.io

---

**文档版本**: v8.0  
**最后更新**: 2026-03-20  
**作者**: 太子
