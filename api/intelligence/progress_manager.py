"""
Progress management for WebSocket status communication during repository processing.
"""
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ProgressManager:
    """
    Manages status updates to the frontend via WebSocket during repository processing.
    
    Provides a simple interface to send status messages that match the existing
    UI status display pattern.
    """
    
    def __init__(self, websocket: WebSocket):
        """
        Initialize progress manager with WebSocket connection.
        
        Args:
            websocket: Active WebSocket connection to frontend
        """
        self.websocket = websocket
        self._connected = True
    
    async def update_status(self, message: str) -> None:
        """
        Send a status update to the frontend.
        
        Args:
            message: Human-readable status message to display
        """
        if not self._connected:
            logger.warning("Attempted to send status to disconnected WebSocket")
            return
            
        try:
            # Send status with prefix so frontend can distinguish from chat content
            status_message = f"STATUS:{message}"
            await self.websocket.send_text(status_message)
            logger.info(f"Sent status update: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
            self._connected = False
    
    async def start_phase(self, phase_name: str) -> None:
        """
        Convenience method for starting a new processing phase.
        
        Args:
            phase_name: Name of the phase being started
        """
        await self.update_status(f"🔄 {phase_name}...")
    
    async def complete_phase(self, phase_name: str) -> None:
        """
        Convenience method for completing a processing phase.
        
        Args:
            phase_name: Name of the phase being completed
        """
        await self.update_status(f"✅ {phase_name} complete")
    
    async def enrichment_progress(self, current: int, total: int, item_name: str = "components") -> None:
        """
        Send enrichment progress update.
        
        Args:
            current: Number of items processed
            total: Total number of items to process
            item_name: Type of item being processed (e.g., "components", "files")
        """
        await self.update_status(f"🔍 Analyzing {current} of {total} {item_name}...")
    
    def is_connected(self) -> bool:
        """
        Check if WebSocket is still connected.
        
        Returns:
            True if WebSocket appears to be connected
        """
        return self._connected 