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
        CodeAnalysis, CodeComponent, Dependency, ArchitecturalInsight, 
        SecurityAnalysis, PerformanceInsight, TestingInsight, OperationalInsight
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
        
        # Generate security analysis document
        if analysis.security:
            security_doc = Document(
                text=self._format_security_document(analysis.security),
                meta_data={
                    "type": "security_analysis",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            security_doc = await add_embedding(security_doc)
            enriched_docs.append(security_doc)
        
        # Generate performance insights document
        if analysis.performance:
            perf_doc = Document(
                text=self._format_performance_document(analysis.performance),
                meta_data={
                    "type": "performance_analysis",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            perf_doc = await add_embedding(perf_doc)
            enriched_docs.append(perf_doc)
        
        # Generate testing insights document
        if analysis.testing:
            testing_doc = Document(
                text=self._format_testing_document(analysis.testing),
                meta_data={
                    "type": "testing_analysis",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            testing_doc = await add_embedding(testing_doc)
            enriched_docs.append(testing_doc)
        
        # Generate operational insights document
        if analysis.operations:
            ops_doc = Document(
                text=self._format_operational_document(analysis.operations),
                meta_data={
                    "type": "operational_analysis",
                    "source": "baml_enrichment",
                    "repo_url": self.repo_url
                }
            )
            ops_doc = await add_embedding(ops_doc)
            enriched_docs.append(ops_doc)
        
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
                     f"- Security Analysis: {'✅ Complete' if analysis.security else '❌ Not analyzed'}\n"
                     f"- Performance Analysis: {'✅ Complete' if analysis.performance else '❌ Not analyzed'}\n"
                     f"- Testing Analysis: {'✅ Complete' if analysis.testing else '❌ Not analyzed'}",
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
        quality_issues = getattr(component, 'qualityIssues', [])
        if quality_issues:
            doc_text += f"**Quality Issues**: {', '.join([issue.value for issue in quality_issues])}\n\n"
        
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
    
    def _format_security_document(self, security: SecurityAnalysis) -> str:
        """Format security analysis into a searchable document."""
        doc_text = f"# Security Analysis\n\n"
        
        if security.vulnerabilities:
            doc_text += f"**Potential Vulnerabilities**:\n"
            for vuln in security.vulnerabilities:
                doc_text += f"- {vuln}\n"
            doc_text += "\n"
        
        if security.securityPatterns:
            doc_text += f"**Security Patterns Identified**:\n"
            for pattern in security.securityPatterns:
                doc_text += f"- {pattern}\n"
            doc_text += "\n"
        
        if security.recommendations:
            doc_text += f"**Security Recommendations**:\n"
            for rec in security.recommendations:
                doc_text += f"- {rec}\n"
            doc_text += "\n"
        
        if security.dataFlowRisks:
            doc_text += f"**Data Flow Security Risks**:\n"
            for risk in security.dataFlowRisks:
                doc_text += f"- {risk}\n"
            doc_text += "\n"
        
        doc_text += "This analysis identifies potential security concerns and provides "
        doc_text += "recommendations for improving the security posture of the codebase."
        
        return doc_text
    
    def _format_performance_document(self, performance: PerformanceInsight) -> str:
        """Format performance insights into a searchable document."""
        doc_text = f"# Performance Analysis\n\n"
        
        if performance.bottlenecks:
            doc_text += f"**Performance Bottlenecks**:\n"
            for bottleneck in performance.bottlenecks:
                doc_text += f"- {bottleneck}\n"
            doc_text += "\n"
        
        if performance.optimizationOpportunities:
            doc_text += f"**Optimization Opportunities**:\n"
            for opp in performance.optimizationOpportunities:
                doc_text += f"- {opp}\n"
            doc_text += "\n"
        
        if performance.scalabilityConcerns:
            doc_text += f"**Scalability Concerns**:\n"
            for concern in performance.scalabilityConcerns:
                doc_text += f"- {concern}\n"
            doc_text += "\n"
        
        doc_text += f"**Resource Usage**: {performance.resourceUsage}\n\n"
        doc_text += "This analysis identifies performance bottlenecks and provides "
        doc_text += "suggestions for optimization and improved scalability."
        
        return doc_text
    
    def _format_testing_document(self, testing: TestingInsight) -> str:
        """Format testing insights into a searchable document."""
        doc_text = f"# Testing Analysis\n\n"
        doc_text += f"**Test Coverage**: {testing.testCoverage}\n\n"
        
        if testing.testableComponents:
            doc_text += f"**Well-Testable Components**:\n"
            for comp in testing.testableComponents:
                doc_text += f"- {comp}\n"
            doc_text += "\n"
        
        if testing.hardToTestComponents:
            doc_text += f"**Hard-to-Test Components**:\n"
            for comp in testing.hardToTestComponents:
                doc_text += f"- {comp}\n"
            doc_text += "\n"
        
        if testing.testingRecommendations:
            doc_text += f"**Testing Recommendations**:\n"
            for rec in testing.testingRecommendations:
                doc_text += f"- {rec}\n"
            doc_text += "\n"
        
        if testing.missingTestTypes:
            doc_text += f"**Missing Test Types**:\n"
            for test_type in testing.missingTestTypes:
                doc_text += f"- {test_type}\n"
            doc_text += "\n"
        
        doc_text += "This analysis evaluates the testability of the codebase and provides "
        doc_text += "recommendations for improving test coverage and quality."
        
        return doc_text
    
    def _format_operational_document(self, operations: OperationalInsight) -> str:
        """Format operational insights into a searchable document."""
        doc_text = f"# Operational Analysis\n\n"
        doc_text += f"**Maintenance Complexity**: {operations.maintenanceComplexity}\n\n"
        
        if operations.configurationFiles:
            doc_text += f"**Configuration Files**:\n"
            for config in operations.configurationFiles:
                doc_text += f"- {config}\n"
            doc_text += "\n"
        
        if operations.environmentDependencies:
            doc_text += f"**Environment Dependencies**:\n"
            for dep in operations.environmentDependencies:
                doc_text += f"- {dep}\n"
            doc_text += "\n"
        
        if operations.deploymentConsiderations:
            doc_text += f"**Deployment Considerations**:\n"
            for consideration in operations.deploymentConsiderations:
                doc_text += f"- {consideration}\n"
            doc_text += "\n"
        
        if operations.monitoringOpportunities:
            doc_text += f"**Monitoring Opportunities**:\n"
            for opp in operations.monitoringOpportunities:
                doc_text += f"- {opp}\n"
            doc_text += "\n"
        
        doc_text += "This analysis provides insights into operational aspects including "
        doc_text += "deployment, configuration, and maintenance considerations."
        
        return doc_text
    
    def _format_insights_document(self, analysis: CodeAnalysis) -> str:
        """Format HOW/WHERE/WHY insights into a searchable document."""
        doc_text = f"# Repository Insights for Developers\n\n"
        
        if analysis.keyInsights:
            doc_text += f"**🔑 Key Insights**:\n"
            for insight in analysis.keyInsights:
                doc_text += f"- {insight}\n"
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
        
        if analysis.debuggingTips:
            doc_text += f"**🐛 Debugging Tips**:\n"
            for tip in analysis.debuggingTips:
                doc_text += f"- {tip}\n"
            doc_text += "\n"
        
        if analysis.refactoringPriorities:
            doc_text += f"**🔧 Refactoring Priorities**:\n"
            for priority in analysis.refactoringPriorities:
                doc_text += f"- {priority}\n"
            doc_text += "\n"
        
        doc_text += "This document provides curated insights to help developers understand "
        doc_text += "how the codebase works, where to find specific functionality, and why "
        doc_text += "certain architectural decisions were made."
        
        return doc_text 