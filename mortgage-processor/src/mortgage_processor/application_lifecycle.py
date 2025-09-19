"""
Unified Application Lifecycle Management
Handles application creation and linking across chat conversations and document uploads
"""

import uuid
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging
from enum import Enum

from .neo4j_mortgage import MortgageGraphManager

logger = logging.getLogger(__name__)

class ApplicationPhase(Enum):
    """Application lifecycle phases"""
    DISCOVERY = "discovery"              # Just browsing, asking questions
    INITIATED = "initiated"              # Serious intent detected, ID created
    DOCUMENT_COLLECTION = "document_collection"  # Collecting documents
    IN_PROGRESS = "in_progress"          # Actively filling application
    READY_FOR_REVIEW = "ready_for_review"  # All info collected, ready to review
    SUBMITTED = "submitted"              # Formally submitted for processing
    PROCESSING = "processing"            # Under review by underwriters
    DECISION_MADE = "decision_made"      # Approved/denied/conditional

class ApplicationIntent(Enum):
    """Intent detection levels"""
    CASUAL_INQUIRY = "casual_inquiry"    # Just asking questions
    SERIOUS_INTEREST = "serious_interest"  # Wants rates, pre-qual
    READY_TO_APPLY = "ready_to_apply"    # Wants to start application
    DOCUMENT_UPLOAD = "document_upload"  # Uploading documents
    FINAL_SUBMISSION = "final_submission"  # Ready to submit

class UnifiedApplicationManager:
    """Manages application lifecycle across all touchpoints"""
    
    def __init__(self):
        self.neo4j_manager = MortgageGraphManager()
    
    def detect_application_intent(self, 
                                conversation_context: Optional[Dict] = None,
                                document_content: Optional[str] = None,
                                user_message: Optional[str] = None) -> ApplicationIntent:
        """
        Detect user intent level to determine when to create application ID
        
        Args:
            conversation_context: Chat conversation state
            document_content: Uploaded document content  
            user_message: Latest user message
            
        Returns:
            Detected intent level
        """
        
        # Document upload always indicates serious intent
        if document_content:
            return ApplicationIntent.DOCUMENT_UPLOAD
        
        if user_message:
            message_lower = user_message.lower()
            
            # Strong intent indicators
            if any(phrase in message_lower for phrase in [
                "i want to apply", "start application", "apply for mortgage",
                "submit application", "need a loan", "ready to apply"
            ]):
                return ApplicationIntent.READY_TO_APPLY
            
            # Serious interest indicators  
            if any(phrase in message_lower for phrase in [
                "pre-qualification", "pre-approve", "what rate", "how much can i borrow",
                "get approved", "loan estimate", "what documents", "income verification"
            ]):
                return ApplicationIntent.SERIOUS_INTEREST
            
            # Casual inquiry (default)
            return ApplicationIntent.CASUAL_INQUIRY
        
        # Check conversation context for progressive signals
        if conversation_context:
            # Has provided personal information
            if any(conversation_context.get(field) for field in [
                "full_name", "annual_income", "purchase_price", "down_payment"
            ]):
                return ApplicationIntent.SERIOUS_INTEREST
            
            # Has completed significant portion
            completion = conversation_context.get("completion_percentage", 0)
            if completion > 30:
                return ApplicationIntent.READY_TO_APPLY
        
        return ApplicationIntent.CASUAL_INQUIRY
    
    def find_or_create_application(self,
                                 person_name: Optional[str] = None,
                                 conversation_context: Optional[Dict] = None,
                                 document_entities: Optional[Dict] = None,
                                 intent: Optional[ApplicationIntent] = None) -> Tuple[str, str, ApplicationPhase]:
        """
        Unified application detection/creation across all touchpoints
        
        Args:
            person_name: Detected person name from documents or chat
            conversation_context: Chat conversation state
            document_entities: Knowledge graph entities from documents
            intent: Detected intent level
            
        Returns:
            Tuple of (application_id, detection_status, current_phase)
        """
        
        # Determine person identity from multiple sources
        detected_person = self._resolve_person_identity(
            person_name, conversation_context, document_entities
        )
        
        if not detected_person:
            # No person identity - only create application for serious intent
            if intent in [ApplicationIntent.DOCUMENT_UPLOAD, ApplicationIntent.READY_TO_APPLY]:
                return self._create_application(
                    person_name=None,
                    phase=ApplicationPhase.INITIATED,
                    source="unknown_person"
                )
            else:
                # Too early to create application
                return None, "no_application_needed", ApplicationPhase.DISCOVERY
        
        # Search for existing applications
        existing_app = self._find_existing_application(detected_person)
        
        if existing_app:
            app_id, current_phase = existing_app
            logger.info(f"Found existing application {app_id} for {detected_person}")
            return app_id, "found_existing", current_phase
        
        # Determine if we should create new application
        should_create = self._should_create_application(intent, conversation_context)
        
        if should_create:
            # Determine starting phase based on context
            if intent == ApplicationIntent.DOCUMENT_UPLOAD:
                phase = ApplicationPhase.DOCUMENT_COLLECTION
            elif conversation_context and conversation_context.get("completion_percentage", 0) > 0:
                phase = ApplicationPhase.IN_PROGRESS  
            else:
                phase = ApplicationPhase.INITIATED
            
            return self._create_application(
                person_name=detected_person,
                phase=phase,
                source="unified_detection"
            )
        
        # Intent not strong enough yet
        return None, "waiting_for_stronger_intent", ApplicationPhase.DISCOVERY
    
    def _resolve_person_identity(self, 
                               person_name: Optional[str],
                               conversation_context: Optional[Dict],
                               document_entities: Optional[Dict]) -> Optional[str]:
        """Resolve person identity from multiple sources"""
        
        # Priority 1: Explicit person name from documents (knowledge graph)
        if person_name:
            return person_name
        
        # Priority 2: Person entities from document knowledge graph
        if document_entities:
            persons = [node for node in document_entities.get("nodes", []) 
                      if node["type"] == "Person"]
            if persons:
                return persons[0]["id"]
        
        # Priority 3: Full name from conversation
        if conversation_context and conversation_context.get("full_name"):
            return conversation_context["full_name"]
        
        return None
    
    def _find_existing_application(self, person_name: str) -> Optional[Tuple[str, ApplicationPhase]]:
        """Find existing application for person"""
        
        query = """
        MATCH (app:Application)
        WHERE app.applicant_name CONTAINS $person_name 
           OR app.primary_applicant CONTAINS $person_name
        RETURN app.id as application_id, 
               app.phase as phase,
               app.created_at as created_at
        ORDER BY app.created_at DESC
        LIMIT 1
        """
        
        results = self.neo4j_manager.graph.query(query, {"person_name": person_name})
        
        if results:
            app_data = results[0]
            phase = ApplicationPhase(app_data.get("phase", "initiated"))
            return app_data["application_id"], phase
        
        return None
    
    def _should_create_application(self, 
                                 intent: Optional[ApplicationIntent],
                                 conversation_context: Optional[Dict]) -> bool:
        """Determine if application should be created based on intent and context"""
        
        # Always create for document uploads
        if intent == ApplicationIntent.DOCUMENT_UPLOAD:
            return True
        
        # Create for ready-to-apply intent
        if intent == ApplicationIntent.READY_TO_APPLY:
            return True
        
        # Create for serious interest with significant conversation progress
        if intent == ApplicationIntent.SERIOUS_INTEREST and conversation_context:
            completion = conversation_context.get("completion_percentage", 0)
            if completion > 20:  # Some meaningful info collected
                return True
        
        return False
    
    def _create_application(self, 
                          person_name: Optional[str],
                          phase: ApplicationPhase,
                          source: str) -> Tuple[str, str, ApplicationPhase]:
        """Create new application"""
        
        app_id = f"APP_{uuid.uuid4().hex[:8].upper()}"
        
        query = """
        CREATE (app:Application {
            id: $app_id,
            applicant_name: $person_name,
            primary_applicant: $person_name,
            phase: $phase,
            status: $phase,
            created_at: datetime(),
            created_from: $source,
            auto_created: true,
            lifecycle_managed: true
        })
        RETURN app.id as application_id
        """
        
        self.neo4j_manager.graph.query(query, {
            "app_id": app_id,
            "person_name": person_name or "Unknown",
            "phase": phase.value,
            "source": source
        })
        
        logger.info(f"Created application {app_id} for {person_name or 'unknown'} in phase {phase.value}")
        
        return app_id, "created_new", phase
    
    def update_application_phase(self, application_id: str, new_phase: ApplicationPhase) -> bool:
        """Update application phase"""
        
        query = """
        MATCH (app:Application {id: $app_id})
        SET app.phase = $new_phase,
            app.status = $new_phase,
            app.last_updated = datetime()
        RETURN app.id as application_id
        """
        
        result = self.neo4j_manager.graph.query(query, {
            "app_id": application_id,
            "new_phase": new_phase.value
        })
        
        return bool(result)
    
    def link_conversation_to_application(self, 
                                       thread_id: str, 
                                       application_id: str) -> bool:
        """Link chat conversation thread to application"""
        
        query = """
        MATCH (app:Application {id: $app_id})
        MERGE (conv:ConversationThread {thread_id: $thread_id})
        MERGE (app)-[:HAS_CONVERSATION]->(conv)
        SET conv.linked_at = datetime()
        RETURN app.id as application_id
        """
        
        result = self.neo4j_manager.graph.query(query, {
            "app_id": application_id,
            "thread_id": thread_id
        })
        
        return bool(result)

# Global instance
application_manager = UnifiedApplicationManager()

def get_application_manager() -> UnifiedApplicationManager:
    """Get global application manager instance"""
    return application_manager
