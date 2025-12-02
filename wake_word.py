"""
Picovoice Wake Word Detection Module for "Melissa"

This module continuously listens to the microphone and triggers
when the wake word "Melissa" is detected.
"""

import asyncio
import struct
import os
from typing import Callable, Optional
import logging

try:
    import pvporcupine
    import pyaudio
except ImportError:
    raise ImportError(
        "Please install picovoice dependencies: pip install pvporcupine pyaudio"
    )

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Detects the wake word "Melissa" using Picovoice Porcupine.
    
    Usage:
        detector = WakeWordDetector(access_key="your_picovoice_key")
        await detector.start(on_wake_word=my_callback)
    """
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        keyword_path: Optional[str] = None,
        sensitivity: float = 0.5
    ):
        """
        Initialize the wake word detector.
        
        Args:
            access_key: Picovoice access key. If None, reads from PICOVOICE_ACCESS_KEY env var.
            keyword_path: Path to custom .ppn wake word file. If None, uses built-in "jarvis" 
                         (you'll need to create a custom "Melissa" wake word at console.picovoice.ai)
            sensitivity: Detection sensitivity (0.0 to 1.0). Higher = more sensitive but more false positives.
        """
        self.access_key = access_key or os.environ.get("PICOVOICE_ACCESS_KEY")
        if not self.access_key:
            raise ValueError(
                "Picovoice access key required. Set PICOVOICE_ACCESS_KEY env var "
                "or pass access_key parameter. Get your key at https://console.picovoice.ai"
            )
        
        self.keyword_path = keyword_path
        self.sensitivity = sensitivity
        self._porcupine: Optional[pvporcupine.Porcupine] = None
        self._audio_stream = None
        self._pa: Optional[pyaudio.PyAudio] = None
        self._running = False
        
    def _initialize_porcupine(self):
        """Initialize the Porcupine wake word engine."""
        if self.keyword_path and os.path.exists(self.keyword_path):
            # Use custom wake word file
            self._porcupine = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=[self.keyword_path],
                sensitivities=[self.sensitivity]
            )
            logger.info(f"Loaded custom wake word from: {self.keyword_path}")
        else:
            # Use built-in keyword as fallback
            # Available built-in keywords: alexa, americano, blueberry, bumblebee, 
            # computer, grapefruit, grasshopper, hey google, hey siri, jarvis, ok google, 
            # picovoice, porcupine, terminator
            self._porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=["jarvis"],  # Using "jarvis" as fallback - replace with custom Melissa
                sensitivities=[self.sensitivity]
            )
            logger.warning(
                "No custom 'Melissa' wake word file found. Using 'jarvis' as fallback. "
                "Create a custom wake word at https://console.picovoice.ai/ppn"
            )
    
    def _initialize_audio(self):
        """Initialize PyAudio for microphone input."""
        self._pa = pyaudio.PyAudio()
        self._audio_stream = self._pa.open(
            rate=self._porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self._porcupine.frame_length
        )
        logger.info(
            f"Audio initialized - Sample rate: {self._porcupine.sample_rate}, "
            f"Frame length: {self._porcupine.frame_length}"
        )
    
    async def start(
        self,
        on_wake_word: Callable[[], None],
        loop_delay: float = 0.01
    ):
        """
        Start listening for the wake word.
        
        Args:
            on_wake_word: Callback function to call when wake word is detected.
            loop_delay: Small delay between audio processing loops to prevent CPU hogging.
        """
        self._initialize_porcupine()
        self._initialize_audio()
        self._running = True
        
        logger.info("🎤 Wake word detection started. Say 'Melissa' (or 'Jarvis' if using fallback)...")
        
        try:
            while self._running:
                # Read audio frame
                pcm = self._audio_stream.read(
                    self._porcupine.frame_length,
                    exception_on_overflow=False
                )
                pcm = struct.unpack_from("h" * self._porcupine.frame_length, pcm)
                
                # Process audio for wake word
                keyword_index = self._porcupine.process(pcm)
                
                if keyword_index >= 0:
                    logger.info("✨ Wake word detected!")
                    on_wake_word()
                
                # Small delay to prevent CPU hogging
                await asyncio.sleep(loop_delay)
                
        except KeyboardInterrupt:
            logger.info("Wake word detection stopped by user.")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the wake word detector and release resources."""
        self._running = False
        
        if self._audio_stream:
            self._audio_stream.close()
            self._audio_stream = None
            
        if self._pa:
            self._pa.terminate()
            self._pa = None
            
        if self._porcupine:
            self._porcupine.delete()
            self._porcupine = None
            
        logger.info("Wake word detector stopped and resources released.")


class WakeWordGate:
    """
    Gate that controls when the agent should listen based on wake word detection.
    
    This integrates with the main agent loop to enable/disable listening.
    """
    
    def __init__(self, timeout_seconds: float = 30.0):
        """
        Args:
            timeout_seconds: How long to stay active after wake word before going back to sleep.
        """
        self.timeout_seconds = timeout_seconds
        self._is_active = False
        self._active_until: float = 0
        self._lock = asyncio.Lock()
        
    async def activate(self):
        """Activate the gate (called when wake word is detected)."""
        async with self._lock:
            self._is_active = True
            self._active_until = asyncio.get_event_loop().time() + self.timeout_seconds
            logger.info(f"🟢 Gate activated for {self.timeout_seconds}s")
    
    async def deactivate(self):
        """Manually deactivate the gate."""
        async with self._lock:
            self._is_active = False
            logger.info("🔴 Gate deactivated")
    
    async def is_active(self) -> bool:
        """Check if the gate is currently active."""
        async with self._lock:
            if self._is_active:
                current_time = asyncio.get_event_loop().time()
                if current_time > self._active_until:
                    self._is_active = False
                    logger.info("⏰ Gate timed out, going back to sleep")
            return self._is_active
    
    async def extend_timeout(self):
        """Extend the active timeout (call this when user is speaking)."""
        async with self._lock:
            if self._is_active:
                self._active_until = asyncio.get_event_loop().time() + self.timeout_seconds


# Standalone test
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    def on_wake():
        print("\n🎉 WAKE WORD DETECTED! Melissa is listening...\n")
    
    async def main():
        detector = WakeWordDetector()
        await detector.start(on_wake_word=on_wake)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)

