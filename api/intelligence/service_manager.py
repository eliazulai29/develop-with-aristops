"""
Service Management for Multi-Repository Intelligence

Handles service creation, repository assignment, and communication protocol detection
for the service-level intelligence system.
"""
import os
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# BAML client for intelligent analysis
try:
    from api.baml_client.async_client import b
    BAML_AVAILABLE = True
    logger.info("BAML client loaded successfully")
except ImportError as e:
    logger.warning(f"BAML client not available: {e}")
    BAML_AVAILABLE = False
    b = None


class ServiceManager:
    """
    Manages services and repository assignments with protocol detection.
    
    Provides intelligent service management capabilities including:
    - Service creation and metadata management
    - Repository assignment to services
    - Communication protocol detection
    - Service registry maintenance
    """
    
    def __init__(self):
        """Initialize ServiceManager with proper directory structure."""
        self.adalflow_root = Path.home() / ".adalflow"
        self.services_dir = self.adalflow_root / "services"
        self.repos_dir = self.adalflow_root / "repos"
        
        # Ensure directories exist
        self.services_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.services_dir / "services_registry.json"
        
        # Initialize BAML client for intelligent analysis
        if BAML_AVAILABLE:
            self.baml_client = b
            logger.info("BAML client initialized successfully in ServiceManager")
        else:
            self.baml_client = None
            logger.warning("BAML client not available - intelligent analysis disabled")
        
        logger.info(f"ServiceManager initialized with services directory: {self.services_dir}")
        
        # Self-validation: Check for hardcoded patterns
        self._validate_no_hardcoding()
    
    def _validate_no_hardcoding(self):
        """
        Self-validation to ensure no hardcoded logic is present.
        Helps maintain BAML-driven approach and prevent regression.
        """
        validation_passed = True
        warnings = []
        
        # Check this file for common hardcoding patterns
        current_file = __file__
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patterns that indicate hardcoding
            hardcode_patterns = [
                (r'\.py|\.js|\.ts.*=', "File extension hardcoding detected"),
                (r'THRESHOLD\s*=\s*\d+', "Hardcoded threshold detected"),
                (r'if.*>\s*\d{3,}', "Hardcoded numeric comparison detected"),
                (r'node_modules|__pycache__.*in.*path', "Hardcoded directory patterns detected"),
                (r'score\s*\+=\s*\d+', "Hardcoded scoring logic detected"),
                (r'MAX_.*=\s*\d+', "Hardcoded maximum values detected")
            ]
            
            for pattern, message in hardcode_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if it's in a comment or validation context
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip if it's in a comment or this validation method
                            if ('#' in line or 
                                'def _validate_no_hardcoding' in lines[max(0, i-5):i+5] or
                                'hardcode_patterns' in line):
                                continue
                            warnings.append(f"Line {i+1}: {message}")
                            validation_passed = False
            
            if validation_passed:
                logger.info("✅ Self-validation passed: No hardcoded logic detected")
            else:
                logger.warning(f"⚠️ Self-validation warnings: {warnings}")
                logger.warning("🔍 Consider moving logic to BAML functions")
                
        except Exception as e:
            logger.warning(f"Could not perform self-validation: {e}")
        
        return validation_passed
    
    def create_service(self, name: str, description: str = "", owner: str = "") -> str:
        """
        Create a new service with metadata.
        
        Args:
            name: Human-readable service name (e.g., "Sales Service")
            description: Optional service description
            owner: Optional owner/team identifier
            
        Returns:
            str: Unique service ID
            
        Raises:
            ValueError: If service name already exists
        """
        if not name or not name.strip():
            raise ValueError("Service name cannot be empty")
        
        # Generate unique service ID
        service_id = self._generate_service_id(name)
        
        # Check if service already exists
        if self._service_exists(service_id):
            raise ValueError(f"Service with name '{name}' already exists")
        
        # Create service metadata
        service_data = {
            "id": service_id,
            "name": name.strip(),
            "description": description.strip(),
            "owner": owner.strip(),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "repositories": {},
            "repository_count": 0
        }
        
        # Save service file
        service_file = self.services_dir / f"{service_id}.json"
        try:
            with open(service_file, 'w', encoding='utf-8') as f:
                json.dump(service_data, f, indent=2, ensure_ascii=False)
            
            # Update registry
            self._update_registry()
            
            logger.info(f"Created service '{name}' with ID: {service_id}")
            return service_id
            
        except Exception as e:
            logger.error(f"Failed to create service '{name}': {e}")
            raise RuntimeError(f"Failed to create service: {str(e)}")
    
    def list_services(self) -> List[Dict[str, Any]]:
        """
        List all available services.
        
        Returns:
            List of service metadata dictionaries
        """
        try:
            if not self.registry_file.exists():
                return []
            
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            return registry.get("services", [])
            
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            return []
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed service information.
        
        Args:
            service_id: Unique service identifier
            
        Returns:
            Service data dictionary or None if not found
        """
        service_file = self.services_dir / f"{service_id}.json"
        
        if not service_file.exists():
            return None
        
        try:
            with open(service_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load service {service_id}: {e}")
            return None
    
    def find_service_by_repo_url(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """
        Find service that contains the specified repository.
        
        Args:
            repo_url: Repository URL to search for
            
        Returns:
            Service data dictionary with service_id, or None if not found
        """
        try:
            # Normalize repo URL for comparison
            normalized_url = repo_url.rstrip('/').replace('.git', '')
            
            # Search through all services
            for service_file in self.services_dir.glob("*.json"):
                try:
                    with open(service_file, 'r', encoding='utf-8') as f:
                        service_data = json.load(f)
                    
                    # Check if this service has repositories
                    repositories = service_data.get("repositories", {})
                    
                    # Search for matching repository URL
                    for repo_key, repo_info in repositories.items():
                        # Normalize stored URL for comparison
                        stored_url = repo_info.get("url", repo_key).rstrip('/').replace('.git', '')
                        
                        if normalized_url == stored_url:
                            # Found matching repository
                            service_data["service_id"] = service_file.stem  # Add service_id to response
                            logger.info(f"Found repository {repo_url} in service {service_file.stem}")
                            return service_data
                            
                except Exception as e:
                    logger.error(f"Error reading service file {service_file}: {e}")
                    continue
            
            logger.info(f"No service found containing repository: {repo_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for repository {repo_url}: {e}")
            return None
    
    async def assign_repo_to_service(self, service_id: str, repo_url: str) -> bool:
        """Assign repository to service with BAML-powered analysis."""
        try:
            logger.info(f"🔍 DEBUG: Starting assign_repo_to_service - service_id: {service_id}, repo_url: {repo_url}")
            
            # Validate inputs
            if not service_id or not repo_url:
                logger.error(f"🔍 DEBUG: Invalid inputs - service_id: {service_id}, repo_url: {repo_url}")
                return False
            
            # Check if service exists
            service_file = self.services_dir / f"{service_id}.json"
            if not service_file.exists():
                logger.error(f"🔍 DEBUG: Service file does not exist: {service_file}")
                return False
            
            # Load service data
            with open(service_file, 'r', encoding='utf-8') as f:
                service_data = json.load(f)
            logger.info(f"🔍 DEBUG: Loaded service data: {service_data.get('name', 'Unknown')}")
            
            # Check if repository already exists in service
            if repo_url in service_data.get("repositories", {}):
                logger.info(f"🔍 DEBUG: Repository {repo_url} already exists in service {service_id}")
                return True
            
            # Phase 1: Detect repository size and choose analysis strategy
            logger.info(f"🔍 DEBUG: Detecting repository size and choosing analysis strategy")
            analysis_strategy = await self._detect_analysis_strategy(repo_url)
            logger.info(f"🔍 DEBUG: Selected analysis strategy: {analysis_strategy}")
            
            # Phase 2: Perform appropriate BAML analysis
            if analysis_strategy == "progressive":
                logger.info(f"🔍 DEBUG: Using progressive BAML analysis for large repository")
                analysis_success = await self._analyze_large_repository_with_progressive_baml(repo_url, service_data, service_file)
            else:
                logger.info(f"🔍 DEBUG: Using standard BAML analysis for regular repository")
                analysis_success = await self._analyze_repository_with_baml(repo_url, service_data, service_file)
                
            if analysis_success:
                logger.info(f"🔍 DEBUG: BAML analysis completed successfully")
                # Update registry
                self._update_registry()
                logger.info(f"✅ Successfully assigned repository {repo_url} to service {service_id} with BAML analysis")
                return True
            else:
                logger.warning(f"🔍 DEBUG: BAML analysis failed, but repository was still added with fallback data")
                # Update registry even for fallback data
                self._update_registry()
                logger.info(f"⚠️ Assigned repository {repo_url} to service {service_id} with fallback data")
                return True
                
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error in assign_repo_to_service: {e}")
            logger.error(f"🔍 DEBUG: Exception traceback:", exc_info=True)
            return False
    
    def _generate_service_id(self, name: str) -> str:
        """Generate unique service ID from name."""
        # Convert to lowercase, replace spaces/special chars with hyphens
        base_id = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        base_id = re.sub(r'\s+', '-', base_id.strip())
        
        # Add timestamp for uniqueness
        timestamp = int(time.time())
        return f"{base_id}-{timestamp}"
    
    def _service_exists(self, service_id: str) -> bool:
        """Check if service ID already exists."""
        service_file = self.services_dir / f"{service_id}.json"
        return service_file.exists()
    
    def _update_registry(self) -> None:
        """Update the services registry with current services."""
        try:
            services = []
            
            # Scan all service files
            for service_file in self.services_dir.glob("*.json"):
                if service_file.name == "services_registry.json":
                    continue
                
                try:
                    with open(service_file, 'r', encoding='utf-8') as f:
                        service_data = json.load(f)
                    
                    # Extract summary info for registry
                    services.append({
                        "id": service_data["id"],
                        "name": service_data["name"],
                        "description": service_data.get("description", ""),
                        "owner": service_data.get("owner", ""),
                        "created_at": service_data["created_at"],
                        "last_updated": service_data["last_updated"],
                        "repository_count": service_data.get("repository_count", 0)
                    })
                    
                except Exception as e:
                    logger.warning(f"Skipping invalid service file {service_file}: {e}")
                    continue
            
            # Sort by creation date (newest first)
            services.sort(key=lambda s: s["created_at"], reverse=True)
            
            # Save registry
            registry_data = {
                "services": services,
                "last_updated": datetime.now().isoformat(),
                "total_services": len(services)
            }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Updated services registry with {len(services)} services")
            
        except Exception as e:
            logger.error(f"Failed to update services registry: {e}")
    
    async def _analyze_repository_with_baml(self, repo_url: str, service_data: Dict[str, Any], service_file: Path) -> bool:
        """
        Analyze repository using BAML to determine role, tech stack, and communication protocols.
        
        Args:
            repo_url: Repository URL to analyze
            service_data: Service data dictionary to update
            service_file: Path to service JSON file for saving
            
        Returns:
            bool: True if analysis successful, False otherwise
        """
        try:
            logger.info(f"🔍 DEBUG: Starting BAML analysis for {repo_url}")
            
            # Get repository path
            repo_path = self._get_repo_path(repo_url)
            logger.info(f"🔍 DEBUG: Repository path resolved to: {repo_path}")
            
            if not repo_path or not repo_path.exists():
                logger.warning(f"🔍 DEBUG: Repository path not found or doesn't exist: {repo_path}")
                return False # Changed to return False as per new_code
            
            logger.info(f"🔍 DEBUG: Repository path exists, proceeding with file analysis")
            
            # Collect repository data for BAML analysis
            file_structure = self._collect_file_structure(repo_path)
            repository_content = self._collect_repository_content(repo_path)
            
            logger.info(f"🔍 DEBUG: Collected data - Files: {len(file_structure.splitlines())}, Content: {len(repository_content.splitlines())}")
            
            # Call BAML function with proper parameters
            try:
                logger.info(f"🔍 DEBUG: Calling BAML AnalyzeRepository function")
                logger.info(f"🔍 DEBUG: File structure length: {len(file_structure)} chars")
                logger.info(f"🔍 DEBUG: Repository content length: {len(repository_content)} chars")
                logger.info(f"🔍 DEBUG: File structure preview: {file_structure[:500]}...")
                logger.info(f"🔍 DEBUG: Repository content preview: {repository_content[:1000]}...")
                
                response = await self.baml_client.AnalyzeRepository(
                    file_structure=file_structure,
                    repository_content=repository_content
                )
                logger.info(f"🔍 DEBUG: BAML response received: {type(response)}")
                logger.info(f"🔍 DEBUG: BAML response content: {response}")
                
                if response:
                    logger.info(f"🔍 DEBUG: Response role: {response.role}")
                    logger.info(f"🔍 DEBUG: Response tech_stack: {response.tech_stack}")
                    logger.info(f"🔍 DEBUG: Response communication_protocols: {response.communication_protocols}")
                    logger.info(f"🔍 DEBUG: Response deployment_patterns: {response.deployment_patterns}")
                    logger.info(f"🔍 DEBUG: Response confidence: {response.confidence}")
                    logger.info(f"🔍 DEBUG: Response reasoning: {response.reasoning}")
                    
                    # Convert BAML response to storage format
                    protocols = []
                    if response.communication_protocols:
                        for protocol in response.communication_protocols:
                            protocol_dict = {
                                "protocol_type": protocol.protocol_type,
                                "endpoints": protocol.endpoints,
                                "configuration_details": protocol.configuration_details,
                                "evidence_files": protocol.evidence_files
                            }
                            protocols.append(protocol_dict)
                            logger.info(f"🔍 DEBUG: Converted protocol: {protocol_dict}")
                    
                    tech_stack_dict = {
                        "primary_stack": response.tech_stack.primary_stack,
                        "secondary_stacks": response.tech_stack.secondary_stacks,
                        "frameworks": response.tech_stack.frameworks,
                        "evidence_files": response.tech_stack.evidence_files,
                        "confidence": response.tech_stack.confidence,
                        "reasoning": response.tech_stack.reasoning
                    }
                    logger.info(f"🔍 DEBUG: Converted tech_stack: {tech_stack_dict}")
                    
                    repo_entry = {
                        "url": repo_url,
                        "local_path": str(repo_path),
                        "role": response.role,
                        "tech_stack": tech_stack_dict,
                        "communication_protocols": protocols,
                        "deployment_patterns": response.deployment_patterns,
                        "confidence": response.confidence,
                        "reasoning": response.reasoning,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "enriched": True
                    }
                    logger.info(f"🔍 DEBUG: Final repo_entry before storage: {repo_entry}")
                    
                    # Store in service data
                    service_data["repositories"][repo_url] = repo_entry
                    service_data["repository_count"] = len(service_data["repositories"])
                    service_data["last_updated"] = datetime.now().isoformat()
                    logger.info(f"🔍 DEBUG: Updated service_data repositories count: {service_data['repository_count']}")
                    
                    # Save updated service data
                    with open(service_file, 'w') as f:
                        json.dump(service_data, f, indent=2)
                    logger.info(f"🔍 DEBUG: Service data saved to {service_file}")
                    
                    logger.info(f"BAML detected: Role={repo_entry['role']}, Stack={repo_entry['tech_stack']}, Protocols={protocols}")
                    return True
                else:
                    logger.warning(f"🔍 DEBUG: BAML response was None or empty")
                    return False
                    
            except Exception as baml_error:
                logger.error(f"🔍 DEBUG: BAML analysis failed: {baml_error}")
                logger.error(f"🔍 DEBUG: Exception type: {type(baml_error)}")
                logger.error(f"🔍 DEBUG: Exception details: {str(baml_error)}")
                
                # Store basic repo entry without BAML analysis
                repo_entry = {
                    "url": repo_url,
                    "local_path": str(repo_path),
                    "role": "UNKNOWN",
                    "tech_stack": {
                        "primary_stack": "UNKNOWN",
                        "secondary_stacks": [],
                        "frameworks": [],
                        "evidence_files": [],
                        "confidence": "low",
                        "reasoning": f"BAML analysis failed: {str(baml_error)}"
                    },
                    "communication_protocols": [],
                    "deployment_patterns": [],
                    "confidence": "low",
                    "reasoning": f"BAML analysis failed: {str(baml_error)}",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "enriched": False,
                    "baml_error": str(baml_error)
                }
                logger.info(f"🔍 DEBUG: Fallback repo_entry created: {repo_entry}")
                
                # Store fallback entry
                service_data["repositories"][repo_url] = repo_entry
                service_data["repository_count"] = len(service_data["repositories"])
                service_data["last_updated"] = datetime.now().isoformat()
                
                # Save updated service data
                with open(service_file, 'w') as f:
                    json.dump(service_data, f, indent=2)
                logger.info(f"🔍 DEBUG: Fallback service data saved to {service_file}")
                
                return False
            
        except Exception as e:
            logger.error(f"🔍 DEBUG: Repository analysis failed with error: {type(e).__name__}: {e}")
            logger.error(f"🔍 DEBUG: Full traceback:", exc_info=True)
            return False
    
    async def _analyze_large_repository_with_progressive_baml(self, repo_url: str, service_data: Dict[str, Any], service_file: Path) -> bool:
        """
        Analyze large repository using progressive BAML analysis with intelligent batching.
        
        This method handles repositories that are too large for single-pass analysis by:
        1. Using BAML to prioritize and batch files intelligently
        2. Processing batches sequentially with context accumulation
        3. Building comprehensive analysis from batch results
        
        Args:
            repo_url: Repository URL to analyze
            service_data: Service data dictionary to update
            service_file: Path to service JSON file for saving
            
        Returns:
            bool: True if analysis successful, False otherwise
        """
        try:
            logger.info(f"🔍 DEBUG: Starting progressive BAML analysis for large repository: {repo_url}")
            
            # Get repository path
            repo_path = self._get_repo_path(repo_url)
            if not repo_path or not repo_path.exists():
                logger.warning(f"🔍 DEBUG: Repository path not found: {repo_path}")
                return False
            
            # Phase 1: Generate intelligent file prioritization plan
            logger.info(f"🔍 DEBUG: Phase 1 - Creating intelligent file processing plan")
            file_structure = self._collect_file_structure(repo_path)
            readme_content = self._get_readme_content(repo_path)
            
            logger.info(f"🔍 DEBUG: Calling BAML PrioritizeRepositoryFiles")
            logger.info(f"🔍 DEBUG: File structure length: {len(file_structure)} chars")
            logger.info(f"🔍 DEBUG: README content length: {len(readme_content)} chars")
            
            file_plan = await self.baml_client.PrioritizeRepositoryFiles(
                file_structure=file_structure,
                readme_content=readme_content
            )
            
            logger.info(f"🔍 DEBUG: File plan received - {len(file_plan.priority_batches)} batches planned")
            logger.info(f"🔍 DEBUG: Repository type detected: {file_plan.repository_type}")
            logger.info(f"🔍 DEBUG: Analysis strategy: {file_plan.analysis_strategy}")
            
            # Phase 2: Process batches sequentially with context accumulation
            batch_results = []
            accumulated_context = ""
            
            for i, batch in enumerate(file_plan.priority_batches):
                logger.info(f"🔍 DEBUG: Processing batch {i+1}/{len(file_plan.priority_batches)}: {batch.category}")
                logger.info(f"🔍 DEBUG: Batch contains {len(batch.files)} files, estimated {batch.estimated_total_tokens} tokens")
                
                # Collect content for this batch
                batch_content = self._collect_batch_content(repo_path, batch)
                
                if not batch_content.strip():
                    logger.info(f"🔍 DEBUG: Batch {i+1} has no readable content, skipping")
                    continue
                
                # Analyze this batch with accumulated context
                logger.info(f"🔍 DEBUG: Calling BAML AnalyzeRepositoryBatch for batch {i+1}")
                batch_result = await self.baml_client.AnalyzeRepositoryBatch(
                    batch_description=batch.description,
                    file_content=batch_content,
                    context_from_previous_batches=accumulated_context
                )
                
                logger.info(f"🔍 DEBUG: Batch {i+1} analysis completed")
                batch_results.append({
                    "batch_category": batch.category,
                    "analysis": batch_result
                })
                
                # Accumulate context for next batch (keep it concise)
                accumulated_context += f"\n\n--- {batch.category} Analysis ---\n{batch_result}"
                
                # Limit accumulated context to prevent token overflow
                if len(accumulated_context) > 10000:
                    accumulated_context = accumulated_context[-8000:]  # Keep recent context
            
            # Phase 3: Synthesize final analysis from all batches
            logger.info(f"🔍 DEBUG: Phase 3 - Synthesizing final analysis from {len(batch_results)} batches")
            final_analysis = self._synthesize_progressive_analysis(file_plan, batch_results)
            
            # Phase 4: Store results in service data
            logger.info(f"🔍 DEBUG: Phase 4 - Storing progressive analysis results")
            repo_key = self._get_repo_key(repo_url)
            
            service_data["repositories"][repo_key] = {
                "url": repo_url,
                "analysis_type": "progressive_baml",
                "total_batches_processed": len(batch_results),
                "repository_type": str(file_plan.repository_type),
                "analysis_strategy": file_plan.analysis_strategy,
                **final_analysis
            }
            
            # Save updated service data
            with open(service_file, 'w', encoding='utf-8') as f:
                json.dump(service_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🔍 DEBUG: Progressive analysis completed successfully for {repo_url}")
            return True
            
        except Exception as e:
            logger.error(f"🔍 DEBUG: Progressive repository analysis failed with error: {type(e).__name__}: {e}")
            logger.error(f"🔍 DEBUG: Full traceback:", exc_info=True)
            
            # Store fallback data
            try:
                repo_key = self._get_repo_key(repo_url)
                service_data["repositories"][repo_key] = {
                    "url": repo_url,
                    "analysis_type": "progressive_baml_failed",
                    "error": str(e),
                    "role": "UNKNOWN",
                    "tech_stack": {"primary_stack": "UNKNOWN", "confidence": "low", "reasoning": f"Progressive analysis failed: {e}"},
                    "communication_protocols": [],
                    "deployment_patterns": []
                }
                
                with open(service_file, 'w', encoding='utf-8') as f:
                    json.dump(service_data, f, indent=2, ensure_ascii=False)
                    
            except Exception as save_error:
                logger.error(f"🔍 DEBUG: Failed to save fallback data: {save_error}")
            
            return False
    
    def _get_readme_content(self, repo_path: Path) -> str:
        """Get README content for repository analysis."""
        for readme_name in ["README.md", "README.txt", "README.rst", "README"]:
            readme_path = repo_path / readme_name
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue
        return "No README found"
    
    def _collect_batch_content(self, repo_path: Path, batch) -> str:
        """Collect file content for a specific batch of files."""
        batch_content = []
        
        for file_metadata in batch.files:
            file_path = repo_path / file_metadata.path
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Truncate very large files to respect token limits
                    if len(content) > 5000:
                        content = content[:5000] + "\n... (truncated for analysis)"
                    
                    batch_content.append(f"=== {file_metadata.path} ===\n{content}\n")
                except Exception as e:
                    logger.debug(f"Could not read file {file_metadata.path}: {e}")
                    continue
        
        return "\n".join(batch_content)
    
    def _synthesize_progressive_analysis(self, file_plan, batch_results) -> Dict[str, Any]:
        """Synthesize final analysis from all batch results."""
        
        # Extract key insights from batch results
        tech_patterns = []
        api_patterns = []
        deployment_hints = []
        
        for batch_result in batch_results:
            analysis = batch_result["analysis"]
            category = batch_result["batch_category"]
            
            if "API" in category or "api" in analysis.lower():
                api_patterns.append(analysis)
            if "deploy" in analysis.lower() or "docker" in analysis.lower():
                deployment_hints.append(analysis)
            if "framework" in analysis.lower() or "language" in analysis.lower():
                tech_patterns.append(analysis)
        
        # Infer role from repository type and patterns
        role_mapping = {
            "PYTHON": "BACKEND_SERVICE",
            "NODEJS_JAVASCRIPT": "FRONTEND_APP", 
            "GO": "MICROSERVICE",
            "JAVA_MAVEN": "BACKEND_SERVICE"
        }
        
        inferred_role = role_mapping.get(str(file_plan.repository_type), "LIBRARY")
        
        # Build final analysis
        return {
            "role": inferred_role,
            "tech_stack": {
                "primary_stack": str(file_plan.repository_type),
                "secondary_stacks": [],
                "frameworks": [],
                "evidence_files": [],
                "confidence": "medium",
                "reasoning": f"Progressive analysis of {len(batch_results)} batches using {file_plan.analysis_strategy}"
            },
            "communication_protocols": self._extract_protocols_from_batches(batch_results),
            "deployment_patterns": deployment_hints,
            "confidence": "medium",
            "reasoning": f"Synthesized from progressive analysis of {len(batch_results)} file batches"
        }
    
    def _extract_protocols_from_batches(self, batch_results) -> List[Dict[str, Any]]:
        """Extract communication protocols from batch analysis results."""
        protocols = []
        
        for batch_result in batch_results:
            analysis = batch_result["analysis"].lower()
            
            if "http" in analysis or "rest" in analysis or "api" in analysis:
                protocols.append({
                    "protocol_type": "HTTP/HTTPS",
                    "endpoints": [],
                    "configuration_details": f"Detected in {batch_result['batch_category']} analysis",
                    "evidence_files": []
                })
            
            if "websocket" in analysis:
                protocols.append({
                    "protocol_type": "WebSocket", 
                    "endpoints": [],
                    "configuration_details": f"Detected in {batch_result['batch_category']} analysis",
                    "evidence_files": []
                })
            
            if "grpc" in analysis:
                protocols.append({
                    "protocol_type": "gRPC",
                    "endpoints": [],
                    "configuration_details": f"Detected in {batch_result['batch_category']} analysis", 
                    "evidence_files": []
                })
        
        # Remove duplicates
        unique_protocols = []
        seen_types = set()
        for protocol in protocols:
            if protocol["protocol_type"] not in seen_types:
                unique_protocols.append(protocol)
                seen_types.add(protocol["protocol_type"])
        
        return unique_protocols
    
    def _get_repo_key(self, repo_url: str) -> str:
        """
        Generate a consistent key for repository storage.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            str: Standardized repository key
        """
        # Clean and standardize the repo URL for use as a key
        return repo_url.rstrip('/').rstrip('.git')
    
    async def _detect_analysis_strategy(self, repo_url: str) -> str:
        """
        Detect repository complexity using BAML to choose appropriate analysis strategy.
        NO HARDCODED THRESHOLDS - Let BAML make intelligent decisions.
        
        Args:
            repo_url: Repository URL to analyze
            
        Returns:
            str: "standard" for regular analysis, "progressive" for large repos, "lightweight" for very large repos
        """
        try:
            logger.info(f"🔍 DEBUG: Using BAML to determine analysis strategy for {repo_url}")
            
            # Get repository path
            repo_path = self._get_repo_path(repo_url)
            if not repo_path or not repo_path.exists():
                logger.warning(f"🔍 DEBUG: Repository path not found, defaulting to standard analysis")
                return "standard"
            
            # Collect basic metrics (no hardcoded decisions)
            file_count = sum(1 for _ in repo_path.rglob("*") if _.is_file())
            repository_structure = self._collect_file_structure(repo_path)
            readme_content = self._get_readme_content(repo_path)
            
            # Get sample files for context (first 50 files for strategy assessment)
            sample_files = []
            for file_path in repo_path.rglob("*"):
                if file_path.is_file() and len(sample_files) < 50:
                    relative_path = file_path.relative_to(repo_path)
                    sample_files.append(str(relative_path))
            sample_files_str = "\n".join(sample_files)
            
            logger.info(f"🔍 DEBUG: Calling BAML DetermineRepositoryStrategy")
            logger.info(f"🔍 DEBUG: File count: {file_count}")
            logger.info(f"🔍 DEBUG: Repository structure length: {len(repository_structure)} chars")
            logger.info(f"🔍 DEBUG: Sample files: {len(sample_files)} files")
            
            # Let BAML decide the strategy (NO HARDCODED THRESHOLDS)
            strategy_analysis = await self.baml_client.DetermineRepositoryStrategy(
                file_count=file_count,
                repository_structure=repository_structure,
                readme_content=readme_content,
                sample_files=sample_files_str
            )
            
            logger.info(f"🔍 DEBUG: BAML strategy recommendation: {strategy_analysis.recommended_approach}")
            logger.info(f"🔍 DEBUG: Complexity level: {strategy_analysis.estimated_complexity_level}")
            logger.info(f"🔍 DEBUG: BAML reasoning: {strategy_analysis.reasoning}")
            logger.info(f"🔍 DEBUG: Max files recommended: {strategy_analysis.max_files_for_analysis}")
            
            return strategy_analysis.recommended_approach
                
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error in BAML strategy detection: {e}")
            logger.info(f"🔍 DEBUG: Defaulting to standard analysis due to error")
            return "standard"
    
    def _get_repo_path(self, repo_url: str) -> Optional[Path]:
        """Get local path for repository."""
        try:
            # Extract repo identifier from URL (consistent with data_pipeline logic)
            # e.g., "https://github.com/owner/repo.git" -> "owner_repo"
            if any(domain in repo_url for domain in ["github.com", "gitlab.com", "bitbucket.org"]):
                parts = repo_url.rstrip('/').split('/')
                if len(parts) >= 5:
                    owner, repo = parts[-2], parts[-1]
                    # Remove .git suffix if present (consistent with data_pipeline)
                    repo = repo.replace(".git", "")
                    repo_identifier = f"{owner}_{repo}"
                    return self.repos_dir / repo_identifier
            
            return None
        except Exception as e:
            logger.error(f"Failed to determine repo path for {repo_url}: {e}")
            return None
    
    def _collect_file_structure(self, repo_path: Path) -> str:
        """Collect complete repository file structure for BAML analysis."""
        file_list = []
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(repo_path)
                file_list.append(str(relative_path))
        
        # Let BAML decide what's important - just provide the structure
        repo_name = repo_path.name
        structure = f"{repo_name}/\n"
        for file_path in sorted(file_list[:200]):  # Reasonable limit for analysis
            structure += f"  {file_path}\n"
        return structure
    
    def _collect_repository_content(self, repo_path: Path) -> str:
        """Collect all repository content and let BAML intelligently analyze it."""
        all_files_content = []
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                try:
                    relative_path = file_path.relative_to(repo_path)
                    # Let BAML decide what's readable - just try to read everything
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Limit content per file for analysis
                    if len(content) > 2000:
                        content = content[:2000] + "\n... (truncated)"
                    all_files_content.append(f"=== {relative_path} ===\n{content}\n")
                except Exception:
                    # Skip files that can't be read - let BAML handle the rest
                    continue
                
                # Reasonable limit for BAML analysis
                if len(all_files_content) >= 20:
                    break
        
        return "\n".join(all_files_content) if all_files_content else "No readable files found"
    
    # All classification and formatting is now handled by BAML
    def _collect_code_samples(self, repo_path: Path) -> str:
        """Deprecated - use _collect_repository_content instead."""
        return "Use _collect_repository_content for intelligent analysis"
    
    def _collect_config_files(self, repo_path: Path) -> str:
        """Deprecated - use _collect_repository_content instead."""
        return "Use _collect_repository_content for intelligent analysis"
    
    def _collect_package_manifests(self, repo_path: Path) -> str:
        """Deprecated - use _collect_repository_content instead."""
        return "Use _collect_repository_content for intelligent analysis"
    
 