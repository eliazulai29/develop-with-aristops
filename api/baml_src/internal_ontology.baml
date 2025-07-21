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

enum QualityIssue {
  HIGH_COMPLEXITY
  SECURITY_VULNERABILITY
  PERFORMANCE_BOTTLENECK
  CODE_DUPLICATION
  POOR_ERROR_HANDLING
  TIGHT_COUPLING
  LOW_COHESION
  MISSING_TESTS
  HARDCODED_VALUES
  LONG_PARAMETER_LIST
}

class CodeComponent {
  name string
  type ComponentType
  sourceFile string
  description string
  snippet string
  complexity "low" | "medium" | "high"
  dependencies string[] @description("Names of other components this component depends on")
  
  // Enhanced analysis fields
  purpose string @description("What this component is responsible for")
  publicInterface string[] @description("Public methods/functions exposed")
  qualityIssues QualityIssue[] @description("Identified code quality issues")
  refactoringOpportunities string[] @description("Suggested improvements")
  testability "excellent" | "good" | "poor" @description("How testable this component is")
  reusability "high" | "medium" | "low" @description("How reusable this component is")
}

class Dependency {
  sourceComponent string @description("Name of the source component")
  targetComponent string @description("Name of the target component")
  type string @description("Type of dependency: 'calls', 'imports', 'inherits', etc.")
  description string
  strength "strong" | "medium" | "weak" @description("How tightly coupled this dependency is")
  direction "unidirectional" | "bidirectional" @description("Direction of the dependency")
}

class ArchitecturalInsight {
  pattern ArchitecturalPattern @description("Detected architectural pattern")
  confidence "high" | "medium" | "low" @description("Confidence in pattern detection")
  description string @description("How this pattern is implemented")
  adherence "excellent" | "good" | "partial" | "poor" @description("How well the pattern is followed")
  improvements string[] @description("Suggestions for better pattern implementation")
}

class SecurityAnalysis {
  vulnerabilities string[] @description("Potential security issues found")
  securityPatterns string[] @description("Security patterns identified")
  recommendations string[] @description("Security improvement recommendations")
  dataFlowRisks string[] @description("Data flow security concerns")
}

class PerformanceInsight {
  bottlenecks string[] @description("Identified performance bottlenecks")
  optimizationOpportunities string[] @description("Performance optimization suggestions")
  scalabilityConcerns string[] @description("Scalability issues")
  resourceUsage string @description("Resource usage patterns")
}

class TestingInsight {
  testCoverage "high" | "medium" | "low" | "unknown" @description("Estimated test coverage")
  testableComponents string[] @description("Well-testable components")
  hardToTestComponents string[] @description("Components that are hard to test")
  testingRecommendations string[] @description("Testing improvement suggestions")
  missingTestTypes string[] @description("Types of tests that appear to be missing")
}

class OperationalInsight {
  configurationFiles string[] @description("Configuration files found")
  environmentDependencies string[] @description("Environment-specific dependencies")
  deploymentConsiderations string[] @description("Deployment-related insights")
  monitoringOpportunities string[] @description("Monitoring and observability suggestions")
  maintenanceComplexity "low" | "medium" | "high" @description("Maintenance complexity")
}

class CodeAnalysis {
  components CodeComponent[]?
  dependencies Dependency[]?
  overallSummary string? @description("High-level summary of the code structure")
  
  // Enhanced analysis sections
  architecture ArchitecturalInsight? @description("Architectural pattern analysis")
  security SecurityAnalysis? @description("Security analysis")
  performance PerformanceInsight? @description("Performance analysis")
  testing TestingInsight? @description("Testing analysis")
  operations OperationalInsight? @description("Operational considerations")
  
  // Quick insights for external agents
  keyInsights string[] @description("Top 5 most important insights for this codebase")
  debuggingTips string[] @description("Tips for debugging this codebase")
  refactoringPriorities string[] @description("Top refactoring priorities")
  howToQuestions string[] @description("Common 'how to' questions this analysis can answer")
  whereToLook string[] @description("Where to look for specific functionality")
  whyDecisions string[] @description("Explanations for architectural decisions")
}

// Enhanced main analysis function
function AnalyzeCode(code: string) -> CodeAnalysis {
  client "openai/gpt-4o"
  prompt #"
    You are a senior software architect and code analyst. Perform a comprehensive analysis of the provided codebase.

    Your analysis should include:

    1. **Component Analysis**: Identify all functions, classes, modules, services, configs, tests, middleware, and utilities.
    2. **Dependency Mapping**: Map all relationships between components, including their strength and direction.
    3. **Architectural Patterns**: Detect architectural patterns like MVC, microservices, layered architecture, etc.
    4. **Security Analysis**: Identify potential vulnerabilities, security patterns, and recommendations.
    5. **Performance Insights**: Spot performance bottlenecks and optimization opportunities.
    6. **Testing Assessment**: Evaluate test coverage and testability.
    7. **Operational Considerations**: Analyze configuration, deployment, and maintenance aspects.
    8. **Quality Issues**: Identify code smells, complexity issues, and refactoring opportunities.

    Focus on providing insights that would help developers answer:
    - **HOW**: How does this code work? How are components connected?
    - **WHERE**: Where to find specific functionality? Where are the pain points?
    - **WHY**: Why were certain architectural decisions made?

    This analysis will be used by:
    - Developers asking questions about the codebase
    - External coding agents needing context
    - Debugging and refactoring tasks
    - Code reviews and documentation

    Be thorough but practical. Focus on actionable insights.

    {{ ctx.output_format }}

    Code to analyze:
    {{ _.role("user") }} {{ code }}
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

def initialize_system():
    db = DatabaseConnection()
    user_manager = UserManager(db)
    return user_manager
"#
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
