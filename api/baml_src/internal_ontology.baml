enum ComponentType {
  FUNCTION
  CLASS
  MODULE
  FILE
  API_ENDPOINT
}

class CodeComponent {
  name string
  type ComponentType
  sourceFile string
  description string
  snippet string
  complexity "low" | "medium" | "high"
  dependencies string[] @description("Names of other components this component depends on")
}

class Dependency {
  sourceComponent string @description("Name of the source component")
  targetComponent string @description("Name of the target component")
  type string @description("Type of dependency: 'calls', 'imports', 'inherits', etc.")
  description string
}

class CodeAnalysis {
  components CodeComponent[]?
  dependencies Dependency[]?
  overallSummary string? @description("High-level summary of the code structure")
}

// Main analysis function
function AnalyzeCode(code: string) -> CodeAnalysis {
  client "openai/gpt-4o"
  prompt #"
    Analyze the provided code and create a detailed breakdown of its components and dependencies.
    Focus on identifying functions, classes, and their relationships.
    
    {{ ctx.output_format }}

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
