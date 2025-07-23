// ===========================================
// STRUCTURAL CODE ANALYSIS ONTOLOGY  
// ===========================================

enum ComponentType {
  FUNCTION
  CLASS
  MODULE
  FILE
  API_ENDPOINT
  SERVICE
  CONFIG
  TEST
  MIDDLEWARE
  UTILS
}

enum ArchitecturalPattern {
  MVC
  MICROSERVICES
  MONOLITH
  LAYERED
  EVENT_DRIVEN
  REPOSITORY
  FACTORY
  SINGLETON
  OBSERVER
  UNKNOWN
}

enum TechnologyStack {
  PYTHON
  NODEJS_JAVASCRIPT
  GO
  JAVA_MAVEN
  RUST
  DOTNET_CSHARP
  PHP
  RUBY
  RESEARCH_PROJECT
  DATA_SCIENCE
  UNKNOWN
}

enum RepositoryRole {
  BACKEND_SERVICE
  FRONTEND_APP
  API_GATEWAY
  DATABASE_SERVICE
  MESSAGE_QUEUE
  ANALYTICS_SERVICE
  MICROSERVICE
  MONOLITH
  LIBRARY
  RESEARCH_PROJECT
  DATA_SCIENCE
  UNKNOWN
}

class CodeComponent {
  name string
  type ComponentType
  sourceFile string
  description string
  snippet string
  complexity "low" | "medium" | "high"
  dependencies string[] @description("Names of other components this depends on")
  purpose string @description("Component's primary responsibility")
  publicInterface string[] @description("Public methods/functions exposed")
  architecturalRole string @description("Role in overall architecture")
  interactionPatterns string[] @description("Component interaction patterns")
}

class Dependency {
  sourceComponent string @description("Source component name")
  targetComponent string @description("Target component name")
  type string @description("Dependency type: 'calls', 'imports', 'inherits', etc.")
  description string
  strength "strong" | "medium" | "weak" @description("Coupling strength")
  direction "unidirectional" | "bidirectional"
}

class ArchitecturalInsight {
  pattern ArchitecturalPattern
  confidence "high" | "medium" | "low"
  description string
  adherence "excellent" | "good" | "partial" | "poor"
  improvements string[]
}

class CodeAnalysis {
  components CodeComponent[]?
  dependencies Dependency[]?
  overallSummary string? @description("High-level code structure summary")
  architecture ArchitecturalInsight?
  keyInsights string[] @description("Top 5 structural insights")
  entryPoints string[] @description("Main entry points")
  coreComponents string[] @description("Critical components and purpose")
  howToQuestions string[] @description("Common usage questions")
  whereToLook string[] @description("Functionality location guide")
  whyDecisions string[] @description("Architectural decision rationale")
  navigationTips string[] @description("Codebase navigation guidance")
}

// Structural analysis function - focused on architecture and navigation
function AnalyzeCode(code: string) -> CodeAnalysis {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert software architect performing structural analysis of code. Your analysis focuses on architecture, navigation, and service-level understanding.

    ANALYSIS OBJECTIVES:
    1. Map the codebase structure and component relationships
    2. Identify architectural patterns and design decisions
    3. Create navigation guidance for developers
    4. Document component interactions and dependencies
    5. Highlight entry points and core components

    ANALYSIS METHODOLOGY:
    1. First scan: Identify all components and their basic properties
    2. Second scan: Map dependencies and relationships
    3. Third scan: Detect architectural patterns
    4. Fourth scan: Document navigation paths and entry points
    5. Final scan: Compile insights and structural recommendations

    KEY FOCUS AREAS:
    - Component identification and classification
    - Dependency mapping and strength assessment
    - Architectural pattern recognition
    - Navigation path documentation
    - Entry point identification
    - Core component highlighting

    EXCLUDE FROM ANALYSIS:
    - Security analysis
    - Performance optimization
    - Test coverage
    - Code quality issues
    - Deployment concerns
    
    {{ ctx.output_format }}

    {{ _.role("user") }}
    Analyze this code:
    {{ code }}
  "#
}

// Specialized analysis for specific aspects
function AnalyzeComplexity(component: CodeComponent) -> string {
  client "openai/gpt-4o-mini"
  prompt #"
    Analyze the complexity of this code component and provide a detailed explanation.
    Consider factors like cyclomatic complexity, number of dependencies, and code structure.

    {{ ctx.output_format }}

    Component details:
    {{ _.role("user") }} {{ component }}
  "#
}

// === SERVICE-LEVEL INTELLIGENCE ONTOLOGY ===

class CommunicationProtocol {
  protocol_type string
  endpoints string[]
  configuration_details string?
  evidence_files string[]
}

class TechStackAnalysis {
  primary_stack TechnologyStack
  secondary_stacks TechnologyStack[]
  frameworks string[]
  evidence_files string[]
  confidence "high" | "medium" | "low"
  reasoning string
}

class RepositoryClassification {
  role RepositoryRole
  tech_stack TechStackAnalysis
  communication_protocols CommunicationProtocol[]
  deployment_patterns string[]
  confidence "high" | "medium" | "low"
  reasoning string
}

function AnalyzeRepository(
  file_structure: string,
  repository_content: string
) -> RepositoryClassification {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert software architect analyzing a repository for service classification.
    
    Focus on identifying:
    1. Technology stack and frameworks
    2. Repository role in service architecture
    3. Communication protocols
    4. Deployment patterns

    Base your analysis only on observed patterns and evidence in the code.
    Provide confidence levels and reasoning for each classification.

    {{ ctx.output_format }}

    {{ _.role("user") }}
    File Structure:
    {{ file_structure }}

    Repository Content:
    {{ repository_content }}
  "#
}

function ClassifyServiceRelationships(
  service_repositories: string,
  repository_classifications: string
) -> string {
  client "CustomGPT4o"
  prompt #"
    You are an expert system architect analyzing relationships between repositories in a service.
    
    TASK: Analyze the relationships and dependencies between repositories within a service.
    
    Service Repositories:
    {{ service_repositories }}
    
    Repository Classifications:
    {{ repository_classifications }}
    
    ANALYSIS GOALS:
    1. Identify communication flows between repositories
    2. Detect dependency relationships
    3. Suggest architectural improvements
    4. Identify potential security or performance concerns
    
    Provide a detailed analysis of how these repositories work together as a cohesive service.
    Focus on production architecture patterns and best practices.
  "#
}

// =========================================== 
// INTELLIGENT FILE FILTERING FOR LARGE REPOS
// ===========================================

enum FileImportance {
  CRITICAL      // README, main entry points, core config
  HIGH          // Key modules, API definitions, main components  
  MEDIUM        // Supporting files, utilities, tests
  LOW           // Generated files, docs, examples
  SKIP          // Build artifacts, cache, node_modules
}

enum FileBatchCategory {
  CORE_STRUCTURE    // Entry points, main configs, README
  API_LAYER         // Routes, controllers, API definitions
  BUSINESS_LOGIC    // Services, models, core algorithms
  USER_INTERFACE    // Components, pages, styling
  INFRASTRUCTURE    // Docker, CI/CD, deployment configs
  TESTING           // Test files and configurations
  DOCUMENTATION     // Docs, examples, guides
  SUPPORTING        // Utils, helpers, constants
}

class FileMetadata {
  path string
  importance FileImportance
  category FileBatchCategory
  reasoning string @description("Why this file was categorized this way")
  estimated_tokens int @description("Rough estimate of content size")
  dependencies string[] @description("Files this depends on or imports")
}

class FileBatch {
  category FileBatchCategory
  files FileMetadata[]
  priority_order int @description("1=process first, higher=process later")
  description string @description("What this batch represents")
  estimated_total_tokens int
}

class RepositoryFilePlan {
  total_files int
  repository_type TechnologyStack
  analysis_strategy string @description("Recommended approach for this repo size/type")
  priority_batches FileBatch[]
  skipped_patterns string[] @description("File patterns that can be safely ignored")
  estimated_analysis_time_minutes int
}

function PrioritizeRepositoryFiles(
  file_structure: string,
  readme_content: string
) -> RepositoryFilePlan {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert software architect specializing in large-scale repository analysis.
    
    TASK: Analyze a repository's file structure and create an intelligent processing plan.
    
    OBJECTIVES:
    1. Categorize ALL files by importance and functional area
    2. Create processing batches that respect token limits (~25,000 tokens per batch)
    3. Prioritize files that are most important for understanding the project
    4. Skip files that don't contribute to architectural understanding
    
    CRITICAL RULES:
    - ALWAYS include: README, package.json, main entry points, core configs
    - Group related files together (e.g., all API routes in one batch)
    - Estimate tokens conservatively (source files: ~100 tokens per file, large files: 500+)
    - Skip: node_modules, .git, build outputs, cache directories
    - Prioritize business logic over tests and documentation
    
    {{ ctx.output_format }}
    
    {{ _.role("user") }}
    Repository File Structure:
    {{ file_structure }}
    
    README Content (for context):
    {{ readme_content }}
  "#
}

function AnalyzeRepositoryBatch(
  batch_description: string,
  file_content: string,
  context_from_previous_batches: string
) -> string {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are analyzing a specific batch of files from a large repository.
    
    FOCUS: This batch represents {{ batch_description }}.
    
    CONTEXT from previous batches:
    {{ context_from_previous_batches }}
    
    TASK: Analyze these files and provide insights that will contribute to:
    1. Repository classification (role, tech stack, protocols)
    2. Architectural understanding 
    3. Wiki structure planning
    
    Keep your analysis concise but insightful. Focus on patterns, dependencies,
    and architectural decisions that would be valuable for documentation.
    
    {{ _.role("user") }}
    Files in this batch:
    {{ file_content }}
  "#
}

// =========================================== 
// INTELLIGENT DECISION FUNCTIONS (NO HARDCODING)
// ===========================================

class FileClassification {
  path string
  importance FileImportance
  reasoning string @description("Why this file has this importance level")
  estimated_content_value int @description("1-10 scale of content value for understanding the project")
  should_include_in_sample bool
}

class RepositoryAnalysisStrategy {
  recommended_approach "standard" | "progressive" | "lightweight"
  reasoning string @description("Why this approach is recommended")
  estimated_complexity_level "low" | "medium" | "high" | "very_high"
  max_files_for_analysis int @description("Recommended maximum files to analyze")
  batch_size_recommendation int @description("Optimal batch size if using progressive approach")
  priority_focus_areas string[] @description("Areas to prioritize for this specific repository")
}

class TokenManagementPlan {
  total_estimated_tokens int
  per_file_token_estimate int
  recommended_batch_size int
  max_context_window int
  safety_margin_percentage int
  chunking_strategy string @description("How to chunk content if needed")
}

function ClassifyRepositoryFiles(
  file_list: string,
  readme_content: string,
  repository_context: string
) -> FileClassification[] {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert software architect analyzing a repository's files to determine their importance for understanding the project.
    
    NO HARDCODED RULES - Base your decisions on the actual project context and content.
    
    TASK: Classify each file's importance for understanding this specific repository:
    - CRITICAL: Essential for understanding the project (varies by project type)
    - HIGH: Important for architecture understanding  
    - MEDIUM: Useful supporting files
    - LOW: Nice to have but not essential
    - SKIP: Not valuable for analysis
    
    Consider:
    - Project type and technology stack
    - File relationships and dependencies
    - Actual content value (not just filename patterns)
    - Repository structure and organization
    
    {{ ctx.output_format }}
    
    {{ _.role("user") }}
    Repository Files:
    {{ file_list }}
    
    README Content:
    {{ readme_content }}
    
    Repository Context:
    {{ repository_context }}
  "#
}

function DetermineRepositoryStrategy(
  file_count: int,
  repository_structure: string,
  readme_content: string,
  sample_files: string
) -> RepositoryAnalysisStrategy {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert at analyzing repositories and determining the optimal analysis approach.
    
    NO HARDCODED THRESHOLDS - Make decisions based on actual repository characteristics.
    
    TASK: Determine the best analysis strategy for this repository:
    - standard: Single-pass analysis (for simpler/smaller repos)
    - progressive: Multi-batch analysis (for complex/large repos)  
    - lightweight: Minimal analysis (for very large/simple repos)
    
    Consider:
    - Repository complexity (not just size)
    - Technology stack complexity
    - Code organization and structure
    - Actual content density and value
    
    {{ ctx.output_format }}
    
    {{ _.role("user") }}
    File Count: {{ file_count }}
    
    Repository Structure:
    {{ repository_structure }}
    
    README Content:
    {{ readme_content }}
    
    Sample Files:
    {{ sample_files }}
  "#
}

function OptimizeTokenUsage(
  estimated_content_size: int,
  target_model: string,
  analysis_goals: string
) -> TokenManagementPlan {
  client "CustomGPT4o"
  prompt #"
    {{ _.role("system") }}
    You are an expert at optimizing LLM token usage for large-scale code analysis.
    
    NO HARDCODED LIMITS - Adapt to the specific model and content characteristics.
    
    TASK: Create an optimal token management plan that:
    - Maximizes analysis quality within model constraints
    - Provides appropriate safety margins
    - Suggests intelligent chunking strategies
    - Adapts to the specific model's capabilities
    
    {{ ctx.output_format }}
    
    {{ _.role("user") }}
    Estimated Content Size: {{ estimated_content_size }} characters
    
    Target Model: {{ target_model }}
    
    Analysis Goals:
    {{ analysis_goals }}
  "#
}

// Tests
test BasicAnalysis {
  functions [AnalyzeCode]
  args {
    code #"
class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        
    def create_user(self, name, email):
        return self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [name, email]
        )
"#
  }
}

test RepositoryAnalysisTest {
  functions [AnalyzeRepository]
  args {
    file_structure "test-repo/\n  main.py\n  requirements.txt\n  README.md"
    repository_content "=== main.py ===\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello World'"
  }
}

test NoDependencies {
  functions [AnalyzeCode]
  args {
    code #"
// A simple script with no internal dependencies
function greet(name) {
  return `Hello, ${name}`;
}

function farewell(name) {
  return `Goodbye, ${name}`;
}
"#
  }
}

test EmptyInput {
  functions [AnalyzeCode]
  args {
    code ""
  }
}
