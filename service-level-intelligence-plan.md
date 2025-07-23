# 🚀 Service-Level Intelligence Architecture Plan

**Evolution from Single-Repository to Multi-Repository Service Intelligence**

---

## 📋 **Current State (Successfully Implemented)**

### ✅ **Single-Repository BAML Enrichment**
- **BAML-powered intelligence** for individual repositories
- **13 types of enriched documents** per repository:
  - Component Analysis (files, complexity, purpose)
  - Dependency Analysis (relationships, coupling)
  - Architectural Analysis (patterns, design decisions)
  - Security Analysis (vulnerabilities, recommendations)
  - Performance Analysis (optimization opportunities)
  - Testing Analysis (coverage, quality)
  - Operational Analysis (deployment, maintenance)
  - Insights Summary & Architecture Summary
- **30x performance improvement** on subsequent loads
- **77KB intelligent storage** vs basic text indexing
- **Production-ready** with persistence and skip logic

---

## 🎯 **Vision: Service-Level Intelligence**

### **Problem Statement**
Real-world services consist of **multiple repositories** working together:
- **Sales Service Example:**
  - `sales-backend` (Python/FastAPI, K8s)
  - `sales-frontend` (React/TypeScript, K8s)
  - `sales-analytics` (Go/gRPC, EC2)
  - `sales-data-pipeline` (Python/Airflow, EC2)
  - `sales-dashboard` (Vue.js, K8s)

### **Service Intelligence Goals**
1. **Group repositories** into logical services
2. **Understand cross-repo relationships** (APIs, WebSockets, shared resources)
3. **Multi-stack awareness** (Python, React, Go, different deployment targets)
4. **Service-level insights** that emerge from repository interactions
5. **Intelligent chat routing** for service vs repo questions

---

## 🏗️ **Architecture Design**

### **1. Service Assignment & Management**

#### **User Experience Flow:**
```
User loads new repo → "Which service does this belong to?"
│
├─ Show dropdown with existing services
├─ Option to "Create New Service"
│
└─ Smart suggestions based on repo naming patterns
```

#### **Service Management:**
- **Service Registry**: Maintain list of defined services
- **Repository Mapping**: Track which repos belong to which services
- **Service Metadata**: Name, description, owner, creation date

### **2. Service-Level Data Structure**

#### **Lightweight Service Metadata (2-5KB per service):**
```
Service: "Sales Service"
├─ Repositories: [sales-backend, sales-frontend, sales-analytics, ...]
├─ Connection Matrix: 
│  ├─ sales-backend → [API] → sales-frontend
│  ├─ sales-backend → [gRPC] → sales-analytics  
│  └─ sales-analytics → [WebSocket] → sales-dashboard
├─ Tech Stack Summary: [Python, React, Go, Vue.js]
├─ Deployment Topology: [K8s clusters, EC2 instances]
└─ Communication Protocols: [REST, gRPC, WebSocket]
```

#### **Individual Repository Data (77KB each):**
- **Unchanged**: Keep current BAML enrichment per repo
- **Referenced**: Service level points to individual repo analyses
- **On-demand**: Load detailed repo data only when needed

### **3. Relationship Discovery (Option B: Smart Detection)**

#### **Auto-Detection Mechanisms:**
- **API Endpoints**: Scan code/configs for endpoint definitions
- **Database Connections**: Detect shared database connection strings
- **Import Statements**: Find references to other repos in codebase
- **Container Configs**: Parse Docker Compose, K8s manifests
- **Network Calls**: Analyze HTTP/gRPC calls in code

#### **Detection Process:**
```
New Repo Added → Smart Detection Scanner → Relationship Candidates → User Confirmation
```

### **4. Smart Chat Intelligence Architecture**

#### **Query Routing Logic:**

**🎯 Repository-Specific Questions:**
```
User: "How does sales-backend handle authentication?"
│
Intelligence Router:
├─ Detect: Question about specific repo
├─ Retrieve: Sales Service context (for related repos)
├─ Retrieve: sales-backend deep analysis
└─ Synthesize: Repo-focused answer with service context
```

**🎯 Service-Level Questions:**
```
User: "How does Sales Service handle user data?"
│
Intelligence Router:
├─ Detect: Question about service-wide concern
├─ Analyze: Which repos handle "user data"?
├─ Retrieve: Service metadata + relevant repo analyses
└─ Synthesize: Service-level answer from multiple repos
```

**🤖 External Agent Integration:**
```
External Agent API Request → Same Intelligence Router → Service/Repo Analysis
```

#### **Question Analysis Components:**
1. **Scope Detection**: Repo-specific vs Service-wide
2. **Relevant Repo Identification**: Which repos needed for this question?
3. **Context Assembly**: Combine service metadata with repo details
4. **Smart Synthesis**: Generate comprehensive answer

---

## 🎨 **User Interface Design**

### **Service Dashboard Visualization**

#### **Interactive Service Diagram:**
```
[Sales Service Dashboard]

┌─────────────────────────────────────────────┐
│  Sales Service Architecture                 │
├─────────────────────────────────────────────┤
│                                             │
│  🐍 sales-backend    ──API──→  ⚛️ frontend  │
│  (Python/K8s)                 (React/K8s)  │
│        │                                    │
│        │                                    │
│    gRPC │                                   │
│        ↓                                    │
│  🐹 analytics        ──WS──→  📊 dashboard  │
│  (Go/EC2)                     (Vue/K8s)    │
│                                             │
└─────────────────────────────────────────────┘
```

#### **Interactive Elements:**
- **Click Repository**: Drill down to individual repo analysis
- **Click Connection**: Show API specs, endpoints, protocols
- **Hover**: Quick tech stack and deployment info
- **Service Health**: Overall health score and status

### **Service Selection UI**
- **Dropdown with existing services** when adding new repo
- **Service creation workflow** for new services
- **Smart suggestions** based on repository naming patterns
- **Service search and filtering** for large organizations

---

## 🧠 **Extended BAML Intelligence Schema**

### **Service-Level Analysis Types:**

#### **1. Service Architecture Analysis**
- **Architecture Pattern**: Microservices, Modular Monolith, Hybrid, etc.
- **Repository Roles**: API Gateway, Backend Service, Frontend App, Data Pipeline
- **Service Tiers**: Presentation, Business Logic, Data Access, Integration
- **Service Boundaries**: Clear separation of concerns analysis

#### **2. Cross-Repository Relationship Analysis**
- **Dependency Graph**: Visual map of all inter-repo dependencies
- **Communication Patterns**: REST, gRPC, WebSocket, Message Queue flows
- **Data Flow Analysis**: How data moves through the service ecosystem
- **Integration Points**: Critical connection points and potential bottlenecks

#### **3. Technology Stack Analysis**
- **Language Distribution**: Python 40%, TypeScript 30%, Go 30%
- **Framework Compatibility**: Version conflicts, upgrade paths
- **Infrastructure Diversity**: K8s vs EC2 deployment implications
- **Technology Debt**: Outdated versions, migration recommendations

#### **4. Service Health & Resilience**
- **Single Points of Failure**: Critical dependencies that could break service
- **Resilience Analysis**: Fault tolerance, circuit breakers, fallback mechanisms
- **Operational Complexity**: Deployment difficulty, monitoring gaps
- **Scaling Characteristics**: Which components scale together/independently

#### **5. Security Analysis (Service-Wide)**
- **Cross-Repository Vulnerabilities**: Shared security risks
- **Service Attack Vectors**: How threats propagate through the service
- **Security Boundaries**: Trust zones and security perimeters
- **Compliance Impact**: Service-wide compliance requirements

---

## 🚀 **Implementation Phases**

### **Phase 1: Foundation (Service Grouping)**
- ✅ **Current State**: Single-repo BAML enrichment working
- 🔄 **Add**: Service assignment UI during repo loading
- 🔄 **Add**: Service registry (JSON-based) and repository mapping
- 🔄 **Add**: Basic service dashboard with repository list

### **Phase 2: BAML Service Intelligence**
- 🔄 **Extend**: BAML schema for service-level analysis
- 🔄 **Implement**: BAML functions for relationship discovery
- 🔄 **Add**: Auto-detection of repo connections using BAML
- 🔄 **Add**: Service architecture visualization

### **Phase 3: BAML Query Intelligence**
- 🔄 **Implement**: Core BAML functions (AnalyzeUserQuestion, DetermineDataSources, SynthesizeServiceResponse)
- 🔄 **Add**: BAML-powered intelligent query routing
- 🔄 **Add**: Context-aware response synthesis
- 🔄 **Add**: Service health scoring and insights

### **Phase 4: Advanced BAML Integration**
- 🔄 **Enhance**: External agent API with BAML intelligence
- 🔄 **Add**: Cross-service performance correlation analysis
- 🔄 **Add**: BAML-powered service recommendations
- 🔄 **Add**: Advanced service visualization and insights

---

## 🎯 **Key Success Metrics**

### **User Experience Metrics**
- **Service Discovery**: How quickly users can understand service architecture
- **Question Resolution**: Accuracy of service vs repo question routing
- **Insight Quality**: Value of cross-repo relationship insights

### **Technical Metrics**
- **Detection Accuracy**: Percentage of correctly identified repo relationships
- **Performance**: Service dashboard load times (target: <2 seconds)
- **Scalability**: Support for services with 50+ repositories

### **Business Value Metrics**
- **Architectural Understanding**: Improved service-level decision making
- **Risk Reduction**: Early identification of single points of failure
- **Onboarding Speed**: Faster developer understanding of service ecosystems

---

## 💭 **Open Design Questions**

### **1. Service Scope Management**
- **Company-wide services**: All developers see same service definitions
- **User-specific services**: Each user maintains their own service groupings
- **Team-based services**: Services scoped to team/organization level

### **2. Service Evolution Handling**
- **Repository Migration**: Moving repos between services
- **Service Splitting**: Breaking large services into smaller ones
- **Service Merging**: Combining related services
- **Historical Tracking**: Maintaining service evolution history

### **3. External Integration Points**
- **CI/CD Integration**: Automatic service updates on deployments
- **Infrastructure Integration**: K8s cluster awareness, cloud resource mapping
- **Monitoring Integration**: Service health from observability platforms
- **Documentation Integration**: Linking to external service documentation

---

## 🔮 **Future Enhancements**

### **Advanced Service Intelligence**
- **Performance Correlation Analysis**: How individual repo changes affect service performance
- **Cost Analysis**: Resource usage and cost optimization across service repositories
- **Compliance Tracking**: Service-wide regulatory compliance status
- **Change Impact Analysis**: Predicting service-wide impact of repository changes

### **Advanced Visualizations**
- **3D Service Architecture**: Interactive 3D visualization of complex services
- **Time-based Analysis**: Service evolution over time
- **Performance Heatmaps**: Visual performance bottleneck identification
- **Security Flow Diagrams**: Visual security boundary and threat modeling

---

## 🔄 **Service Management Flow & Data Architecture**

### **Service Creation & Management Flow**

#### **1. Service Creation Flow**

```
🆕 NEW SERVICE CREATION:

User adds first repo → "Create New Service"
│
├─ Service Creation Form:
│  ├─ Service Name: "Sales Service" 
│  ├─ Description: "Customer sales and analytics platform"
│  ├─ Owner/Team: "Sales Engineering Team"
│  └─ Tags: ["sales", "customer", "analytics"]
│
├─ Repo Assignment:
│  ├─ Repo Role: [Backend Service, Frontend App, Data Pipeline, etc.]
│  ├─ Tech Stack: Auto-detected (Python/FastAPI)
│  └─ Deployment Target: [K8s, EC2, Serverless]
│
└─ Service Created + First Repo Assigned
```

#### **2. Adding Repos to Existing Service**

```
📁 ADDING TO EXISTING SERVICE:

User adds new repo → Dropdown shows existing services
│
├─ Select "Sales Service" 
│
├─ Repo Assignment:
│  ├─ Repo Role: "Frontend App"
│  ├─ Tech Stack: Auto-detected (React/TypeScript)
│  ├─ Connections: "Connects to sales-backend via REST API"
│  └─ Deployment: "K8s cluster-1"
│
├─ Smart Detection:
│  ├─ Scan for API endpoints → Found: /api/customers, /api/orders
│  ├─ Scan for connections → Found: backend API calls
│  └─ Suggest connections → "sales-frontend → REST → sales-backend"
│
└─ Repo Added to Service + Relationships Updated
```

#### **3. Removing Repos from Service**

```
🗑️ REMOVING REPO FROM SERVICE:

Service Dashboard → Click repo → "Remove from Service"
│
├─ Impact Analysis:
│  ├─ Show dependent repos: "sales-frontend depends on this backend"
│  ├─ Show affected connections: "3 API connections will be broken"
│  └─ Warn about service impact
│
├─ Removal Options:
│  ├─ "Remove repo but keep enrichment data"
│  ├─ "Remove repo and delete all connections"
│  └─ "Move repo to different service"
│
└─ Update service architecture + connection matrix
```

### **Data Storage Strategy: Hybrid Approach**

#### **Storage Architecture**

```
📊 STORAGE ARCHITECTURE:

┌─────────────────────────────────────────┐
│  SERVICE METADATA STORE                 │
│  (Lightweight JSON/Database)            │
│                                         │
│  ├─ Service Registry                    │
│  ├─ Repository Mappings                 │
│  ├─ Connection Matrix                   │
│  └─ Service Configuration               │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  INDIVIDUAL REPO FAISS STORES           │
│  (Heavy Intelligence Data)              │
│                                         │
│  ├─ repo1.pkl (77KB BAML enrichment)    │
│  ├─ repo2.pkl (77KB BAML enrichment)    │
│  └─ repo3.pkl (77KB BAML enrichment)    │
└─────────────────────────────────────────┘
```

#### **File Structure**

```
~/.adalflow/
├─ services/
│  ├─ services_registry.json              # All services metadata
│  ├─ sales_service.json                  # Service-specific config
│  └─ auth_service.json                   # Another service
├─ databases/                             # Individual repo FAISS
│  ├─ sales-backend.pkl                   # Repo enrichment
│  ├─ sales-frontend.pkl                  # Repo enrichment
│  └─ sales-analytics.pkl                 # Repo enrichment
└─ wikicache/                            # Generated wiki content
   ├─ sales_service_wiki.json             # Service-level wiki
   └─ individual_repo_wikis/
```

#### **Service Metadata Examples**

**services_registry.json:**
```json
{
  "services": [
    {
      "id": "sales-service-001",
      "name": "Sales Service", 
      "description": "Customer sales and analytics platform",
      "created_at": "2024-07-21T18:00:00Z",
      "owner": "Sales Engineering Team",
      "repositories": [
        "github.com/company/sales-backend",
        "github.com/company/sales-frontend", 
        "github.com/company/sales-analytics"
      ],
      "repository_count": 3,
      "last_updated": "2024-07-21T19:30:00Z"
    }
  ]
}
```

**sales_service.json:**
```json
{
  "service_id": "sales-service-001",
  "name": "Sales Service",
  "repositories": {
    "github.com/company/sales-backend": {
      "role": "BACKEND_SERVICE",
      "tech_stack": "Python/FastAPI",
      "deployment": "K8s/cluster-1", 
      "api_endpoints": ["/api/customers", "/api/orders"],
      "added_at": "2024-07-21T18:00:00Z"
    },
    "github.com/company/sales-frontend": {
      "role": "FRONTEND_APP", 
      "tech_stack": "React/TypeScript",
      "deployment": "K8s/cluster-1",
      "added_at": "2024-07-21T18:15:00Z"
    }
  },
  "connections": [
    {
      "from": "sales-frontend",
      "to": "sales-backend", 
      "protocol": "REST_API",
      "endpoints": ["/api/customers", "/api/orders"],
      "description": "Frontend fetches customer and order data"
    }
  ],
  "architecture_pattern": "MICROSERVICES",
  "health_score": 0.85
}
```

---

## 🧠 **BAML-Powered Smart Chat & API Intelligence**

### **BAML-Driven Intelligent Query Routing**

#### **BAML Intelligence Architecture**

```
USER/AGENT QUESTION → BAML QUESTION ANALYSIS → BAML DATA PLANNING → BAML RESPONSE SYNTHESIS

BAML Intelligence Flow:
├─ b.AnalyzeUserQuestion() → Understands intent, scope, context
├─ b.DetermineDataSources() → Intelligently selects needed data
├─ Load optimized data → Service metadata + relevant repo FAISS
└─ b.SynthesizeServiceResponse() → Combines insights intelligently
```

#### **BAML Functions for Service Intelligence**

**Core BAML Functions:**
```python
# Question analysis and routing
def AnalyzeUserQuestion(
    question: str,
    available_services: list[str],
    available_repositories: list[str]
) -> QuestionAnalysis

# Intelligent data source selection
def DetermineDataSources(
    question_analysis: QuestionAnalysis,
    service_metadata: dict
) -> DataSourcePlan

# Intelligent response synthesis
def SynthesizeServiceResponse(
    original_question: str,
    question_analysis: QuestionAnalysis,
    service_data: dict,
    repo_data: list[dict]
) -> IntelligentResponse
```

**BAML Schema Extensions for Service Intelligence:**
```python
class QuestionAnalysis {
    question_scope QuestionScope  // SERVICE_LEVEL, REPO_SPECIFIC, CROSS_REPO
    relevant_services string[]
    relevant_repositories string[]
    question_intent QuestionIntent  // ARCHITECTURE, SECURITY, PERFORMANCE, etc.
    context_requirements ContextRequirement[]
    confidence_score float
}

class DataSourcePlan {
    priority_services string[]
    priority_repositories string[]
    connection_data_needed boolean
    estimated_data_size string
    loading_strategy LoadingStrategy
}

class IntelligentResponse {
    answer string
    confidence_score float
    data_sources_used string[]
    related_recommendations string[]
    follow_up_suggestions string[]
}
```

#### **BAML-Powered Query Examples**

**Scenario 1: Service-Level Question**
```
User: "How does Sales Service handle user authentication?"

BAML Processing:
├─ b.AnalyzeUserQuestion() → SERVICE_LEVEL, authentication focus, Sales Service scope
├─ b.DetermineDataSources() → sales_service.json + auth-related repos
├─ Load: Service metadata + sales-backend.pkl + auth-service.pkl
└─ b.SynthesizeServiceResponse() → "Sales Service uses OAuth2 via the sales-backend API, 
   which connects to the shared auth-service for token validation. The authentication 
   flow is: frontend → JWT token → backend → OAuth validation → auth-service..."
```

**Scenario 2: Complex Cross-Service Question**
```
User: "Why might the sales dashboard be loading slowly when customers browse products?"

BAML Processing:
├─ b.AnalyzeUserQuestion() → CROSS_SERVICE, performance focus, Sales + Product services
├─ b.DetermineDataSources() → Both service metadata + performance-related repos
├─ Load: sales_service.json + product_service.json + dashboard/API repo enrichments
└─ b.SynthesizeServiceResponse() → Comprehensive cross-service performance analysis
   with intelligent correlation of dashboard performance and product API load
```

**Scenario 3: Contextual Repository Question**
```
User: "How does input validation work in the backend?"
(Previous context: discussing Sales Service)

BAML Processing:
├─ b.AnalyzeUserQuestion() → REPO_SPECIFIC with service context, validation focus
├─ BAML understands "backend" = sales-backend from previous context
├─ b.DetermineDataSources() → sales-backend.pkl + service context
└─ b.SynthesizeServiceResponse() → Detailed validation analysis with service context
```

### **BAML-Powered API Architecture**

#### **BAML Intelligence Processing Flow**

```python
async def intelligent_query_router(question: str, user_context: dict):
    # 1. BAML analyzes the question intelligently
    analysis = await b.AnalyzeUserQuestion(
        question=question,
        available_services=get_user_services(),
        available_repositories=get_user_repositories()
    )
    
    # 2. BAML determines what data to load (optimized)
    data_plan = await b.DetermineDataSources(
        question_analysis=analysis,
        service_metadata=load_service_registry()
    )
    
    # 3. Load only the needed data (efficient)
    service_data = load_relevant_services(data_plan.services)
    repo_data = load_relevant_repos(data_plan.repositories)
    
    # 4. BAML synthesizes intelligent response
    response = await b.SynthesizeServiceResponse(
        original_question=question,
        question_analysis=analysis,
        service_data=service_data,
        repo_data=repo_data
    )
    
    return response
```

#### **Service-Aware API Endpoints**

**Enhanced Existing Endpoints:**
```
POST /api/chat/stream
├─ Now service-aware
├─ Intelligent routing logic
└─ Context assembly from service + repo data
```

**New Service Endpoints:**
```
GET /api/services/                     # List all services
GET /api/services/{service_id}         # Get service details
GET /api/services/{service_id}/repos   # List repos in service
POST /api/services/{service_id}/chat   # Service-specific chat
```

**WebSocket Intelligence:**
```
🔌 WEBSOCKET MESSAGES:
{
  "type": "service_question",
  "service_id": "sales-service-001", 
  "question": "How does authentication work?",
  "context": "service_level"
}

Response includes:
├─ Service architecture context
├─ Relevant repo analysis
└─ Cross-repo relationship insights
```

### **BAML Intelligence Capabilities**

#### **Why BAML Over Hard-Coded Rules:**

**✅ BAML Advantages:**
- **Contextual Understanding**: Understands nuanced and complex questions
- **Intelligent Inference**: Can infer relationships and implications automatically
- **Adaptive Intelligence**: Handles questions we never anticipated
- **Natural Language**: Works with human-like, conversational questions
- **Context Awareness**: Remembers previous conversation context

**❌ Hard-Coded Rules Problems:**
- Rigid pattern matching that breaks easily
- Cannot handle nuanced or complex questions
- Requires exhaustive rule writing for every scenario
- No contextual understanding or inference
- Fails on unexpected inputs

#### **BAML Question Understanding Examples:**

**Complex Contextual Questions:**
```
"Why might users be experiencing timeouts during checkout?"
→ BAML understands: e-commerce context, performance issue, 
  checkout flow spans multiple services, needs cross-service analysis
```

**Implicit Context Questions:**
```
Previous: "Tell me about the Sales Service"
Current: "How does authentication work in the frontend?"
→ BAML infers: frontend = sales-frontend, needs auth flow analysis
```

**Technical Inference Questions:**
```
"What happens when the database goes down?"
→ BAML infers: failure analysis needed, identify database dependencies
  across services, impact assessment, recovery procedures
```

### **External Agent Integration Examples**

**Performance Analysis Request:**
```
Question: "Why is Sales Service slow?"

Data Assembly:
├─ sales_service.json → service architecture + connections
├─ sales-backend.pkl → performance analysis
├─ sales-analytics.pkl → bottleneck identification  
├─ sales-frontend.pkl → client-side performance

Synthesis: "Performance issues in Sales Service stem from:
1. Database queries in sales-backend (identified in repo analysis)
2. Heavy analytics processing blocking the API
3. Frontend making unnecessary API calls
Service-level recommendation: Add caching layer between backend and analytics."
```

**Deployment Topology Request:**
```
External Agent: "What's the deployment topology of Sales Service?"

API Response: {
  "service": "Sales Service",
  "architecture_pattern": "MICROSERVICES", 
  "deployment_topology": {
    "kubernetes_clusters": ["cluster-1"],
    "repositories": {
      "sales-backend": "K8s/cluster-1", 
      "sales-frontend": "K8s/cluster-1",
      "sales-analytics": "EC2/us-east-1"
    },
    "connections": [...],
    "scaling_characteristics": [...]
  }
}
```

---

## 🚀 **Step-by-Step Deployment Journey**

### **Deployment Strategy: Incremental Value with Existing BAML**

**Key Principle**: Each step must be **testable, deployable, and provide immediate user value** while building on existing BAML capabilities and available data.

### **Step 1: Basic Service Assignment with Protocol Detection (Week 1)**
**Goal**: Users can assign repositories to services with automatic communication protocol detection

**Data Available**: Repository URLs, basic metadata, repository code content  
**BAML Available**: Existing individual repo enrichment (13 document types)

**Frontend Changes:**
- Add service dropdown in repository loading UI
- "Create New Service" option with basic form
- Service name and description input
- Protocol detection results display

**Backend Changes:**
- Create `~/.adalflow/services/` directory structure
- Implement `ServiceManager` class for service operations
- Basic `services_registry.json` creation and management
- **Multi-protocol detection system**
- Enhanced service assignment with protocol analysis

**Multi-Protocol Detection Implementation:**
```python
class ServiceManager:
    def assign_repo_to_service(self, service_id: str, repo_url: str):
        # 1. Basic assignment
        self._add_repo_to_service(service_id, repo_url)
        
        # 2. IMMEDIATELY detect communication protocols
        protocols = self._detect_repo_protocols(repo_url)
        
        # 3. Store comprehensive protocol information
        self._update_service_protocols(service_id, repo_url, protocols)
    
    def _detect_repo_protocols(self, repo_url: str) -> dict:
        """Detect all communication protocols in the repository"""
        repo_path = get_repo_path(repo_url)
        protocols = {
            "rest_api": self._scan_for_api_endpoints(repo_path),
            "grpc": self._scan_for_grpc_services(repo_path),
            "websocket": self._scan_for_websockets(repo_path),
            "graphql": self._scan_for_graphql(repo_path),
            "message_queues": self._scan_for_message_queues(repo_path),
            "databases": self._scan_for_databases(repo_path),
            "load_balancers": self._scan_for_load_balancers(repo_path)
        }
        return protocols
```

**Protocol Detection Methods:**
```python
def _scan_for_api_endpoints(self, repo_path: str) -> list:
    """Scan for REST API endpoints"""
    # Look for FastAPI/Flask routes: @app.get("/api/users")
    # Look for Express.js routes: app.get("/api/users", ...)
    # Look for Spring Boot: @GetMapping("/api/users")

def _scan_for_grpc_services(self, repo_path: str) -> list:
    """Scan for gRPC services"""
    # Look for .proto files: service UserService { rpc GetUser(...) }
    # Look for gRPC server setup: grpc.Server(), server.add_insecure_port()

def _scan_for_websockets(self, repo_path: str) -> list:
    """Scan for WebSocket connections"""
    # Look for WebSocket setup: WebSocket(), socket.io
    # Look for WebSocket routes: @websocket.route("/ws/...")

def _scan_for_message_queues(self, repo_path: str) -> list:
    """Scan for message queue usage"""
    # Look for Kafka: KafkaProducer, kafka.Consumer
    # Look for RabbitMQ: pika.BlockingConnection
    # Look for Redis: redis.publish(), celery tasks

def _scan_for_load_balancers(self, repo_path: str) -> list:
    """Scan for load balancer configurations"""
    # Look for NGINX: nginx.conf, upstream blocks
    # Look for HAProxy: haproxy.cfg, balance roundrobin
    # Look for Traefik: traefik.yml, docker labels
    # Look for Kubernetes Ingress: ingress.yaml, nginx-ingress
    # Look for Service Mesh: istio-proxy, linkerd configs
    # Look for Cloud LB: AWS ALB/NLB, GCP Load Balancer configs
```

**Enhanced Service JSON Structure:**
```json
{
  "service_id": "sales-service-001",
  "name": "Sales Service",
  "repositories": {
    "github.com/company/sales-backend": {
      "role": "BACKEND_SERVICE",
      "tech_stack": "Python/FastAPI",
      "deployment": "K8s/cluster-1",
      "communication_protocols": {
        "rest_api": ["/api/customers", "/api/orders", "/api/auth"],
        "websocket": ["/ws/notifications", "/ws/chat"],
        "grpc": ["UserService.GetUser", "OrderService.CreateOrder"],
        "message_queues": ["kafka://order-events", "redis://cache-invalidation"],
        "databases": ["postgresql://users-db", "redis://session-store"],
        "graphql": ["/graphql/users", "/graphql/orders"],
        "load_balancers": ["nginx://sales-backend-lb", "k8s-ingress://sales-ingress", "aws-alb://sales-alb"]
      },
      "added_at": "2024-07-21T18:00:00Z"
    }
  }
}
```

**API Endpoints:**
```python
GET /api/services/                    # List all services
POST /api/services/                   # Create new service  
POST /api/services/{id}/repos         # Assign repo to service with protocol detection
GET /api/services/{id}/protocols      # Get detected protocols for service
```

**Enhanced Test Criteria:**
- Load new repo → see service dropdown with existing services
- Create "Sales Service" → assign repository successfully
- **Protocol detection** → identifies REST API endpoints: `/api/users`, `/api/orders`
- **Protocol detection** → identifies gRPC services: `UserService.GetUser`
- **Protocol detection** → identifies WebSocket endpoints: `/ws/notifications`
- **Protocol detection** → identifies message queues: `kafka://order-events`
- **Protocol detection** → identifies database connections: `postgresql://users-db`
- **Protocol detection** → identifies load balancers: `nginx://sales-backend-lb`, `k8s-ingress://sales-ingress`
- Verify JSON files created in `~/.adalflow/services/` with complete protocol information
- Service registry updated with comprehensive communication details
- UI displays protocol summary: "REST + gRPC + WebSocket + Kafka + Load Balancer"

**User Value**: Start organizing repositories into logical service groups with immediate understanding of all communication protocols, load balancing strategies, and integration patterns

---

### **Step 2: Service Dashboard (Week 2)**
**Goal**: Users can visualize their services and grouped repositories

**Data Available**: Service groupings, repository metadata  
**BAML Available**: Individual repo enrichment per repository

**Frontend Changes:**
- New service dashboard page (`/services`)
- List all services with repository counts
- Service detail view showing grouped repositories
- Basic service information display

**Backend Changes:**
- `GET /api/services/{id}` endpoint for service details
- Service metadata retrieval with repository information
- Repository list with basic service context

**Test Criteria:**
- Navigate to services page → see all created services
- Click "Sales Service" → see assigned repositories
- Service shows correct repository count and metadata

**User Value**: Visual organization and overview of service ecosystem

---

### **Step 3: Service-Aware Chat (Week 3)**
**Goal**: Chat responses include service context using existing BAML intelligence

**Data Available**: Service groupings + existing repo BAML enrichment (77KB per repo)  
**BAML Available**: Existing `b.AnalyzeCode` function with service context capability

**Backend Changes:**
```python
# Enhance existing chat with service awareness
async def service_aware_chat(question: str, repo_context: str):
    # 1. Check if repo belongs to a service
    service = get_service_for_repo(repo_context)
    
    if service:
        # 2. Load existing BAML enrichment for all service repos
        service_repo_data = []
        for repo_url in service.repositories:
            repo_enrichment = load_existing_enrichment(repo_url)  # Our 77KB files
            service_repo_data.append(repo_enrichment)
        
        # 3. Use existing BAML with service context
        response = await b.AnalyzeCode(
            question=question,
            primary_repo=repo_context,
            service_name=service.name,
            related_repos=service_repo_data
        )
        
        return f"In {service.name}: {response}"
    else:
        # Regular single-repo chat (existing behavior)
        return await regular_chat(question, repo_context)
```

**Test Criteria:**
- Ask: "How does authentication work in sales-backend?"
- Response includes: "In Sales Service: The sales-backend uses OAuth2... This connects to sales-frontend and other service components..."
- Service context enhances response quality

**User Value**: Richer, context-aware responses that understand repository relationships within services

---

### **Step 4: BAML Question Analysis (Week 4)**  
**Goal**: System can intelligently analyze question scope and intent

**Data Available**: Service metadata, repository enrichment, conversation context  
**BAML Available**: New dedicated `AnalyzeUserQuestion` function

**Backend Changes:**
- Implement new BAML function:
```python
def AnalyzeUserQuestion(
    question: str,
    available_services: list[str],
    available_repositories: list[str]
) -> QuestionAnalysis
```
- Question scope detection (SERVICE_LEVEL, REPO_SPECIFIC, CROSS_REPO)
- Intelligent routing logic based on analysis

**Test Criteria:**
- Ask: "How does Sales Service work?" → detects SERVICE_LEVEL scope
- Ask: "How does sales-backend work?" → detects REPO_SPECIFIC scope  
- Ask: "How do the frontend and backend communicate?" → detects CROSS_REPO scope

**User Value**: Smarter question understanding and more accurate responses

---

### **Step 5: Enhanced Service Dashboard with BAML Insights (Week 5)**
**Goal**: Rich service visualization using BAML analysis of grouped repositories

**Data Available**: Service groupings + all repo BAML analyses  
**BAML Available**: Existing functions + service overview generation

**Frontend Changes:**
- Interactive service architecture diagram
- Technology stack visualization from repo analyses
- Service health overview from BAML insights
- Repository role display (detected from BAML analysis)

**Backend Changes:**
```python
# Generate service insights from existing repo BAML data
async def generate_service_overview(service_id: str):
    repos = get_service_repos(service_id)
    repo_analyses = [load_repo_enrichment(repo) for repo in repos]
    
    # Use existing BAML to understand service architecture
    overview = await b.AnalyzeCode(
        prompt="Analyze this service architecture from these repository analyses",
        repo_analyses=repo_analyses,
        analysis_focus="service_architecture"
    )
    
    return overview
```

**Test Criteria:**
- Service dashboard shows technology stack summary (Python, React, etc.)
- Visual diagram displays repository relationships
- Service health score based on BAML analysis

**User Value**: Rich architectural insights and visual service understanding

---

### **Step 6: Smart Data Loading with BAML (Week 6)**
**Goal**: BAML intelligently determines which data to load based on questions

**Data Available**: All previous data + question analysis  
**BAML Available**: New `DetermineDataSources` function

**Backend Changes:**
- Implement new BAML function:
```python
def DetermineDataSources(
    question_analysis: QuestionAnalysis,
    service_metadata: dict
) -> DataSourcePlan
```
- Optimized data loading based on BAML intelligence
- Performance improvements through targeted loading

**Test Criteria:**
- Service question → loads service metadata + relevant repository enrichments only
- Repository question → loads specific repo + service context
- Cross-repo question → loads multiple targeted repositories

**User Value**: Faster responses and improved system performance

---

### **Step 7: Auto-Detection of Repository Connections (Week 7)**
**Goal**: BAML automatically detects relationships between repositories

**Data Available**: Repository code content + existing analyses  
**BAML Available**: New `DetectRepoConnections` function

**Backend Changes:**
- Implement connection detection BAML function
- Scan repositories for API endpoints, imports, references
- Generate suggested connections for user confirmation
- Update service metadata with detected relationships

**Test Criteria:**
- Add new repository → system suggests connections to existing repos
- Detection finds API calls, shared dependencies, common configurations
- User can confirm, edit, or reject suggested connections

**User Value**: Reduced manual configuration and automatic relationship discovery

---

### **Step 8: Full Service Intelligence Synthesis (Week 8)**
**Goal**: Complete BAML-powered service ecosystem understanding

**Data Available**: All service and repository data + relationships  
**BAML Available**: Complete suite including `SynthesizeServiceResponse`

**Backend Changes:**
- Implement comprehensive response synthesis:
```python
def SynthesizeServiceResponse(
    original_question: str,
    question_analysis: QuestionAnalysis,
    service_data: dict,
    repo_data: list[dict]
) -> IntelligentResponse
```
- Cross-service analysis capabilities
- Advanced service health and performance insights
- Comprehensive architectural recommendations

**Test Criteria:**
- Complex service questions receive comprehensive, multi-repository answers
- Cross-service performance analysis and recommendations
- Advanced architectural insights and optimization suggestions

**User Value**: Complete service ecosystem intelligence with expert-level insights

---

## 🎯 **Deployment Success Criteria**

### **Each Step Must Achieve:**
- ✅ **Immediate User Value**: Tangible improvement in user experience
- ✅ **Technical Validation**: All functionality works as specified  
- ✅ **Data Integrity**: Proper storage and retrieval of service metadata
- ✅ **Performance**: No degradation of existing functionality
- ✅ **Foundation Building**: Enables subsequent steps to build upon

### **Rollback Strategy:**
- Each step is isolated and can be reverted independently
- Service functionality is additive - never breaks existing repo functionality
- Database migrations are backwards compatible
- Feature flags enable selective rollout

---

## ✅ **Next Steps**

1. **Validate BAML-Powered Design**: Review complete service intelligence architecture
2. **Implement Service Registry**: JSON-based lightweight service metadata storage
3. **Develop Core BAML Functions**: AnalyzeUserQuestion, DetermineDataSources, SynthesizeServiceResponse
4. **Create Service Management UI**: Service creation, repo assignment, relationship editing
5. **Enhance API Layer**: BAML-powered service-aware endpoints and WebSocket integration
6. **Implement BAML Detection**: Auto-detect repo relationships using BAML intelligence

---

## 🎯 **Key Architectural Principles**

### **BAML-First Intelligence**
- **All intelligence routing** powered by BAML LLM functions, not hard-coded rules
- **Adaptive and contextual** understanding of complex, nuanced questions
- **Natural language** processing for human-like interaction
- **Intelligent inference** of relationships and implications

### **Hybrid Data Architecture**
- **Lightweight service metadata** (JSON) for fast service operations
- **Rich repository intelligence** (FAISS) for deep technical insights
- **Optimized data loading** based on BAML intelligence routing
- **Scalable approach** supporting large service ecosystems

### **Intelligent User Experience**
- **Service-aware chat** that understands context and relationships
- **Cross-repository insights** from service-level perspective
- **External agent integration** with same BAML intelligence
- **Adaptive responses** that improve with usage

---

**🎯 This comprehensive plan evolves DeepWiki from single-repository intelligence to a complete BAML-powered service ecosystem platform with truly intelligent query routing, contextual understanding, and adaptive response synthesis capabilities.** 