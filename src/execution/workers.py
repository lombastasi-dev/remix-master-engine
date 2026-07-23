import difflib
import logging
from typing import List, Optional
from uuid import UUID, uuid4
from src.models.schemas import BlueprintNode, ManuscriptChunk, RewriteUnit

logger = logging.getLogger("ExecutionWorkerEngine")

def generate_differential_patch(original_text: str, modified_text: str) -> str:
    """Computes a unified diff string between the original chunk and modified text."""
    orig_lines = original_text.splitlines(keepends=True)
    mod_lines = modified_text.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile="baseline_chunk.txt",
        tofile="remediated_chunk.txt",
        lineterm=""
    )
    return "".join(diff)

async def execute_rewrite_node_async(
    node: BlueprintNode,
    chunk: ManuscriptChunk,
    blueprint_id: Optional[UUID] = None,
    auto_sign_off: bool = False
) -> RewriteUnit:
    """
    Executes a single rewrite task derived from a BlueprintNode.
    Applies remediation guidelines to chunk content, generates diff patch data,
    and constructs a RewriteUnit.
    """
    # Baseline transformation stub (simulating worker AI revision)
    revised_text = chunk.raw_text_content
    if "passive" in revised_text.lower():
        revised_text = revised_text.replace("with passive voice", "actively reframed")
    
    patch_data = generate_differential_patch(chunk.raw_text_content, revised_text)
    
    resolved_blueprint_id = getattr(node, "blueprint_id", None) or blueprint_id or uuid4()
    
    unit = RewriteUnit(
        unit_id=uuid4(),
        blueprint_id=resolved_blueprint_id,
        node_id=node.node_id,
        source_chunk_id=chunk.chunk_id,
        current_approved_text=revised_text,
        differential_patch_data=patch_data,
        is_human_signed_off=auto_sign_off
    )
    
    logger.info(f"Executed node {node.node_id} -> RewriteUnit {unit.unit_id}")
    return unit

async def execute_blueprint_batch_async(
    nodes: List[BlueprintNode],
    chunks_map: dict[str, ManuscriptChunk],
    blueprint_id: Optional[UUID] = None,
    auto_sign_off: bool = False
) -> List[RewriteUnit]:
    """Executes a batch of BlueprintNodes in task graph order."""
    sorted_nodes = sorted(nodes, key=lambda n: n.chronological_execution_order)
    units = []
    
    for node in sorted_nodes:
        chunk = chunks_map.get(str(node.chunk_id))
        if chunk:
            unit = await execute_rewrite_node_async(
                node, 
                chunk, 
                blueprint_id=blueprint_id, 
                auto_sign_off=auto_sign_off
            )
            units.append(unit)
            
    return units
