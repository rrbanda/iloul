"""
Context management and main agent class for mortgage application workflow
"""

from typing import Dict, Any
from datetime import datetime
import os
import sqlite3
from dataclasses import dataclass
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.memory import InMemoryStore

from .workflow import create_mortgage_workflow

@dataclass
class MortgageContext:
    """Runtime context schema for mortgage application processing"""
    user_id: str = None
    customer_tier: str = "standard"  # "premium", "standard", "first_time"
    loan_officer_id: str = None
    application_type: str = "purchase"  # "purchase", "refinance", "heloc"
    risk_tolerance: str = "moderate"  # "conservative", "moderate", "aggressive"
    preferred_language: str = "english"
    communication_style: str = "detailed"  # "detailed", "concise", "technical"
    branch_location: str = None
    referral_source: str = None

class MortgageApplicationAgent:
    """LangGraph mortgage application agent with production-ready persistence"""
    
    def __init__(self, use_persistent_storage: bool = True, db_path: str = "data/mortgage_applications.db"):
        """
        Initialize mortgage application agent with configurable persistence and memory store
        
        Args:
            use_persistent_storage: If True, use SQLite persistence. If False, use in-memory
            db_path: Path to SQLite database file for persistent storage
        """
        # Initialize checkpointer (conversation state)
        # For now, use MemorySaver to avoid async compatibility issues
        # TODO: Implement proper async persistence when needed
        print("🧪 Using in-memory storage (fast and reliable)")
        self.checkpointer = MemorySaver()
        
        # Initialize memory store (cross-session customer data)
        # TODO: In production, replace with PostgresStore or similar
        self.store = InMemoryStore()
        print("💾 Customer memory store initialized")
        
        workflow = create_mortgage_workflow()
        self.graph = workflow.compile(checkpointer=self.checkpointer, store=self.store)
    
    def chat(self, message: str, thread_id: str = "default", user_id: str = None, 
             context: MortgageContext = None, recursion_limit: int = 25) -> str:
        """
        Send message to agent with configurable recursion limit, customer memory, and context
        
        Args:
            message: User message
            thread_id: Thread identifier for conversation
            user_id: User identifier for cross-session memory (optional)
            context: Runtime context with customer preferences and metadata (optional)
            recursion_limit: Maximum number of supersteps (default: 25)
        """
        # Create default context if none provided
        if context is None:
            context = MortgageContext(user_id=user_id)
        elif user_id and not context.user_id:
            context.user_id = user_id
            
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": context.user_id,
                "customer_tier": context.customer_tier,
                "loan_officer_id": context.loan_officer_id,
                "application_type": context.application_type,
                "communication_style": context.communication_style
            },
            "recursion_limit": recursion_limit
        }
        
        # Set durability based on customer tier and application type
        durability = self._get_durability_mode(context)
        
        try:
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=message)]}, 
                config=config,
                durability=durability
            )
            
            if result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                return str(last_message)
            return ""
            
        except Exception as e:
            # Handle recursion limit errors gracefully
            if "recursion" in str(e).lower():
                return "I apologize, but the conversation became too complex. Please try rephrasing your question."
            raise e
    
    async def chat_async(self, message: str, thread_id: str = "default", user_id: str = None, 
                        context: MortgageContext = None, recursion_limit: int = 25) -> str:
        """
        Async version of chat method for concurrent processing with context support
        
        Args:
            message: User message
            thread_id: Thread identifier for conversation
            user_id: User identifier for cross-session memory (optional)
            context: Runtime context with customer preferences and metadata (optional)
            recursion_limit: Maximum number of supersteps (default: 25)
        """
        # Create default context if none provided
        if context is None:
            context = MortgageContext(user_id=user_id)
        elif user_id and not context.user_id:
            context.user_id = user_id
            
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": context.user_id,
                "customer_tier": context.customer_tier,
                "loan_officer_id": context.loan_officer_id,
                "application_type": context.application_type,
                "communication_style": context.communication_style
            },
            "recursion_limit": recursion_limit
        }
        
        # Set durability based on customer tier and application type
        durability = self._get_durability_mode(context)
        
        try:
            result = await self.graph.ainvoke(
                {"messages": [HumanMessage(content=message)]}, 
                config=config,
                durability=durability
            )
            
            if result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                return str(last_message)
            return ""
            
        except Exception as e:
            # Handle recursion limit errors gracefully
            if "recursion" in str(e).lower():
                return "I apologize, but the conversation became too complex. Please try rephrasing your question."
            raise e
    
    async def chat_stream_async(self, message: str, thread_id: str = "default", user_id: str = None, 
                              recursion_limit: int = 25, stream_mode: str = "updates"):
        """
        Async streaming agent responses with real-time updates
        
        Args:
            message: User message
            thread_id: Thread identifier for conversation
            user_id: User identifier for cross-session memory (optional)
            recursion_limit: Maximum number of supersteps (default: 25)
            stream_mode: Streaming mode ("updates", "messages", "custom", or list of modes)
            
        Yields:
            Streaming chunks from the agent execution
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            },
            "recursion_limit": recursion_limit
        }
        
        try:
            async for chunk in self.graph.astream(
                {"messages": [HumanMessage(content=message)]}, 
                config=config, 
                stream_mode=stream_mode
            ):
                yield chunk
                
        except Exception as e:
            if "recursion" in str(e).lower():
                yield {"error": "Conversation became too complex. Please try rephrasing your question."}
            else:
                yield {"error": f"Async streaming error: {str(e)}"}
    
    def chat_stream(self, message: str, thread_id: str = "default", user_id: str = None, 
                   recursion_limit: int = 25, stream_mode: str = "updates"):
        """
        Stream agent responses with real-time updates
        
        Args:
            message: User message
            thread_id: Thread identifier for conversation
            user_id: User identifier for cross-session memory (optional)
            recursion_limit: Maximum number of supersteps (default: 25)
            stream_mode: Streaming mode ("updates", "messages", "custom", or list of modes)
            
        Yields:
            Streaming chunks from the agent execution
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            },
            "recursion_limit": recursion_limit
        }
        
        try:
            for chunk in self.graph.stream(
                {"messages": [HumanMessage(content=message)]}, 
                config=config, 
                stream_mode=stream_mode
            ):
                yield chunk
                
        except Exception as e:
            if "recursion" in str(e).lower():
                yield {"error": "Conversation became too complex. Please try rephrasing your question."}
            else:
                yield {"error": f"Streaming error: {str(e)}"}
    
    def chat_stream_multi_mode(self, message: str, thread_id: str = "default", user_id: str = None,
                             recursion_limit: int = 25, stream_modes: list = None):
        """
        Stream agent responses with multiple streaming modes
        
        Args:
            message: User message
            thread_id: Thread identifier for conversation  
            user_id: User identifier for cross-session memory (optional)
            recursion_limit: Maximum number of supersteps (default: 25)
            stream_modes: List of stream modes (default: ["updates", "messages", "custom"])
            
        Yields:
            Tuples of (mode, chunk) from the agent execution
        """
        if stream_modes is None:
            stream_modes = ["updates", "messages", "custom"]
            
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            },
            "recursion_limit": recursion_limit
        }
        
        try:
            for mode, chunk in self.graph.stream(
                {"messages": [HumanMessage(content=message)]}, 
                config=config, 
                stream_mode=stream_modes
            ):
                yield mode, chunk
                
        except Exception as e:
            if "recursion" in str(e).lower():
                yield "error", {"error": "Conversation became too complex. Please try rephrasing your question."}
            else:
                yield "error", {"error": f"Streaming error: {str(e)}"}
    
    def get_state(self, thread_id: str = "default") -> Dict[str, Any]:
        """Get current application state"""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)
        state_dict = dict(state.values)
        
        # Calculate completion percentage
        required_fields = ["full_name", "phone", "email", "annual_income", "employer", 
                          "employment_type", "purchase_price", "property_type", 
                          "property_location", "down_payment", "credit_score"]
        
        collected = [field for field in required_fields if state_dict.get(field)]
        completion_percentage = (len(collected) / len(required_fields)) * 100
        
        state_dict["completion_percentage"] = completion_percentage
        return state_dict
    
    def visualize_graph(self, output_path: str = None) -> str:
        """
        Visualize the workflow graph using LangGraph's built-in visualization
        
        Args:
            output_path: Optional file path to save PNG. If None, returns ASCII representation
            
        Returns:
            ASCII representation if no output_path provided, otherwise saves PNG and returns path
        """
        try:
            if output_path:
                # Save PNG to file
                png_data = self.graph.get_graph().draw_mermaid_png()
                with open(output_path, "wb") as f:
                    f.write(png_data)
                return f"Graph visualization saved to: {output_path}"
            else:
                # Return ASCII representation for terminal/logging
                return self.graph.get_graph().draw_ascii()
        except Exception as e:
            return f"Error generating graph visualization: {str(e)}"
    
    def save_customer_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """
        Save customer profile data to long-term memory
        
        Args:
            user_id: Unique customer identifier
            profile_data: Customer profile information
        """
        if not user_id:
            return
            
        namespace = (user_id, "profile")
        self.store.put(namespace, "customer_profile", profile_data)
        print(f"💾 Saved customer profile for user {user_id}")
    
    def get_customer_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve customer profile data from long-term memory
        
        Args:
            user_id: Unique customer identifier
            
        Returns:
            Customer profile data or empty dict if not found
        """
        if not user_id:
            return {}
            
        namespace = (user_id, "profile")
        try:
            profile_item = self.store.get(namespace, "customer_profile")
            return profile_item.value if profile_item else {}
        except Exception as e:
            print(f"⚠️ Error retrieving customer profile: {e}")
            return {}
    
    def save_application_milestone(self, user_id: str, milestone_data: Dict[str, Any]) -> None:
        """
        Save application milestone to customer history
        
        Args:
            user_id: Unique customer identifier
            milestone_data: Milestone information
        """
        if not user_id:
            return
            
        namespace = (user_id, "application_history")
        milestone_id = f"milestone_{datetime.now().timestamp()}"
        milestone_data["timestamp"] = datetime.now().isoformat()
        
        self.store.put(namespace, milestone_id, milestone_data)
        print(f"📊 Saved application milestone for user {user_id}")
    
    def get_customer_application_history(self, user_id: str) -> list:
        """
        Retrieve customer's application history
        
        Args:
            user_id: Unique customer identifier
            
        Returns:
            List of application milestones
        """
        if not user_id:
            return []
            
        namespace = (user_id, "application_history")
        try:
            items = self.store.search(namespace)
            return [item.value for item in items]
        except Exception as e:
            print(f"⚠️ Error retrieving application history: {e}")
            return []
    
    def _get_durability_mode(self, context: MortgageContext) -> str:
        """
        Determine appropriate durability mode based on customer context and risk
        
        Args:
            context: Customer and application context
            
        Returns:
            Durability mode: "sync", "async", or "exit"
        """
        # High-value applications or premium customers get maximum durability
        if context.customer_tier == "premium" or context.application_type in ["refinance", "heloc"]:
            return "sync"  # Maximum durability for important customers/applications
        
        # Standard customers get balanced performance and durability
        elif context.customer_tier == "standard":
            return "async"  # Good durability with reasonable performance
        
        # First-time buyers or development mode get basic durability
        else:
            return "exit"  # Basic durability, best performance
    
    @staticmethod
    def create_premium_context(user_id: str, loan_officer_id: str = None, **kwargs) -> MortgageContext:
        """Create context for premium customers with enhanced service level"""
        return MortgageContext(
            user_id=user_id,
            customer_tier="premium",
            loan_officer_id=loan_officer_id,
            communication_style="detailed",
            **kwargs
        )
    
    @staticmethod
    def create_first_time_buyer_context(user_id: str, **kwargs) -> MortgageContext:
        """Create context for first-time home buyers with educational focus"""
        return MortgageContext(
            user_id=user_id,
            customer_tier="first_time",
            communication_style="detailed",
            risk_tolerance="conservative",
            **kwargs
        )
    
    @staticmethod
    def create_refinance_context(user_id: str, **kwargs) -> MortgageContext:
        """Create context for refinance applications"""
        return MortgageContext(
            user_id=user_id,
            application_type="refinance",
            communication_style="concise",  # Experienced customers
            **kwargs
        )
    
    def start_new_conversation(self) -> str:
        """Start new conversation"""
        return """Hello there! I'm absolutely delighted to help you with your mortgage application today! 

I know applying for a home loan can feel like a big step, but I want you to know that I'm here to make this process as smooth and enjoyable as possible. We'll work together to get you pre-qualified, and I'm genuinely excited to be part of your homeownership journey!

We'll chat about:
• Your contact information
• Your employment and income details  
• The amazing property you're hoping to buy
• Your financial situation

I promise to keep things conversational and stress-free. Think of this as just a friendly chat where I get to learn about your goals and help make them happen!

So, let's start with something easy - what's your full name? I'd love to know who I'm working with!"""

class MortgageConversationWorkflow:
    """LangGraph-native workflow - uses thread IDs for session management"""
    
    def __init__(self, config=None, use_persistent_storage: bool = True):
        """
        Initialize mortgage conversation workflow
        
        Args:
            config: Optional configuration (for future use)
            use_persistent_storage: Whether to use persistent SQLite storage
        """
        self.agent = MortgageApplicationAgent(use_persistent_storage=use_persistent_storage)
    
    async def start_session(self, user_id: str = None) -> Dict[str, Any]:
        """Start new session - LangGraph handles persistence via thread IDs"""
        import uuid
        session_id = str(uuid.uuid4())
        initial_response = self.agent.start_new_conversation()
        return {
            "session_id": session_id,
            "response": initial_response,
            "completion_percentage": 0.0,
            "is_complete": False,
            "phase": "introduction"
        }
    
    async def process_message(self, session_id: str, message: str, user_id: str = None, recursion_limit: int = 25) -> Dict[str, Any]:
        """Process message with async execution - LangGraph automatically manages conversation state"""
        # Use async chat for better concurrency
        response = await self.agent.chat_async(message, thread_id=session_id, user_id=user_id, recursion_limit=recursion_limit)
        state = self.agent.get_state(thread_id=session_id)
        
        # Determine completion based on actual collected data, not just percentage
        collected_fields = [
            state.get("full_name"),
            state.get("phone"),
            state.get("email"),
            state.get("annual_income"),
            state.get("employer"),
            state.get("employment_type"),
            state.get("purchase_price"),
            state.get("property_type"),
            state.get("property_location"),
            state.get("down_payment"),
            state.get("credit_score")
        ]
        
        is_complete = all(field is not None and field != "" for field in collected_fields)
        completion_percentage = 100.0 if is_complete else min(sum(1 for field in collected_fields if field) / len(collected_fields) * 100, 99.0)
        
        # Determine current phase based on collected data
        phase = "in_progress"
        if is_complete:
            phase = "complete"
        elif state.get("full_name") and state.get("phone") and state.get("email"):
            if state.get("annual_income") and state.get("employer"):
                if state.get("purchase_price") and state.get("property_type"):
                    phase = "financial_info"
                else:
                    phase = "property_info"
            else:
                phase = "employment_info"
        elif state.get("full_name") or state.get("phone") or state.get("email"):
            phase = "personal_info"
        else:
            phase = "introduction"
        
        return {
            "session_id": session_id,
            "response": response,
            "completion_percentage": completion_percentage,
            "is_complete": is_complete,
            "phase": phase,
            "application_data": {
                "personal_info": {
                    "full_name": state.get("full_name"),
                    "phone": state.get("phone"),
                    "email": state.get("email")
                },
                "employment_info": {
                    "annual_income": state.get("annual_income"),
                    "employer": state.get("employer"),
                    "employment_type": state.get("employment_type")
                },
                "property_info": {
                    "purchase_price": state.get("purchase_price"),
                    "property_type": state.get("property_type"),
                    "property_location": state.get("property_location")
                },
                "financial_info": {
                    "down_payment": state.get("down_payment"),
                    "credit_score": state.get("credit_score")
                }
            }
        }
    
    async def get_application_status(self, session_id: str) -> Dict[str, Any]:
        """Get application status - LangGraph persists state automatically"""
        state = self.agent.get_state(thread_id=session_id)
        completion_percentage = state.get("completion_percentage", 0.0)
        
        return {
            "session_id": session_id,
            "status": "success",
            "completion_percentage": completion_percentage,
            "current_phase": "complete" if completion_percentage >= 100 else "in_progress",
            "application_data": state
        }
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current session state for validation"""
        try:
            # Get the current state from the agent
            state = self.agent.get_state(thread_id=session_id)
            
            if not state:
                return {
                    "session_id": session_id,
                    "is_complete": False,
                    "completion_percentage": 0.0,
                    "collected_data": {}
                }
            
            # Extract relevant state information
            completion_percentage = state.get("completion_percentage", 0.0)
            current_phase = state.get("current_phase", "data_collection")
            
            # Determine if application is complete based on collected data
            collected_fields = [
                state.get("full_name"),
                state.get("phone"),
                state.get("email"),
                state.get("annual_income"),
                state.get("employer"),
                state.get("employment_type"),
                state.get("purchase_price"),
                state.get("property_type"),
                state.get("property_location"),
                state.get("down_payment"),
                state.get("credit_score")
            ]
            
            is_complete = all(field is not None and field != "" for field in collected_fields)
            
            return {
                "session_id": session_id,
                "is_complete": is_complete,
                "completion_percentage": completion_percentage,
                "current_phase": current_phase,
                "collected_data": {
                    "full_name": state.get("full_name"),
                    "phone": state.get("phone"),
                    "email": state.get("email"),
                    "annual_income": state.get("annual_income"),
                    "employer": state.get("employer"),
                    "employment_type": state.get("employment_type"),
                    "purchase_price": state.get("purchase_price"),
                    "property_type": state.get("property_type"),
                    "property_location": state.get("property_location"),
                    "down_payment": state.get("down_payment"),
                    "credit_score": state.get("credit_score")
                }
            }
            
        except Exception as e:
            print(f"Error getting session state: {e}")
            return {
                "session_id": session_id,
                "is_complete": False,
                "completion_percentage": 0.0,
                "collected_data": {}
            }
    
    async def process_message_stream(self, session_id: str, message: str, user_id: str = None, 
                                   recursion_limit: int = 25, stream_mode: str = "updates"):
        """
        Process message with streaming support for real-time updates
        
        Args:
            session_id: Session identifier
            message: User message
            user_id: User identifier for cross-session memory
            recursion_limit: Maximum supersteps
            stream_mode: Streaming mode ("updates", "messages", "custom")
            
        Yields:
            Streaming chunks with progress updates
        """
        try:
            # Stream the agent response using async streaming
            async for chunk in self.agent.chat_stream_async(
                message, 
                thread_id=session_id, 
                user_id=user_id,
                recursion_limit=recursion_limit,
                stream_mode=stream_mode
            ):
                # Add session metadata to each chunk
                if isinstance(chunk, dict):
                    chunk["session_id"] = session_id
                    chunk["stream_mode"] = stream_mode
                
                yield chunk
                
            # Get final state after streaming completes
            final_state = self.agent.get_state(thread_id=session_id)
            completion_percentage = final_state.get("completion_percentage", 0.0)
            
            # Yield final status update
            yield {
                "type": "status_update",
                "session_id": session_id,
                "completion_percentage": completion_percentage,
                "is_complete": completion_percentage >= 100.0,
                "phase": self._determine_phase(final_state)
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "session_id": session_id,
                "error": str(e),
                "message": "An error occurred during streaming"
            }
    
    def _determine_phase(self, state: Dict[str, Any]) -> str:
        """Determine current application phase based on collected data"""
        completion_percentage = state.get("completion_percentage", 0.0)
        
        if completion_percentage >= 100.0:
            return "complete"
        elif state.get("full_name") and state.get("phone") and state.get("email"):
            if state.get("annual_income") and state.get("employer"):
                if state.get("purchase_price") and state.get("property_type"):
                    return "financial_info"
                else:
                    return "property_info"
            else:
                return "employment_info"
        elif state.get("full_name") or state.get("phone") or state.get("email"):
            return "personal_info"
        else:
            return "introduction"
