"""
Repository State Manager - Production Ready State Tracking

Provides clean separation between:
1. Repository assignment to services
2. Enrichment completion 
3. Chat readiness validation

Author: AI Assistant
"""

import os
import json
import logging
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class RepositoryState(Enum):
    """Repository processing states"""
    NEEDS_ASSIGNMENT = "needs_assignment"
    NEEDS_ENRICHMENT = "needs_enrichment"  
    READY_FOR_CHAT = "ready_for_chat"
    CORRUPTED = "corrupted"

class RepositoryStateManager:
    """
    Production-ready repository state tracking
    
    Implements two-phase detection:
    Phase 1: Service Assignment State
    Phase 2: Enrichment Completion State
    """
    
    def __init__(self, service_manager, config):
        self.service_manager = service_manager
        self.config = config
        self.services_dir = Path(config.get('services_directory', '~/.adalflow/services')).expanduser()
        self.databases_dir = Path(config.get('databases_directory', '~/.adalflow/databases')).expanduser()
        
    def get_repository_state(self, repo_url: str, service_name: str) -> RepositoryState:
        """
        Determine the current state of a repository
        
        Args:
            repo_url: Repository URL
            service_name: Target service name
            
        Returns:
            RepositoryState: Current processing state
        """
        try:
            logger.info(f"🔍 STATE CHECK: Checking state for {repo_url} in service '{service_name}'")
            
            # Phase 1: Check service assignment
            assignment_state = self._check_service_assignment(repo_url, service_name)
            if assignment_state != RepositoryState.READY_FOR_CHAT:
                logger.info(f"📋 STATE: Service assignment incomplete - {assignment_state.value}")
                return assignment_state
                
            # Phase 2: Check enrichment completion
            enrichment_state = self._check_enrichment_completion(repo_url, service_name)
            if enrichment_state != RepositoryState.READY_FOR_CHAT:
                logger.info(f"🔧 STATE: Enrichment incomplete - {enrichment_state.value}")
                return enrichment_state
                
            # Phase 3: Validate data integrity
            integrity_state = self._validate_data_integrity(repo_url)
            logger.info(f"✅ STATE: Final state - {integrity_state.value}")
            return integrity_state
            
        except Exception as e:
            logger.error(f"❌ STATE ERROR: Failed to determine state for {repo_url}: {e}")
            return RepositoryState.CORRUPTED
    
    def _check_service_assignment(self, repo_url: str, service_name: str) -> RepositoryState:
        """Phase 1: Check if repository is properly assigned to service"""
        try:
            # Find service file
            service_file = self._find_service_file(service_name)
            if not service_file:
                logger.debug(f"📋 Service file not found for '{service_name}'")
                return RepositoryState.NEEDS_ASSIGNMENT
                
            # Load service data
            with open(service_file, 'r') as f:
                service_data = json.load(f)
                
            # Check repository assignment
            repositories = service_data.get('repositories', {})
            if repo_url not in repositories:
                logger.debug(f"📋 Repository {repo_url} not assigned to service")
                return RepositoryState.NEEDS_ASSIGNMENT
                
            logger.debug(f"✅ Repository properly assigned to service '{service_name}'")
            return RepositoryState.READY_FOR_CHAT
            
        except Exception as e:
            logger.error(f"❌ Service assignment check failed: {e}")
            return RepositoryState.CORRUPTED
    
    def _check_enrichment_completion(self, repo_url: str, service_name: str) -> RepositoryState:
        """Phase 2: Check if enrichment is complete"""
        try:
            service_file = self._find_service_file(service_name)
            if not service_file:
                return RepositoryState.NEEDS_ASSIGNMENT
                
            with open(service_file, 'r') as f:
                service_data = json.load(f)
                
            repositories = service_data.get('repositories', {})
            repo_entry = repositories.get(repo_url, {})
            
            # Check enrichment flag
            is_enriched = repo_entry.get('enriched', False)
            if not is_enriched:
                logger.debug(f"🔧 Repository enrichment not completed")
                return RepositoryState.NEEDS_ENRICHMENT
                
            # Validate enrichment timestamp
            enrichment_timestamp = repo_entry.get('analysis_timestamp')
            if not enrichment_timestamp:
                logger.debug(f"🔧 No enrichment timestamp found")
                return RepositoryState.NEEDS_ENRICHMENT
                
            logger.debug(f"✅ Repository enrichment completed at {enrichment_timestamp}")
            return RepositoryState.READY_FOR_CHAT
            
        except Exception as e:
            logger.error(f"❌ Enrichment completion check failed: {e}")
            return RepositoryState.CORRUPTED
    
    def _validate_data_integrity(self, repo_url: str) -> RepositoryState:
        """Phase 3: Validate FAISS data integrity"""
        try:
            faiss_path = self._get_faiss_path(repo_url)
            
            # Check file existence
            if not os.path.exists(faiss_path):
                logger.debug(f"🗄️ FAISS file not found: {faiss_path}")
                return RepositoryState.NEEDS_ENRICHMENT
                
            # Check minimum file size (corrupted files are often 0 bytes)
            file_size = os.path.getsize(faiss_path)
            if file_size < 1024:  # Minimum 1KB
                logger.debug(f"🗄️ FAISS file too small ({file_size} bytes), likely corrupted")
                return RepositoryState.CORRUPTED
                
            logger.debug(f"✅ FAISS data integrity validated ({file_size} bytes)")
            return RepositoryState.READY_FOR_CHAT
            
        except Exception as e:
            logger.error(f"❌ Data integrity validation failed: {e}")
            return RepositoryState.CORRUPTED
    
    def _find_service_file(self, service_name: str) -> Optional[Path]:
        """Find service file by name"""
        try:
            if not self.services_dir.exists():
                return None
                
            # Look for service files matching the name
            for service_file in self.services_dir.glob(f"{service_name}-*.json"):
                return service_file
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding service file: {e}")
            return None
    
    def _get_faiss_path(self, repo_url: str) -> Path:
        """Get expected FAISS file path for repository"""
        # Convert URL to filename format
        repo_name = repo_url.replace('https://github.com/', '').replace('.git', '').replace('/', '_')
        return self.databases_dir / f"{repo_name}.pkl"
    
    def mark_enrichment_complete(self, repo_url: str, service_name: str) -> bool:
        """Mark repository enrichment as complete"""
        try:
            service_file = self._find_service_file(service_name)
            if not service_file:
                logger.error(f"❌ Cannot mark enrichment complete: Service file not found for '{service_name}'")
                return False
                
            with open(service_file, 'r') as f:
                service_data = json.load(f)
                
            # Update repository entry
            repositories = service_data.get('repositories', {})
            if repo_url in repositories:
                repositories[repo_url]['enriched'] = True
                repositories[repo_url]['enrichment_completed_at'] = self._get_current_timestamp()
                
                # Save updated service data
                with open(service_file, 'w') as f:
                    json.dump(service_data, f, indent=2)
                    
                logger.info(f"✅ Marked enrichment complete for {repo_url}")
                return True
            else:
                logger.error(f"❌ Repository {repo_url} not found in service")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to mark enrichment complete: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def should_skip_enrichment_for_chat(self, repo_url: str, service_name: str) -> bool:
        """
        Determine if enrichment should be skipped for chat requests
        
        Returns True only if repository is fully ready for chat
        """
        state = self.get_repository_state(repo_url, service_name)
        result = state == RepositoryState.READY_FOR_CHAT
        
        logger.info(f"🤖 CHAT DECISION: Skip enrichment for {repo_url}? {result} (state: {state.value})")
        return result
    
    def should_run_full_enrichment_for_new_repo(self, repo_url: str, service_name: str) -> bool:
        """
        Determine if full enrichment should run for new repository loading
        
        Returns True if repository needs any processing
        """
        state = self.get_repository_state(repo_url, service_name)
        result = state in [RepositoryState.NEEDS_ASSIGNMENT, RepositoryState.NEEDS_ENRICHMENT, RepositoryState.CORRUPTED]
        
        logger.info(f"🆕 NEW REPO DECISION: Run enrichment for {repo_url}? {result} (state: {state.value})")
        return result 