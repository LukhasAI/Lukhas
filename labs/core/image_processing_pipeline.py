"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - EVENT-DRIVEN IMAGE PROCESSING PIPELINE
║ Distributed image processing using actor-centric event-driven architecture
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: image_processing_pipeline.py
║ Path: lukhas/core/image_processing_pipeline.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Implements TODO 95: Event-driven image processing pipeline triggered by
║ NewImageUploaded events. Demonstrates colony-based actor architecture with
║ independent processing stages connected via event bus for scalable AI workflows.
╚══════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# Try to import image processing libraries (optional)
try:
    import numpy as np
    from PIL import Image

    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False

# Import our event bus and actor system
try:
    from .event_bus import EventBus
except ImportError:
    # Define minimal interfaces for testing

    class EventBus:
        def __init__(self):
            self.subscribers = defaultdict(list)

        def subscribe(self, event_type: str, handler: Callable):
            self.subscribers[event_type].append(handler)

        def publish(self, event_type: str, event: Any):
            for handler in self.subscribers[event_type]:
                handler(event_type, event)


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for the image processing pipeline"""

    NEW_IMAGE_UPLOADED = "new_image_uploaded"
    IMAGE_VALIDATED = "image_validated"
    IMAGE_PREPROCESSED = "image_preprocessed"
    FEATURES_EXTRACTED = "features_extracted"
    IMAGE_CLASSIFIED = "image_classified"
    THUMBNAIL_GENERATED = "thumbnail_generated"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"

    # Colony coordination events
    CALL_FOR_PROPOSALS = "call_for_proposals"
    PROPOSAL_SUBMITTED = "proposal_submitted"
    CONTRACT_AWARDED = "contract_awarded"

    # Resource management
    RESOURCE_AVAILABLE = "resource_available"
    RESOURCE_BUSY = "resource_busy"


@dataclass
class ImageEvent:
    """Base event for image processing pipeline"""

    event_id: str
    event_type: EventType
    timestamp: float
    image_id: str
    payload: dict[str, Any]
    metadata: dict[str, Any]
    correlation_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImageEvent":
        data["event_type"] = EventType(data["event_type"])
        return cls(**data)


class ProcessingStage(Enum):
    """Stages in the image processing pipeline"""

    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    CLASSIFICATION = "classification"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    AGGREGATION = "aggregation"


class ImageProcessingColony:
    """
    A colony of actors specialized in a specific image processing task.
    Each colony operates independently and communicates via events.
    """

    def __init__(
        self,
        colony_name: str,
        stage: ProcessingStage,
        event_bus: EventBus,
        num_workers: int = 3,
    ):
        self.colony_name = colony_name
        self.stage = stage
        self.event_bus = event_bus
        self.num_workers = num_workers

        # Colony state
        self.workers: list[Any] = []
        self.supervisor = None
        self.work_queue: asyncio.Queue = asyncio.Queue()
        self.results_cache: dict[str, Any] = {}

        # Metrics
        self.metrics = {
            "processed": 0,
            "failed": 0,
            "avg_processing_time": 0.0,
            "total_processing_time": 0.0,
        }

        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        """Start the colony with supervisor and workers"""
        if self._running:
            return

        self._running = True

        # Create supervisor actor
        self.supervisor = ColonySupervisor(f"{self.colony_name}_supervisor", self.stage, self.event_bus)

        # Create worker actors
        for i in range(self.num_workers):
            worker = ImageProcessingWorker(
                f"{self.colony_name}_worker_{i}",
                self.stage,
                self.process_image,
            )
            self.workers.append(worker)
            self._tasks.append(asyncio.create_task(self._worker_loop(worker)))

        # Subscribe to relevant events
        self._subscribe_to_events()

        # Start supervisor loop
        self._tasks.append(asyncio.create_task(self._supervisor_loop()))

        logger.info(f"Colony {self.colony_name} started with {self.num_workers} workers")

    async def stop(self) -> None:
        """Stop the colony gracefully"""
        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Clear workers
        self.workers.clear()

        logger.info(f"Colony {self.colony_name} stopped")

    def _subscribe_to_events(self) -> None:
        """Subscribe to events based on processing stage"""
        if self.stage == ProcessingStage.VALIDATION:
            self.event_bus.subscribe(EventType.NEW_IMAGE_UPLOADED.value, self._handle_event)
        elif self.stage == ProcessingStage.PREPROCESSING:
            self.event_bus.subscribe(EventType.IMAGE_VALIDATED.value, self._handle_event)
        elif self.stage == ProcessingStage.FEATURE_EXTRACTION:
            self.event_bus.subscribe(EventType.IMAGE_PREPROCESSED.value, self._handle_event)
        elif self.stage == ProcessingStage.CLASSIFICATION:
            self.event_bus.subscribe(EventType.FEATURES_EXTRACTED.value, self._handle_event)
        elif self.stage == ProcessingStage.THUMBNAIL_GENERATION:
            self.event_bus.subscribe(EventType.IMAGE_VALIDATED.value, self._handle_event)

        # All colonies can respond to call for proposals
        self.event_bus.subscribe(EventType.CALL_FOR_PROPOSALS.value, self._handle_call_for_proposals)

    def _handle_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Handle incoming events"""
        try:
            event = ImageEvent.from_dict(event_data)

            # Add to work queue
            asyncio.create_task(self.work_queue.put(event))

        except Exception as e:
            logger.error(f"Error handling event in {self.colony_name}: {e}")

    def _handle_call_for_proposals(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Handle call for proposals for dynamic task allocation"""
        try:
            event = ImageEvent.from_dict(event_data)

            # Check if we can handle this type of work
            if self._can_handle_work(event.payload):
                # Submit proposal
                proposal = self._create_proposal(event)

                proposal_event = ImageEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.PROPOSAL_SUBMITTED,
                    timestamp=time.time(),
                    image_id=event.image_id,
                    payload={
                        "colony": self.colony_name,
                        "stage": self.stage.value,
                        "proposal": proposal,
                        "correlation_id": event.event_id,
                    },
                    metadata={"colony_metrics": self.metrics},
                    correlation_id=event.correlation_id,
                )

                self.event_bus.publish(
                    EventType.PROPOSAL_SUBMITTED.value,
                    proposal_event.to_dict(),
                )

        except Exception as e:
            logger.error(f"Error handling call for proposals: {e}")

    def _can_handle_work(self, work_spec: dict[str, Any]) -> bool:
        """Check if colony can handle the specified work"""
        required_stage = work_spec.get("stage")
        if required_stage and ProcessingStage(required_stage) != self.stage:
            return False

        # Check resource availability
        queue_size = self.work_queue.qsize()
        if queue_size > self.num_workers * 2:
            return False  # Too busy

        return True

    def _create_proposal(self, event: ImageEvent) -> dict[str, Any]:
        """Create a proposal for handling work"""
        # Calculate confidence based on current load and performance
        queue_size = self.work_queue.qsize()
        avg_time = self.metrics["avg_processing_time"]

        # Simple scoring: lower queue and faster processing = higher score
        load_score = max(0, 1.0 - (queue_size / (self.num_workers * 3)))
        speed_score = 1.0 / (1.0 + avg_time) if avg_time > 0 else 1.0

        confidence = (load_score + speed_score) / 2
        estimated_time = avg_time * (1 + queue_size)

        return {
            "confidence": confidence,
            "estimated_time": estimated_time,
            "cost": self.num_workers * avg_time,  # Simple cost model
            "capabilities": [self.stage.value],
        }

    async def _supervisor_loop(self) -> None:
        """Supervisor monitors workers and handles failures"""
        while self._running:
            try:
                # Check worker health
                for worker in self.workers:
                    if hasattr(worker, "is_healthy") and not worker.is_healthy():
                        logger.warning(f"Worker {worker.worker_id} unhealthy, restarting")
                        # In real implementation, would restart worker

                # Aggregate metrics
                if self.metrics["processed"] > 0:
                    self.metrics["avg_processing_time"] = (
                        self.metrics["total_processing_time"] / self.metrics["processed"]
                    )

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Supervisor error in {self.colony_name}: {e}")

    async def _worker_loop(self, worker: "ImageProcessingWorker") -> None:
        """Worker processes events from the queue"""
        while self._running:
            try:
                # Get work from queue
                event = await asyncio.wait_for(self.work_queue.get(), timeout=1.0)

                # Process the image
                start_time = time.time()
                result = await worker.process(event)
                processing_time = time.time() - start_time

                # Update metrics
                self.metrics["processed"] += 1
                self.metrics["total_processing_time"] += processing_time

                # Publish result event
                if result:
                    self._publish_result(event, result)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error in {self.colony_name}: {e}")
                self.metrics["failed"] += 1

                # Publish failure event
                self._publish_failure(event, str(e))

    def _publish_result(self, original_event: ImageEvent, result: dict[str, Any]) -> None:
        """Publish processing result"""
        # Determine output event type based on stage
        output_event_type = {
            ProcessingStage.VALIDATION: EventType.IMAGE_VALIDATED,
            ProcessingStage.PREPROCESSING: EventType.IMAGE_PREPROCESSED,
            ProcessingStage.FEATURE_EXTRACTION: EventType.FEATURES_EXTRACTED,
            ProcessingStage.CLASSIFICATION: EventType.IMAGE_CLASSIFIED,
            ProcessingStage.THUMBNAIL_GENERATION: EventType.THUMBNAIL_GENERATED,
        }.get(self.stage, EventType.PROCESSING_COMPLETED)

        result_event = ImageEvent(
            event_id=str(uuid.uuid4()),
            event_type=output_event_type,
            timestamp=time.time(),
            image_id=original_event.image_id,
            payload={
                **original_event.payload,
                f"{self.stage.value}_result": result,
            },
            metadata={
                **original_event.metadata,
                "processing_colony": self.colony_name,
                "processing_time": result.get("processing_time", 0),
            },
            correlation_id=original_event.correlation_id,
        )

        self.event_bus.publish(output_event_type.value, result_event.to_dict())

    def _publish_failure(self, event: Optional[ImageEvent], error: str) -> None:
        """Publish processing failure event"""
        failure_event = ImageEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PROCESSING_FAILED,
            timestamp=time.time(),
            image_id=event.image_id if event else "unknown",
            payload={
                "stage": self.stage.value,
                "error": error,
                "colony": self.colony_name,
            },
            metadata={"original_event": event.to_dict() if event else None},
            correlation_id=event.correlation_id if event else None,
        )

        self.event_bus.publish(EventType.PROCESSING_FAILED.value, failure_event.to_dict())

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Process image based on stage - override in subclasses"""
        # This is a placeholder - each stage would have its own implementation
        await asyncio.sleep(0.1)  # Simulate processing

        return {
            "status": "processed",
            "stage": self.stage.value,
            "processing_time": 0.1,
        }


class ColonySupervisor:
    """Supervisor actor for a colony"""

    def __init__(self, supervisor_id: str, stage: ProcessingStage, event_bus: EventBus):
        self.supervisor_id = supervisor_id
        self.stage = stage
        self.event_bus = event_bus
        self.worker_states: dict[str, str] = {}

    def handle_worker_failure(self, worker_id: str, error: Exception) -> str:
        """Decide how to handle worker failure"""
        # Simple strategy: always restart
        logger.info(f"Supervisor {self.supervisor_id} restarting worker {worker_id}")
        return "restart"


class ImageProcessingWorker:
    """Worker actor for image processing"""

    def __init__(self, worker_id: str, stage: ProcessingStage, process_func: Callable):
        self.worker_id = worker_id
        self.stage = stage
        self.process_func = process_func
        self.processed_count = 0
        self.error_count = 0
        self._healthy = True

    async def process(self, event: ImageEvent) -> dict[str, Any]:
        """Process an image event"""
        try:
            result = await self.process_func(event)
            self.processed_count += 1
            return result
        except Exception:
            self.error_count += 1
            if self.error_count > 5:
                self._healthy = False
            raise

    def is_healthy(self) -> bool:
        """Check if worker is healthy"""
        return self._healthy and self.error_count < 10


# Specialized processing implementations


class ValidationColony(ImageProcessingColony):
    """Colony specialized in image validation"""

    def __init__(self, event_bus: EventBus, num_workers: int = 2):
        super().__init__(
            "validation_colony",
            ProcessingStage.VALIDATION,
            event_bus,
            num_workers,
        )

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Validate uploaded image"""
        image_path = event.payload.get("image_path")

        if not image_path:
            raise ValueError("No image path provided")

        # Validate file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Check file type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError(f"Invalid image type: {mime_type}")

        # Get file stats
        file_stats = os.stat(image_path)

        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024
        if file_stats.st_size > max_size:
            raise ValueError(f"Image too large: {file_stats.st_size} bytes")

        # If PIL available, validate image integrity
        if IMAGING_AVAILABLE:
            try:
                with Image.open(image_path) as img:
                    img.verify()
                    # Re-open for getting info (verify closes the file)
                    img = Image.open(image_path)
                    width, height = img.size
                    format = img.format
            except Exception as e:
                raise ValueError(f"Invalid image file: {e}")
        else:
            width, height, format = 0, 0, "unknown"

        return {
            "valid": True,
            "mime_type": mime_type,
            "size_bytes": file_stats.st_size,
            "width": width,
            "height": height,
            "format": format,
            "processing_time": 0.05,
        }


class PreprocessingColony(ImageProcessingColony):
    """Colony specialized in image preprocessing"""

    def __init__(self, event_bus: EventBus, num_workers: int = 3):
        super().__init__(
            "preprocessing_colony",
            ProcessingStage.PREPROCESSING,
            event_bus,
            num_workers,
        )

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Preprocess validated image"""
        image_path = event.payload.get("image_path")

        if IMAGING_AVAILABLE:
            # Load and preprocess image
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize to standard size
                standard_size = (224, 224)
                img_resized = img.resize(standard_size, Image.Resampling.LANCZOS)

                # Save preprocessed image
                preprocessed_path = image_path.replace(".", "_preprocessed.")
                img_resized.save(preprocessed_path, quality=95)

                return {
                    "preprocessed_path": preprocessed_path,
                    "original_size": img.size,
                    "new_size": standard_size,
                    "processing_time": 0.1,
                }
        else:
            # Simulate preprocessing
            return {
                "preprocessed_path": image_path,
                "status": "simulated",
                "processing_time": 0.1,
            }


class FeatureExtractionColony(ImageProcessingColony):
    """Colony specialized in feature extraction"""

    def __init__(self, event_bus: EventBus, num_workers: int = 4):
        super().__init__(
            "feature_extraction_colony",
            ProcessingStage.FEATURE_EXTRACTION,
            event_bus,
            num_workers,
        )

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Extract features from preprocessed image"""
        preprocessed_path = event.payload.get("preprocessed_path", event.payload.get("image_path"))

        if IMAGING_AVAILABLE:
            with Image.open(preprocessed_path) as img:
                # Convert to numpy array
                img_array = np.array(img)

                # Extract simple features
                features = {
                    "mean_rgb": img_array.mean(axis=(0, 1)).tolist(),
                    "std_rgb": img_array.std(axis=(0, 1)).tolist(),
                    "histogram": [np.histogram(img_array[:, :, i], bins=8)[0].tolist() for i in range(3)],
                }

                # In real implementation, would use CNN features
                return {
                    "features": features,
                    "feature_dim": 27,  # 3 mean + 3 std + 3*8 histogram
                    "processing_time": 0.2,
                }
        else:
            # Simulate feature extraction
            return {
                "features": {"simulated": True},
                "feature_dim": 128,
                "processing_time": 0.2,
            }


class ClassificationColony(ImageProcessingColony):
    """Colony specialized in image classification"""

    def __init__(self, event_bus: EventBus, num_workers: int = 2):
        super().__init__(
            "classification_colony",
            ProcessingStage.CLASSIFICATION,
            event_bus,
            num_workers,
        )

        # Mock classification categories
        self.categories = [
            "landscape",
            "portrait",
            "animal",
            "object",
            "document",
            "artwork",
            "food",
            "vehicle",
        ]

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Classify image based on extracted features"""
        features = event.payload.get("features_extracted_result", {}).get("features", {})

        # Simulate classification (in reality would use ML model)
        # Generate mock confidence scores
        scores = {}
        for _i, category in enumerate(self.categories):
            # Use feature values to generate pseudo-random scores
            score = abs(hash(str(features) + category) % 100) / 100.0
            scores[category] = score

        # Sort by confidence
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "predicted_class": sorted_scores[0][0],
            "confidence": sorted_scores[0][1],
            "top_3": [{"class": cls, "confidence": conf} for cls, conf in sorted_scores[:3]],
            "all_scores": scores,
            "processing_time": 0.15,
        }


class ThumbnailColony(ImageProcessingColony):
    """Colony specialized in thumbnail generation"""

    def __init__(self, event_bus: EventBus, num_workers: int = 2):
        super().__init__(
            "thumbnail_colony",
            ProcessingStage.THUMBNAIL_GENERATION,
            event_bus,
            num_workers,
        )

    async def process_image(self, event: ImageEvent) -> dict[str, Any]:
        """Generate thumbnail for validated image"""
        image_path = event.payload.get("image_path")

        if IMAGING_AVAILABLE:
            with Image.open(image_path) as img:
                # Create thumbnail
                thumbnail_size = (128, 128)
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

                # Save thumbnail
                thumbnail_path = image_path.replace(".", "_thumb.")
                img.save(thumbnail_path, quality=85)

                return {
                    "thumbnail_path": thumbnail_path,
                    "thumbnail_size": img.size,
                    "processing_time": 0.08,
                }
        else:
            # Simulate thumbnail generation
            return {
                "thumbnail_path": image_path.replace(".", "_thumb."),
                "thumbnail_size": (128, 128),
                "status": "simulated",
                "processing_time": 0.08,
            }


class AggregationColony(ImageProcessingColony):
    """Colony that aggregates results from all processing stages"""

    def __init__(self, event_bus: EventBus):
        super().__init__(
            "aggregation_colony",
            ProcessingStage.AGGREGATION,
            event_bus,
            num_workers=1,
        )

        # Track processing state for each image
        self.image_states: dict[str, dict[str, Any]] = {}

        # Subscribe to all result events
        result_events = [
            EventType.IMAGE_VALIDATED,
            EventType.IMAGE_PREPROCESSED,
            EventType.FEATURES_EXTRACTED,
            EventType.IMAGE_CLASSIFIED,
            EventType.THUMBNAIL_GENERATED,
            EventType.PROCESSING_FAILED,
        ]

        for event_type in result_events:
            self.event_bus.subscribe(event_type.value, self._handle_result_event)

    def _handle_result_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Handle result events and aggregate state"""
        try:
            event = ImageEvent.from_dict(event_data)
            image_id = event.image_id

            # Initialize state if needed
            if image_id not in self.image_states:
                self.image_states[image_id] = {
                    "start_time": time.time(),
                    "stages_completed": [],
                    "results": {},
                    "errors": [],
                }

            state = self.image_states[image_id]

            # Handle failure
            if event.event_type == EventType.PROCESSING_FAILED:
                state["errors"].append(
                    {
                        "stage": event.payload.get("stage"),
                        "error": event.payload.get("error"),
                        "timestamp": event.timestamp,
                    }
                )
            else:
                # Record successful stage completion
                stage_name = self._event_type_to_stage(event.event_type)
                state["stages_completed"].append(stage_name)
                state["results"][stage_name] = event.payload

            # Check if processing is complete
            if self._is_processing_complete(state):
                self._publish_completion_event(image_id, state)

        except Exception as e:
            logger.error(f"Error in aggregation: {e}")

    def _event_type_to_stage(self, event_type: EventType) -> str:
        """Map event type to stage name"""
        mapping = {
            EventType.IMAGE_VALIDATED: "validation",
            EventType.IMAGE_PREPROCESSED: "preprocessing",
            EventType.FEATURES_EXTRACTED: "feature_extraction",
            EventType.IMAGE_CLASSIFIED: "classification",
            EventType.THUMBNAIL_GENERATED: "thumbnail_generation",
        }
        return mapping.get(event_type, "unknown")

    def _is_processing_complete(self, state: dict[str, Any]) -> bool:
        """Check if all required stages are complete"""
        required_stages = {
            "validation",
            "preprocessing",
            "feature_extraction",
            "classification",
        }
        completed = set(state["stages_completed"])

        # Complete if all required stages done or if there were critical errors
        return required_stages.issubset(completed) or len(state["errors"]) > 2

    def _publish_completion_event(self, image_id: str, state: dict[str, Any]) -> None:
        """Publish final processing completion event"""
        total_time = time.time() - state["start_time"]

        completion_event = ImageEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PROCESSING_COMPLETED,
            timestamp=time.time(),
            image_id=image_id,
            payload={
                "success": len(state["errors"]) == 0,
                "stages_completed": state["stages_completed"],
                "results": state["results"],
                "errors": state["errors"],
                "total_processing_time": total_time,
            },
            metadata={"aggregated_by": self.colony_name},
        )

        self.event_bus.publish(EventType.PROCESSING_COMPLETED.value, completion_event.to_dict())

        # Clean up state
        del self.image_states[image_id]


class ImageProcessingPipeline:
    """
    Main orchestrator for the image processing pipeline.
    Manages colonies and coordinates the overall workflow.
    """

    def __init__(self):
        self.event_bus = EventBus()
        self.colonies: list[ImageProcessingColony] = []
        self._running = False

    async def start(self) -> None:
        """Start the image processing pipeline"""
        if self._running:
            return

        # Create colonies
        self.colonies = [
            ValidationColony(self.event_bus, num_workers=2),
            PreprocessingColony(self.event_bus, num_workers=3),
            FeatureExtractionColony(self.event_bus, num_workers=4),
            ClassificationColony(self.event_bus, num_workers=2),
            ThumbnailColony(self.event_bus, num_workers=2),
            AggregationColony(self.event_bus),
        ]

        # Start all colonies
        for colony in self.colonies:
            await colony.start()

        self._running = True
        logger.info("Image processing pipeline started")

    async def stop(self) -> None:
        """Stop the pipeline gracefully"""
        if not self._running:
            return

        # Stop all colonies
        for colony in self.colonies:
            await colony.stop()

        self.colonies.clear()
        self._running = False
        logger.info("Image processing pipeline stopped")

    async def process_image(self, image_path: str, metadata: Optional[dict[str, Any]] = None) -> str:
        """
        Process a new image through the pipeline.
        Returns correlation ID for tracking.
        """
        if not self._running:
            raise RuntimeError("Pipeline not started")

        # Generate IDs
        image_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        # Create initial event
        upload_event = ImageEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.NEW_IMAGE_UPLOADED,
            timestamp=time.time(),
            image_id=image_id,
            payload={"image_path": image_path, "upload_time": time.time()},
            metadata=metadata or {},
            correlation_id=correlation_id,
        )

        # Publish to event bus
        self.event_bus.publish(EventType.NEW_IMAGE_UPLOADED.value, upload_event.to_dict())

        logger.info(f"Started processing image {image_id} from {image_path}")
        return correlation_id

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get statistics from all colonies"""
        stats = {}

        for colony in self.colonies:
            stats[colony.colony_name] = {
                "stage": colony.stage.value,
                "workers": colony.num_workers,
                "metrics": colony.metrics,
                "queue_size": colony.work_queue.qsize(),
            }

        return stats


# Example usage and helpers


async def simulate_image_upload(pipeline: ImageProcessingPipeline, num_images: int = 5):
    """Simulate uploading multiple images"""
    correlation_ids = []

    # Create dummy image paths
    for i in range(num_images):
        image_path = f"/tmp/test_image_{i}.jpg"

        # Create a dummy file if imaging not available
        if not IMAGING_AVAILABLE:
            Path(image_path).touch()
        else:
            # Create actual test image
            img = Image.new("RGB", (800, 600), color=(i * 50 % 255, 100, 200))
            img.save(image_path)

        # Process image
        correlation_id = await pipeline.process_image(image_path, metadata={"source": "test", "batch": i // 2})
        correlation_ids.append(correlation_id)

        # Small delay between uploads
        await asyncio.sleep(0.1)

    return correlation_ids