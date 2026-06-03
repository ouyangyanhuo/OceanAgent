/** 图谱 API 服务。 */

export async function fetchGraph() {
  try {
    const res = await fetch('/api/graph')
    if (!res.ok) throw new Error(`Graph request failed: ${res.status}`)
    const json = await res.json()
    return { ok: true, data: json.data ?? { nodes: [], edges: [] } }
  } catch (err) {
    return { ok: false, error: err.message || '无法连接到后端服务', data: { nodes: [], edges: [] } }
  }
}

export async function fetchNode(nodeId) {
  try {
    const res = await fetch(`/api/graph/nodes/${encodeURIComponent(nodeId)}`)
    if (!res.ok) throw new Error(`Node request failed: ${res.status}`)
    const json = await res.json()
    return json.data ?? null
  } catch {
    return null
  }
}

export async function fetchNeighbors(nodeId, depth = 1) {
  try {
    const res = await fetch(`/api/graph/nodes/${encodeURIComponent(nodeId)}/neighbors?depth=${depth}`)
    if (!res.ok) throw new Error(`Neighbors request failed: ${res.status}`)
    const json = await res.json()
    return json.data ?? { nodes: [], edges: [] }
  } catch {
    return { nodes: [], edges: [] }
  }
}

export async function fetchExpandOptions(nodeId) {
  try {
    const res = await fetch(`/api/graph/nodes/${encodeURIComponent(nodeId)}/expand-options`)
    if (!res.ok) throw new Error(`Expand options request failed: ${res.status}`)
    const json = await res.json()
    return json.data ?? { node_id: nodeId, options: [] }
  } catch {
    return { node_id: nodeId, options: [] }
  }
}

export async function expandNode(nodeId, expandType, forceRefresh = false) {
  try {
    const res = await fetch('/api/graph/expand', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: nodeId, expand_type: expandType, force_refresh: forceRefresh }),
    })
    if (!res.ok) throw new Error(`Expand request failed: ${res.status}`)
    const json = await res.json()
    return json.data ?? null
  } catch {
    return null
  }
}
