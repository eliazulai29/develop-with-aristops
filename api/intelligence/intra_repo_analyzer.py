"""
Repository Intelligence Enrichment using AdalFlow + BAML.

This module implements the IntraRepoAnalyzer that orchestrates BAML-powered 
analysis to find deep relationships within a repository after FAISS indexing.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import adalflow as adal
from adalflow.core.types import Document

try:
    from api.baml_client.async_client import b
    from api.baml_client.types import (
    CodeAnalysis, CodeComponent, Dependency, ArchitecturalInsight
)
except ImportError as e:
    # Handle missing BAML gracefully
    raise ImportError(f"BAML client not available: {e}")

try:
    from .progress_manager import ProgressManager
except ImportError:
    from api.intelligence.progress_manager import ProgressManager

logger = logging.getLogger(__name__)

@dataclass
class EnrichmentResult:
    """Result of repository enrichment analysis."""
    enriched_documents: List[Document]
    analysis_summary: str
    component_count: int
    dependency_count: int

class IntraRepoAnalyzer(adal.Component):
    """
    AdalFlow Component for repository intelligence enrichment.
    
    This analyzer takes control after FAISS indexing completes, uses BAML 
    to analyze repository structure and relationships, then generates 
    enriched documents that are added back to the FAISS store.
    
    Follows the same Component pattern as the RAG class.
    """
    
    def __init__(self, progress_manager: ProgressManager):
        """
        Initialize the IntraRepo analyzer.
        
        Args:
            progress_manager: Progress manager for WebSocket status updates
        """
        super().__init__()
        self.progress_manager = progress_manager
        self.baml_client = b  # Use existing BAML client
        
        # Component state
        self.repo_path: Optional[str] = None
        self.repo_url: Optional[str] = None
        
    async def analyze_and_enrich(
        self, 
        repo_path: str, 
        repo_url: str,
        existing_documents: List[Document],
        embedder=None
    ) -> EnrichmentResult:
        """
        Main orchestration method for repository enrichment.
        
        Args:
            repo_path: Local path to the cloned repository
            repo_url: Original repository URL
            existing_documents: Documents already in FAISS
            embedder: Embedder to generate embeddings for enriched documents
            
        Returns:
            EnrichmentResult with enriched documents and metadata
        """
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.embedder = embedder
        
        try:
            # Phase 1: Start enrichment
            await self.progress_manager.start_phase("Deep code enrichment")
            
            # Phase 2: Repository analysis via BAML
            await self.progress_manager.update_status("🧠 Analyzing repository structure...")
            code_samples = await self._extract_code_samples(repo_path, existing_documents)
            
            # Phase 3: Intelligent analysis using BAML
            await self.progress_manager.update_status("🔍 Discovering code relationships...")
            analysis_results = await self._analyze_with_baml(code_samples)
            
            # Phase 4: Generate enriched documents
            await self.progress_manager.update_status("📝 Generating architectural insights...")
            enriched_docs = await self._generate_enrichment_documents(analysis_results)
            
            # Phase 5: Complete
            await self.progress_manager.complete_phase("Repository enrichment")
            
            return EnrichmentResult(
                enriched_documents=enriched_docs,
                analysis_summary=analysis_results.overallSummary or "Repository analysis complete",
                component_count=len(analysis_results.components or []),
                dependency_count=len(analysis_results.dependencies or [])
            )
            
        except Exception as e:
            logger.error(f"Repository enrichment failed: {e}")
            await self.progress_manager.update_status(f"❌ Enrichment failed: {str(e)}")
            raise
    
    async def _extract_code_samples(
        self, 
        repo_path: str, 
        existing_documents: List[Document]
    ) -> List[str]:
        """
        Extract representative code samples from repository.
        
        Args:
            repo_path: Path to repository
            existing_documents: Already processed documents
            
        Returns:
            List of code samples for analysis
        """
        code_samples = []
        
        # Extract content from existing documents (limit for BAML analysis)
        for i, doc in enumerate(existing_documents[:20]):  # Analyze top 20 documents
            if hasattr(doc, 'text') and doc.text:
                code_samples.append(doc.text[:2000])  # Limit text size
                
                if i % 5 == 0:  # Progress every 5 documents
                    await self.progress_manager.enrichment_progress(
                        current=i + 1, 
                        total=min(20, len(existing_documents)), 
                        item_name="code files"
                    )
        
        logger.info(f"Extracted {len(code_samples)} code samples for analysis")
        return code_samples
    
    async def _analyze_with_baml(self, code_samples: List[str]) -> CodeAnalysis:
        """
        Perform intelligent analysis using BAML.
        
        Args:
            code_samples: Code samples to analyze
            
        Returns:
            CodeAnalysis object with structured insights
        """
        # Combine code samples for comprehensive analysis
        combined_code = "\n\n--- FILE SEPARATOR ---\n\n".join(code_samples)
        
        try:
            # Use existing BAML AnalyzeCode function
            analysis = await self.baml_client.AnalyzeCode(combined_code)
            
            logger.info(f"BAML analysis complete: {len(analysis.components or [])} components, "
                       f"{len(analysis.dependencies or [])} dependencies")
            
            return analysis
            
        except Exception as e:
            logger.error(f"BAML analysis failed: {e}")
            # Return minimal analysis on failure
            return CodeAnalysis(
                components=[],
                dependencies=[],
                overallSummary=f"Analysis partially failed: {str(e)}"
            )
    
    async def _generate_enrichment_documents(self, analysis: CodeAnalysis) -> List[Document]:
        """
        Convert BAML analysis into searchable FAISS documents with embeddings.
        
        Args:
            analysis: BAML CodeAnalysis results
            
        Returns:
            List of enriched Document objects with embeddings
        """
        enriched_docs = []
        
        # Helper function to generate embeddings for a document
        async def add_embedding(doc: Document) -> Document:
            if self.embedder and hasattr(self.embedder, '__call__'):
                try:
                    # Generate embedding for the document text
                    result = await self.embedder.acall(doc.text) if hasattr(self.embedder, 'acall') else self.embedder(doc.text)
                    
                    # Extract actual embedding from EmbedderOutput
                    if hasattr(result, 'data') and result.data and len(result.data) > 0:
                        embedding = result.data[0].embedding
                        doc.vector = embedding
                        logger.debug(f"Generated embedding for document: {doc.meta_data.get('type', 'unknown')} (size: {len(embedding)})")
                    else:
                        logger.warning(f"No embedding data received for document: {doc.meta_data.get('type', 'unknown')}")
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for document: {e}")
            return doc
        
        # Generate component relationship documents
        if analysis.components:
            for component in analysis.components:
                doc_text = self._format_component_document(component)
                doc = Document(
                    text=doc_text,
                    meta_data={
                        "type": "component_analysis",
                        "component_name": component.name,
                        "component_type": component.type.value if component.type else "unknown",
                        "source": "baml_enrichment",
                        "repo_url": self.repo_url
                    }
                )
                doc = await add_embedding(doc)
                enriched_docs.append(doc)
        
        # Generate dependency relationship documents  
        if analysis.dependencies:
            for dependency in analysis.dependencies:
                doc_text = self._format_dependency_document(dependency)
                doc = Document(
                    text=doc_text,
                    meta_data={
                        "type": "dependency_analysis", 
                        "source_component": dependency.sourceComponent,
                        "target_component": dependency.targetComponent,
                        "dependency_type": dependency.type,
                        "source": "baml_enrichment",
                        "repo_url": self.repo_url
                    }
                )
                doc = await add_embedding(doc)
                enriched_docs.append(doc)
        
        # Generate architectural insights document
        if analysis.architecture:
            arch_doc = Document(
                text=self._format_architectural_document(analysis.architecture),
                meta_data={
                    "type": "architectural_analysis",
                    "pattern": analysis.architecture.pattern.value if analysis.architecture.pattern else "unknown",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            arch_doc = await add_embedding(arch_doc)
            enriched_docs.append(arch_doc)
        
        # Analytical documents removed - now handled by chat-time AdalFlow analysis
        # This includes: security, performance, testing, and operational analysis
        
        # Generate HOW/WHERE/WHY insights document
        if analysis.keyInsights or analysis.howToQuestions or analysis.whereToLook or analysis.whyDecisions:
            insights_doc = Document(
                text=self._format_insights_document(analysis),
                meta_data={
                    "type": "insights_summary",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            insights_doc = await add_embedding(insights_doc)
            enriched_docs.append(insights_doc)
        
        # Generate overall architecture summary
        if analysis.overallSummary:
            summary_doc = Document(
                text=f"# Repository Architecture Summary\n\n{analysis.overallSummary}\n\n"
                     f"This repository contains {len(analysis.components or [])} components "
                     f"with {len(analysis.dependencies or [])} identified relationships.\n\n"
                     f"**Key Features:**\n"
                     f"- Components: {len(analysis.components or [])}\n"
                     f"- Dependencies: {len(analysis.dependencies or [])}\n"
                     f"- Architecture Pattern: {analysis.architecture.pattern.value if analysis.architecture and analysis.architecture.pattern else 'Unknown'}\n"
                                 f"- Navigation Guidance: {'✅ Complete' if analysis.navigationTips else '❌ Not analyzed'}\n"
            f"- Entry Points: {'✅ Complete' if analysis.entryPoints else '❌ Not analyzed'}\n"
            f"- Core Components: {'✅ Complete' if analysis.coreComponents else '❌ Not analyzed'}",
                meta_data={
                    "type": "architecture_summary",
                    "source": "baml_enrichment", 
                    "repo_url": self.repo_url,
                    "component_count": len(analysis.components or []),
                    "dependency_count": len(analysis.dependencies or [])
                }
            )
            summary_doc = await add_embedding(summary_doc)
            enriched_docs.append(summary_doc)
        
        logger.info(f"Generated {len(enriched_docs)} enrichment documents")
        return enriched_docs
    
    def _format_component_document(self, component: CodeComponent) -> str:
        """Format a component into a searchable document."""
        doc_text = f"# Component: {component.name}\n\n"
        doc_text += f"**Type**: {component.type.value if component.type else 'Unknown'}\n"
        doc_text += f"**File**: {component.sourceFile}\n"
        doc_text += f"**Complexity**: {component.complexity}\n"
        doc_text += f"**Purpose**: {getattr(component, 'purpose', 'Not specified')}\n"
        doc_text += f"**Testability**: {getattr(component, 'testability', 'Unknown')}\n"
        doc_text += f"**Reusability**: {getattr(component, 'reusability', 'Unknown')}\n\n"
        
        doc_text += f"**Description**: {component.description}\n\n"
        
        if component.dependencies:
            doc_text += f"**Dependencies**: {', '.join(component.dependencies)}\n\n"
        
        # Add public interface
        public_interface = getattr(component, 'publicInterface', [])
        if public_interface:
            doc_text += f"**Public Interface**: {', '.join(public_interface)}\n\n"
        
        # Add quality issues
        # Quality issues removed - now handled by chat-time analysis
        
        # Add refactoring opportunities
        refactoring_ops = getattr(component, 'refactoringOpportunities', [])
        if refactoring_ops:
            doc_text += f"**Refactoring Opportunities**:\n"
            for op in refactoring_ops:
                doc_text += f"- {op}\n"
            doc_text += "\n"
        
        if component.snippet:
            doc_text += f"**Code Sample**:\n```\n{component.snippet}\n```\n\n"
        
        doc_text += f"This component is part of the repository architecture and has "
        doc_text += f"{len(component.dependencies)} identified dependencies."
        
        return doc_text
    
    def _format_dependency_document(self, dependency: Dependency) -> str:
        """Format a dependency relationship into a searchable document."""
        doc_text = f"# Dependency: {dependency.sourceComponent} → {dependency.targetComponent}\n\n"
        doc_text += f"**Relationship Type**: {dependency.type}\n"
        doc_text += f"**Strength**: {getattr(dependency, 'strength', 'Unknown')}\n"
        doc_text += f"**Direction**: {getattr(dependency, 'direction', 'Unknown')}\n"
        doc_text += f"**Description**: {dependency.description}\n\n"
        doc_text += f"The component '{dependency.sourceComponent}' {dependency.type} "
        doc_text += f"'{dependency.targetComponent}'. {dependency.description}"
        
        return doc_text
    
    def _format_architectural_document(self, architecture: ArchitecturalInsight) -> str:
        """Format architectural insights into a searchable document."""
        doc_text = f"# Architectural Pattern Analysis\n\n"
        doc_text += f"**Pattern**: {architecture.pattern.value}\n"
        doc_text += f"**Confidence**: {architecture.confidence}\n"
        doc_text += f"**Adherence**: {architecture.adherence}\n\n"
        doc_text += f"**Description**: {architecture.description}\n\n"
        
        if architecture.improvements:
            doc_text += f"**Improvement Suggestions**:\n"
            for improvement in architecture.improvements:
                doc_text += f"- {improvement}\n"
            doc_text += "\n"
        
        doc_text += f"This codebase follows the {architecture.pattern.value} architectural pattern "
        doc_text += f"with {architecture.adherence} adherence to the pattern principles."
        
        return doc_text
    
    # Removed analytical formatting methods - now handled by chat-time AdalFlow analysis:
    # - _format_security_document (security analysis)
    # - _format_performance_document (performance analysis)  
    # - _format_testing_document (testing analysis)
    # - _format_operational_document (operational analysis)
    
    def _format_insights_document(self, analysis: CodeAnalysis) -> str:
        """Format structural insights into a searchable document."""
        doc_text = f"# Repository Navigation & Structural Insights\n\n"
        
        if analysis.keyInsights:
            doc_text += f"**🔑 Key Structural Insights**:\n"
            for insight in analysis.keyInsights:
                doc_text += f"- {insight}\n"
            doc_text += "\n"
        
        if analysis.entryPoints:
            doc_text += f"**🚪 Entry Points**:\n"
            for entry_point in analysis.entryPoints:
                doc_text += f"- {entry_point}\n"
            doc_text += "\n"
        
        if analysis.coreComponents:
            doc_text += f"**⚙️ Core Components**:\n"
            for component in analysis.coreComponents:
                doc_text += f"- {component}\n"
            doc_text += "\n"
        
        if analysis.howToQuestions:
            doc_text += f"**❓ HOW Questions This Analysis Can Answer**:\n"
            for question in analysis.howToQuestions:
                doc_text += f"- {question}\n"
            doc_text += "\n"
        
        if analysis.whereToLook:
            doc_text += f"**📍 WHERE To Look For Functionality**:\n"
            for location in analysis.whereToLook:
                doc_text += f"- {location}\n"
            doc_text += "\n"
        
        if analysis.whyDecisions:
            doc_text += f"**🤔 WHY Architectural Decisions Were Made**:\n"
            for decision in analysis.whyDecisions:
                doc_text += f"- {decision}\n"
            doc_text += "\n"
        
        if analysis.navigationTips:
            doc_text += f"**🧭 Navigation Tips**:\n"
            for tip in analysis.navigationTips:
                doc_text += f"- {tip}\n"
            doc_text += "\n"
        
        doc_text += "This document provides structural insights to help developers understand "
        doc_text += "the codebase architecture, navigate components, and find functionality. "
        doc_text += "For quality, performance, security, and testing analysis, ask specific questions in chat."
        
        return doc_text 