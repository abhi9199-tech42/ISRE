"""Main ISRE pipeline orchestrator."""

import threading
import uuid
from typing import Any

from ..compression.multimodal import MultimodalProcessor
from ..config import PipelineConfig, get_config
from ..graph.builder import IntentGraphBuilder
from ..knowledge.engine import KnowledgeQueryEngine
from ..knowledge.gaps import KnowledgeGapDetector
from ..reasoning.generator import ReasoningPathGenerator
from ..reasoning.selection import CompetitiveSelector
from ..reconstruction.translator import MultiFormatTranslator
from ..utils.logging import get_logger
from ..utils.resources import ResourceMonitor

log = get_logger(__name__)

class ISREPipeline:
    """
    Main orchestrator for the ISRE system.
    Coordinates the flow through all five architectural layers.
    Requirement 6.1: Sequential processing through five layers.
    Requirement 6.4: Traceability and diagnostics.
    Thread-safe for concurrent request handling.
    """

    def __init__(self, memory_threshold_mb: float = 500.0, config: PipelineConfig | None = None):
        # Deep copy the config to avoid mutating the global singleton
        if config is not None:
            self.config = config.model_copy(deep=True)
        else:
            self.config = get_config().model_copy(deep=True)
        # Allow overriding memory threshold via parameter
        if memory_threshold_mb != 500.0:
            self.config.memory_threshold_mb = memory_threshold_mb

        self.compression = MultimodalProcessor()
        self.graph_builder = IntentGraphBuilder(conflict_config=self.config.conflict)
        self.reasoning_gen = ReasoningPathGenerator()
        self.selector = CompetitiveSelector(reasoning_config=self.config.reasoning)
        self.knowledge_engine = KnowledgeQueryEngine()
        self.gap_detector = KnowledgeGapDetector(self.knowledge_engine)
        self.translator = MultiFormatTranslator()
        self.resource_monitor = ResourceMonitor(self.config.memory_threshold_mb)

        self.trace_log: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def process(self, raw_input: Any, modality: str = "text", target_formats: list[str] | None = None) -> dict[str, Any]:
        """
        Executes the full pipeline process.
        """
        request_id = str(uuid.uuid4())
        log.debug("Processing request %s: modality=%s", request_id, modality)
        self._log(request_id, "start", {"input": raw_input, "modality": modality})

        # 0. Resource Check (Graceful Degradation - Requirement 7.5)
        if self.resource_monitor.is_resource_constrained():
            self._log(request_id, "degradation", {"reason": "high_memory_usage"})
            primitives = self.compression.process(raw_input, modality)
            return {
                "request_id": request_id,
                "outputs": {"text": f"SYSTEM BUSY (Degraded Mode). Concepts: {[p.concept for p in primitives]}"},
                "degraded": True
            }

        try:
            # 1. Semantic Compression
            primitives = self.compression.process(raw_input, modality)
            log.debug("Compressed %d primitives from input", len(primitives))
            self._log(request_id, "compression", {
                "primitives_count": len(primitives),
                "primitives": [p.model_dump() for p in primitives]
            })

            # 2. Intent Graph Construction
            graph = self.graph_builder.build_from_primitives(primitives)
            self._log(request_id, "graph_construction", {
                "nodes_count": len(graph.nodes),
                "edges_count": len(graph.edges),
                "conflicts": [n.id for n in graph.nodes.values() if n.conflict_markers]
            })

            # 3. Designed Reasoning (Generation + Selection with Oscillatory Dynamics)
            paths = self.reasoning_gen.generate_paths(graph)
            self._log(request_id, "reasoning_generation", {"paths_count": len(paths)})

            decision = self.selector.select(paths)

            self._log(request_id, "reasoning_selection", {
                "selected_path_id": decision.selected_path.id,
                "confidence": decision.confidence,
                "convergence_metadata": decision.convergence_metadata
            })

            # 4. World Knowledge Integration (Gap Detection)
            gaps = self.gap_detector.detect_gaps(decision)
            if gaps:
                self._log(request_id, "knowledge_gaps", {"gaps": gaps})

            # 5. Semantic Reconstruction
            outputs = self.translator.translate(decision, target_formats)
            self._log(request_id, "reconstruction", {"formats": list(outputs.keys())})

            final_result = {
                "request_id": request_id,
                "outputs": outputs,
                "knowledge_gaps": gaps,
                "decision_metadata": {
                    "justification": decision.justification,
                    "confidence": decision.confidence,
                    "convergence_metadata": decision.convergence_metadata
                }
            }

            self._log(request_id, "complete", {"success": True})
            return final_result

        except Exception as e:
            log.error("Request %s failed: %s", request_id, str(e))
            self._log(request_id, "error", {"message": str(e)})
            raise

    def _log(self, request_id: str, stage: str, data: dict[str, Any]):
        with self._lock:
            self.trace_log.append({
                "request_id": request_id,
                "stage": stage,
                "data": data,
                "resource_status": self.resource_monitor.get_status()
            })

    def get_trace(self, request_id: str) -> list[dict[str, Any]]:
        return [entry for entry in self.trace_log if entry["request_id"] == request_id]

    def clear(self):
        with self._lock:
            self.trace_log.clear()
