const NODE_TYPE_LAYOUT_ORDER = {
  SeaArea: 0,
  Buoy: 1,
  Observation: 2,
  CurrentField: 2,
  RiskFactor: 3,
  RedTideEvent: 4,
  Species: 5,
  FisheryArea: 5,
  Route: 6,
  PreventionMeasure: 7,
  Agent: 8,
  Report: 9,
}

const LAYOUT = {
  ringGap: 165,
  firstRingRadius: 150,
  componentGap: 260,
  collisionGap: 42,
  collisionCellSize: 130,
  edgeNodeGap: 28,
  edgeEdgeGap: 38,
  idealEdgeLength: 185,
  forceIterations: 72,
  forceMaxMove: 18,
  forceRepulsionRadius: 360,
  coreClusterRadius: 150,
  anchorStrength: 0.075,
}

export function repelFromNode(cy, dragged) {
  if (!cy) return
  const pd = dragged.position()
  const rd = Math.max(dragged.width(), dragged.height()) / 2 + 18

  cy.nodes().forEach((other) => {
    if (other.id() === dragged.id()) return
    const po = other.position()
    let dx = po.x - pd.x
    let dy = po.y - pd.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const ro = Math.max(other.width(), other.height()) / 2 + 18
    const minDist = rd + ro

    if (dist < minDist) {
      const push = minDist - dist + 2
      const nx = dx / dist
      const ny = dy / dist
      other.position({ x: po.x + nx * push, y: po.y + ny * push })
    }
  })
}

function nodeTypeRank(node) {
  return NODE_TYPE_LAYOUT_ORDER[node.data('nodeType')] ?? 99
}

function stableHash(text) {
  let hash = 2166136261
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function stableAngle(id) {
  return (stableHash(id) / 0xffffffff) * Math.PI * 2
}

function sortNodesForLayout(nodes, degreeById) {
  return [...nodes].sort((a, b) => {
    const rankDiff = nodeTypeRank(a) - nodeTypeRank(b)
    if (rankDiff !== 0) return rankDiff
    const degreeDiff = (degreeById.get(b.id()) || 0) - (degreeById.get(a.id()) || 0)
    if (degreeDiff !== 0) return degreeDiff
    return a.data('label').localeCompare(b.data('label'), 'zh-Hans') || a.id().localeCompare(b.id())
  })
}

function buildTopology(cy) {
  const nodes = cy.nodes().toArray()
  const nodeById = new Map(nodes.map((node) => [node.id(), node]))
  const adjacency = new Map(nodes.map((node) => [node.id(), new Set()]))
  const degreeById = new Map(nodes.map((node) => [node.id(), 0]))

  cy.edges().forEach((edge) => {
    const source = edge.data('source')
    const target = edge.data('target')
    if (!nodeById.has(source) || !nodeById.has(target)) return
    adjacency.get(source).add(target)
    adjacency.get(target).add(source)
    degreeById.set(source, (degreeById.get(source) || 0) + 1)
    degreeById.set(target, (degreeById.get(target) || 0) + 1)
  })

  return { nodes, nodeById, adjacency, degreeById }
}

function connectedComponents(topology) {
  const visited = new Set()
  const components = []

  for (const node of topology.nodes) {
    if (visited.has(node.id())) continue
    const queue = [node.id()]
    const ids = []
    visited.add(node.id())

    while (queue.length > 0) {
      const id = queue.shift()
      ids.push(id)
      for (const nextId of topology.adjacency.get(id) || []) {
        if (visited.has(nextId)) continue
        visited.add(nextId)
        queue.push(nextId)
      }
    }

    components.push(ids.map((id) => topology.nodeById.get(id)).filter(Boolean))
  }

  return components.sort((a, b) => {
    const coreDiff = Number(b.some((node) => node.data('isCore'))) - Number(a.some((node) => node.data('isCore')))
    if (coreDiff !== 0) return coreDiff
    return b.length - a.length
  })
}

function chooseComponentRoot(component, topology, focusNodeId = null) {
  const focused = focusNodeId ? component.find((node) => node.id() === focusNodeId) : null
  if (focused) return focused

  const ordered = sortNodesForLayout(component, topology.degreeById)
  return ordered[0]
}

function buildComponentPositions(component, topology, root) {
  const cores = componentCoreNodes(component, topology, root)
  const coreAngles = new Map()
  const positions = new Map()
  const coreRadius = cores.length <= 1 ? 0 : Math.max(LAYOUT.coreClusterRadius, cores.length * 58)
  let layoutRadius = Math.max(coreRadius, 110)

  cores.forEach((node, index) => {
    const angle = cores.length <= 1 ? -Math.PI / 2 : -Math.PI / 2 + (Math.PI * 2 * index) / cores.length
    coreAngles.set(node.id(), angle)
    positions.set(node.id(), {
      x: Math.cos(angle) * coreRadius,
      y: Math.sin(angle) * coreRadius,
    })
  })

  const assignments = assignNodesToCores(component, cores, topology)
  const sectorWidth = cores.length <= 1 ? Math.PI * 2 : (Math.PI * 2 / cores.length) * 0.72

  cores.forEach((core) => {
    const assigned = assignments.get(core.id()) || new Map()
    const coreAngle = coreAngles.get(core.id()) ?? -Math.PI / 2

    for (const depth of [...assigned.keys()].sort((a, b) => a - b)) {
      const depthNodes = sortNodesForLayout(assigned.get(depth), topology.degreeById)
      const count = depthNodes.length
      const ringRadius = coreRadius + LAYOUT.firstRingRadius + (depth - 1) * LAYOUT.ringGap + Math.max(0, count - 6) * 12
      const usableWidth = Math.min(sectorWidth, Math.max(0.95, count * 0.34))
      const angleStart = coreAngle - usableWidth / 2
      layoutRadius = Math.max(layoutRadius, ringRadius)

      depthNodes.forEach((node, index) => {
        const angle = count === 1
          ? coreAngle
          : angleStart + (usableWidth * index) / (count - 1)
        const jitter = (stableAngle(`${core.id()}:${node.id()}`) - Math.PI) * 0.045
        positions.set(node.id(), {
          x: Math.cos(angle + jitter) * ringRadius,
          y: Math.sin(angle + jitter) * ringRadius,
        })
      })
    }
  })

  return { positions, radius: Math.max(layoutRadius, 110) }
}

function componentCoreNodes(component, topology, fallbackRoot) {
  const explicitCores = component.filter((node) => node.data('isCore'))
  const cores = explicitCores.length > 0 ? explicitCores : [fallbackRoot]
  return sortNodesForLayout(cores, topology.degreeById)
}

function assignNodesToCores(component, cores, topology) {
  const componentIds = new Set(component.map((node) => node.id()))
  const coreIds = new Set(cores.map((node) => node.id()))
  const ownerById = new Map()
  const queue = []

  cores.forEach((core) => {
    ownerById.set(core.id(), { coreId: core.id(), depth: 0 })
    queue.push(core.id())
  })

  while (queue.length > 0) {
    const id = queue.shift()
    const current = ownerById.get(id)
    const nextIds = [...(topology.adjacency.get(id) || [])].sort()

    for (const nextId of nextIds) {
      if (!componentIds.has(nextId) || ownerById.has(nextId)) continue
      ownerById.set(nextId, { coreId: current.coreId, depth: current.depth + 1 })
      queue.push(nextId)
    }
  }

  const assignments = new Map(cores.map((core) => [core.id(), new Map()]))
  for (const node of component) {
    if (coreIds.has(node.id())) continue
    const owner = ownerById.get(node.id()) || { coreId: cores[0].id(), depth: 1 }
    const depth = Math.max(1, owner.depth)
    const byDepth = assignments.get(owner.coreId)
    if (!byDepth.has(depth)) byDepth.set(depth, [])
    byDepth.get(depth).push(node)
  }

  return assignments
}

function packComponents(componentLayouts) {
  const positions = new Map()
  const totalRadius = componentLayouts.reduce((sum, layout) => sum + layout.radius, 0)
  const rowLimit = Math.max(900, Math.sqrt(Math.max(1, totalRadius)) * 180)
  let cursorX = 0
  let cursorY = 0
  let rowHeight = 0

  for (const layout of componentLayouts) {
    const size = layout.radius * 2 + LAYOUT.componentGap
    if (cursorX > 0 && cursorX + size > rowLimit) {
      cursorX = 0
      cursorY += rowHeight
      rowHeight = 0
    }

    const offsetX = cursorX + size / 2
    const offsetY = cursorY + size / 2
    for (const [id, pos] of layout.positions) {
      positions.set(id, { x: pos.x + offsetX, y: pos.y + offsetY })
    }

    cursorX += size
    rowHeight = Math.max(rowHeight, size)
  }

  const values = [...positions.values()]
  if (values.length === 0) return positions

  const minX = Math.min(...values.map((pos) => pos.x))
  const maxX = Math.max(...values.map((pos) => pos.x))
  const minY = Math.min(...values.map((pos) => pos.y))
  const maxY = Math.max(...values.map((pos) => pos.y))
  const centerX = (minX + maxX) / 2
  const centerY = (minY + maxY) / 2

  for (const [id, pos] of positions) {
    positions.set(id, { x: pos.x - centerX, y: pos.y - centerY })
  }

  return positions
}

function runPresetLayout(cy, positions, { animate = true, fit = false, focusNodeId = null } = {}) {
  const layout = cy.layout({
    name: 'preset',
    positions: (node) => positions.get(node.id()) || node.position(),
    fit: false,
    animate: animate && cy.nodes().length <= 120,
    animationDuration: 360,
    padding: 60,
  })

  layout.one('layoutstop', () => {
    resolveGraphConstraints(cy, { relax: true, anchorPositions: positions })
    if (fit) {
      setTimeout(() => focusGraph(cy, focusNodeId), 20)
    }
  })
  layout.run()
}

export function applyStableGraphLayout(cy, { animate = true, fit = false, focusNodeId = null } = {}) {
  if (!cy || cy.nodes().length === 0) return

  const topology = buildTopology(cy)
  const layouts = connectedComponents(topology).map((component) => {
    const root = chooseComponentRoot(component, topology, focusNodeId)
    return buildComponentPositions(component, topology, root)
  })

  runPresetLayout(cy, packComponents(layouts), { animate, fit, focusNodeId })
}

function findLargestAngleGap(angles) {
  if (angles.length === 0) return { start: -Math.PI / 2, size: Math.PI * 2 }
  const sorted = [...angles].sort((a, b) => a - b)
  let bestStart = sorted[sorted.length - 1]
  let bestGap = sorted[0] + Math.PI * 2 - sorted[sorted.length - 1]

  for (let i = 0; i < sorted.length - 1; i++) {
    const gap = sorted[i + 1] - sorted[i]
    if (gap > bestGap) {
      bestGap = gap
      bestStart = sorted[i]
    }
  }

  return { start: bestStart, size: bestGap }
}

export function placeNewNodesAround(cy, centerNodeId, newNodeIds, { animate = true } = {}) {
  if (!cy || !centerNodeId || newNodeIds.length === 0) return false

  const center = cy.getElementById(centerNodeId)
  if (!center.length) return false

  const newIdSet = new Set(newNodeIds)
  const newNodes = sortNodesForLayout(
    newNodeIds.map((id) => cy.getElementById(id)).filter((node) => node.length),
    buildTopology(cy).degreeById,
  )
  if (newNodes.length === 0) return false

  const centerPos = center.position()
  const occupiedAngles = []
  center.connectedEdges().connectedNodes().forEach((node) => {
    if (node.id() === centerNodeId || newIdSet.has(node.id())) return
    const pos = node.position()
    occupiedAngles.push(Math.atan2(pos.y - centerPos.y, pos.x - centerPos.x))
  })

  const gap = findLargestAngleGap(occupiedAngles)
  const perRing = 10
  const step = Math.min(0.78, gap.size / Math.max(newNodes.length + 1, 2))
  const baseAngle = gap.start + gap.size / 2 - ((Math.min(newNodes.length, perRing) - 1) * step) / 2

  cy.batch(() => {
    newNodes.forEach((node, index) => {
      const ring = Math.floor(index / perRing)
      const indexInRing = index % perRing
      const ringCount = Math.min(perRing, newNodes.length - ring * perRing)
      const angle = baseAngle + (indexInRing - (ringCount - 1) / 2) * step + ring * 0.28
      const radius = LAYOUT.firstRingRadius + ring * 105 + Math.max(0, ringCount - 6) * 8
      node.position({
        x: centerPos.x + Math.cos(angle) * radius,
        y: centerPos.y + Math.sin(angle) * radius,
      })
    })
  })

  const anchorPositions = new Map(newNodes.map((node) => [node.id(), { ...node.position() }]))
  resolveGraphConstraints(cy, {
    relax: true,
    relaxIterations: 34,
    movableIds: newIdSet,
    anchorPositions,
  })
  if (animate) {
    const focus = center.closedNeighborhood().union(cy.collection(newNodes))
    cy.fit(focus, 80)
  }

  return true
}

export function resolveGraphConstraints(
  cy,
  { relax = false, relaxIterations = LAYOUT.forceIterations, movableIds = null, anchorPositions = null } = {},
) {
  if (!cy) return

  if (relax) {
    relaxStraightForces(cy, { iterations: relaxIterations, movableIds, anchorPositions })
  }

  for (let round = 0; round < 4; round++) {
    const nodeMoved = resolveSpatialCollisions(cy)
    const edgeMoved = resolveEdgeNodeOverlaps(cy)
    if (!nodeMoved && !edgeMoved) break
  }

  resolveSpatialCollisions(cy)
  resolveStraightEdgeOverlaps(cy)
  resolveEdgeNodeOverlaps(cy)
}

function canMoveNode(node, movableIds) {
  return !movableIds || movableIds.has(node.id())
}

function addForce(forces, nodeId, x, y) {
  const force = forces.get(nodeId)
  if (!force) return
  force.x += x
  force.y += y
}

function clampMove(value) {
  return Math.max(-LAYOUT.forceMaxMove, Math.min(LAYOUT.forceMaxMove, value))
}

function idealLengthForEdge(edge) {
  const source = edge.source()
  const target = edge.target()
  const sourceIsCore = source.data('isCore')
  const targetIsCore = target.data('isCore')
  if (sourceIsCore && targetIsCore) return LAYOUT.coreClusterRadius * 1.25
  if (sourceIsCore || targetIsCore) return LAYOUT.idealEdgeLength
  return LAYOUT.idealEdgeLength + 35
}

function relaxStraightForces(cy, { iterations, movableIds = null, anchorPositions = null }) {
  const nodes = cy.nodes().toArray()
  const edges = cy.edges().toArray()
  if (nodes.length < 2) return

  const movableNodes = nodes.filter((node) => canMoveNode(node, movableIds))
  if (movableNodes.length === 0) return

  for (let iter = 0; iter < iterations; iter++) {
    const cooling = 1 - iter / iterations
    const forces = new Map(nodes.map((node) => [node.id(), { x: 0, y: 0 }]))

    applyNodeRepulsion(nodes, forces, movableIds)
    applyEdgeSprings(edges, forces, movableIds)
    applyNodeEdgeForces(nodes, edges, forces, movableIds)
    applyComponentGravity(nodes, forces, movableIds)
    applyAnchorForces(nodes, forces, movableIds, anchorPositions)

    cy.batch(() => {
      for (const node of movableNodes) {
        const force = forces.get(node.id())
        if (!force) continue
        const pos = node.position()
        node.position({
          x: pos.x + clampMove(force.x * 0.12 * cooling),
          y: pos.y + clampMove(force.y * 0.12 * cooling),
        })
      }
    })

    if (iter % 12 === 11) {
      resolveSpatialCollisions(cy)
    }
  }
}

function applyNodeRepulsion(nodes, forces, movableIds) {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i]
      const b = nodes[j]
      const pa = a.position()
      const pb = b.position()
      let dx = pa.x - pb.x
      let dy = pa.y - pb.y
      let dist = Math.hypot(dx, dy)
      if (dist > LAYOUT.forceRepulsionRadius) continue

      if (dist < 1) {
        const angle = stableAngle(`${a.id()}:${b.id()}:repel`)
        dx = Math.cos(angle)
        dy = Math.sin(angle)
        dist = 1
      }

      const minDist = nodeClearanceRadius(a, 28) + nodeClearanceRadius(b, 28)
      const strength = dist < minDist
        ? (minDist - dist + 24) * 1.7
        : ((LAYOUT.forceRepulsionRadius - dist) / LAYOUT.forceRepulsionRadius) * 10
      const nx = dx / dist
      const ny = dy / dist

      if (canMoveNode(a, movableIds)) addForce(forces, a.id(), nx * strength, ny * strength)
      if (canMoveNode(b, movableIds)) addForce(forces, b.id(), -nx * strength, -ny * strength)
    }
  }
}

function applyEdgeSprings(edges, forces, movableIds) {
  for (const edge of edges) {
    const endpoints = edgeEndpoints(edge)
    if (!endpoints) continue

    const dx = endpoints.end.x - endpoints.start.x
    const dy = endpoints.end.y - endpoints.start.y
    const dist = Math.hypot(dx, dy) || 1
    const target = idealLengthForEdge(edge)
    const pull = (dist - target) * 0.11
    const nx = dx / dist
    const ny = dy / dist

    if (canMoveNode(endpoints.source, movableIds)) addForce(forces, endpoints.source.id(), nx * pull, ny * pull)
    if (canMoveNode(endpoints.target, movableIds)) addForce(forces, endpoints.target.id(), -nx * pull, -ny * pull)
  }
}

function applyNodeEdgeForces(nodes, edges, forces, movableIds) {
  for (const edge of edges) {
    const endpoints = edgeEndpoints(edge)
    if (!endpoints) continue

    const dx = endpoints.end.x - endpoints.start.x
    const dy = endpoints.end.y - endpoints.start.y
    const length = Math.hypot(dx, dy) || 1
    const nx = -dy / length
    const ny = dx / length

    for (const node of nodes) {
      if (node.id() === endpoints.source.id() || node.id() === endpoints.target.id()) continue

      const pos = node.position()
      const hit = pointSegmentDistance(pos, endpoints.start, endpoints.end)
      if (hit.t <= 0.08 || hit.t >= 0.92) continue

      const radius = nodeClearanceRadius(node, LAYOUT.edgeNodeGap + 18)
      if (hit.distance >= radius) continue

      const side = (pos.x - endpoints.start.x) * nx + (pos.y - endpoints.start.y) * ny
      const direction = side >= 0 ? 1 : -1
      const strength = (radius - hit.distance + 18) * 1.35

      if (canMoveNode(node, movableIds)) {
        addForce(forces, node.id(), nx * direction * strength, ny * direction * strength)
      } else {
        const endpointForce = strength * 0.38
        if (canMoveNode(endpoints.source, movableIds)) addForce(forces, endpoints.source.id(), -nx * direction * endpointForce, -ny * direction * endpointForce)
        if (canMoveNode(endpoints.target, movableIds)) addForce(forces, endpoints.target.id(), -nx * direction * endpointForce, -ny * direction * endpointForce)
      }
    }
  }
}

function applyComponentGravity(nodes, forces, movableIds) {
  let centerX = 0
  let centerY = 0
  for (const node of nodes) {
    const pos = node.position()
    centerX += pos.x
    centerY += pos.y
  }
  centerX /= nodes.length
  centerY /= nodes.length

  for (const node of nodes) {
    if (!canMoveNode(node, movableIds)) continue
    const pos = node.position()
    addForce(forces, node.id(), (centerX - pos.x) * 0.015, (centerY - pos.y) * 0.015)
  }
}

function applyAnchorForces(nodes, forces, movableIds, anchorPositions) {
  if (!anchorPositions) return

  for (const node of nodes) {
    if (!canMoveNode(node, movableIds)) continue
    const anchor = anchorPositions.get(node.id())
    if (!anchor) continue

    const pos = node.position()
    addForce(
      forces,
      node.id(),
      (anchor.x - pos.x) * LAYOUT.anchorStrength,
      (anchor.y - pos.y) * LAYOUT.anchorStrength,
    )
  }
}

function resolveSpatialCollisions(cy) {
  if (!cy) return
  const nodes = cy.nodes().toArray()
  if (nodes.length < 2) return false

  const radiusOf = (node) => Math.max(node.width(), node.height()) / 2 + LAYOUT.collisionGap
  const cellSize = LAYOUT.collisionCellSize
  const cellKey = (x, y) => `${Math.floor(x / cellSize)}:${Math.floor(y / cellSize)}`
  let anyMoved = false

  for (let round = 0; round < 8; round++) {
    const grid = new Map()
    let moved = false

    for (const node of nodes) {
      const pos = node.position()
      const cx = Math.floor(pos.x / cellSize)
      const cyIndex = Math.floor(pos.y / cellSize)

      for (let gx = cx - 1; gx <= cx + 1; gx++) {
        for (let gy = cyIndex - 1; gy <= cyIndex + 1; gy++) {
          const occupants = grid.get(`${gx}:${gy}`) || []
          for (const other of occupants) {
            const otherPos = other.position()
            let dx = pos.x - otherPos.x
            let dy = pos.y - otherPos.y
            let dist = Math.sqrt(dx * dx + dy * dy)
            const minDist = radiusOf(node) + radiusOf(other)
            if (dist >= minDist) continue

            if (dist < 1) {
              const angle = stableAngle(`${node.id()}:${other.id()}`)
              dx = Math.cos(angle)
              dy = Math.sin(angle)
              dist = 1
            }

            const push = (minDist - dist) / 2 + 2
            const nx = dx / dist
            const ny = dy / dist
            node.position({ x: pos.x + nx * push, y: pos.y + ny * push })
            other.position({ x: otherPos.x - nx * push, y: otherPos.y - ny * push })
            moved = true
            anyMoved = true
          }
        }
      }

      const nextPos = node.position()
      const key = cellKey(nextPos.x, nextPos.y)
      if (!grid.has(key)) grid.set(key, [])
      grid.get(key).push(node)
    }

    if (!moved) break
  }

  return anyMoved
}

function nodeClearanceRadius(node, extra = 0) {
  return Math.max(node.width(), node.height()) / 2 + extra
}

function pointSegmentDistance(point, start, end) {
  const dx = end.x - start.x
  const dy = end.y - start.y
  const lengthSq = dx * dx + dy * dy
  if (lengthSq === 0) {
    return {
      distance: Math.hypot(point.x - start.x, point.y - start.y),
      t: 0,
      closest: start,
    }
  }

  const rawT = ((point.x - start.x) * dx + (point.y - start.y) * dy) / lengthSq
  const t = Math.max(0, Math.min(1, rawT))
  const closest = { x: start.x + dx * t, y: start.y + dy * t }
  return {
    distance: Math.hypot(point.x - closest.x, point.y - closest.y),
    t,
    closest,
  }
}

function edgeEndpoints(edge) {
  const source = edge.source()
  const target = edge.target()
  if (!source.length || !target.length) return null
  return {
    source,
    target,
    start: source.position(),
    end: target.position(),
  }
}

function resolveEdgeNodeOverlaps(cy) {
  const nodes = cy.nodes().toArray()
  const edges = cy.edges().toArray()
  let anyMoved = false

  for (let round = 0; round < 8; round++) {
    let moved = false

    for (const edge of edges) {
      const endpoints = edgeEndpoints(edge)
      if (!endpoints) continue

      const dx = endpoints.end.x - endpoints.start.x
      const dy = endpoints.end.y - endpoints.start.y
      const length = Math.hypot(dx, dy) || 1
      const nx = -dy / length
      const ny = dx / length

      for (const node of nodes) {
        if (node.id() === endpoints.source.id() || node.id() === endpoints.target.id()) continue

        const pos = node.position()
        const hit = pointSegmentDistance(pos, endpoints.start, endpoints.end)
        if (hit.t <= 0.08 || hit.t >= 0.92) continue

        const radius = nodeClearanceRadius(node, LAYOUT.edgeNodeGap)
        if (hit.distance >= radius) continue

        const side = (pos.x - endpoints.start.x) * nx + (pos.y - endpoints.start.y) * ny
        const direction = side >= 0 ? 1 : -1
        const push = radius - hit.distance + 12

        node.position({
          x: pos.x + nx * direction * push,
          y: pos.y + ny * direction * push,
        })
        moved = true
        anyMoved = true
      }
    }

    if (!moved) break
    resolveSpatialCollisions(cy)
  }

  return anyMoved
}

function segmentOverlapAmount(a, b) {
  const aEnd = edgeEndpoints(a)
  const bEnd = edgeEndpoints(b)
  if (!aEnd || !bEnd) return 0

  const ax = aEnd.end.x - aEnd.start.x
  const ay = aEnd.end.y - aEnd.start.y
  const bx = bEnd.end.x - bEnd.start.x
  const by = bEnd.end.y - bEnd.start.y
  const aLen = Math.hypot(ax, ay)
  const bLen = Math.hypot(bx, by)
  if (aLen < 1 || bLen < 1) return 0

  const cross = Math.abs(ax * by - ay * bx) / (aLen * bLen)
  if (cross > 0.035) return 0

  const nx = -ay / aLen
  const ny = ax / aLen
  const bStartOffset = Math.abs((bEnd.start.x - aEnd.start.x) * nx + (bEnd.start.y - aEnd.start.y) * ny)
  const bEndOffset = Math.abs((bEnd.end.x - aEnd.start.x) * nx + (bEnd.end.y - aEnd.start.y) * ny)
  if (Math.max(bStartOffset, bEndOffset) > 16) return 0

  const ux = ax / aLen
  const uy = ay / aLen
  const b0 = (bEnd.start.x - aEnd.start.x) * ux + (bEnd.start.y - aEnd.start.y) * uy
  const b1 = (bEnd.end.x - aEnd.start.x) * ux + (bEnd.end.y - aEnd.start.y) * uy
  const overlapStart = Math.max(0, Math.min(b0, b1))
  const overlapEnd = Math.min(aLen, Math.max(b0, b1))
  return Math.max(0, overlapEnd - overlapStart)
}

function moveEdgeEndpointAway(edge, referenceEdge, amount) {
  const endpoints = edgeEndpoints(edge)
  const reference = edgeEndpoints(referenceEdge)
  if (!endpoints || !reference) return false

  const dx = reference.end.x - reference.start.x
  const dy = reference.end.y - reference.start.y
  const len = Math.hypot(dx, dy) || 1
  const sideSeed = stableHash(edge.id()) % 2 === 0 ? 1 : -1
  const nx = (-dy / len) * sideSeed
  const ny = (dx / len) * sideSeed
  const sourceDegree = endpoints.source.connectedEdges().length
  const targetDegree = endpoints.target.connectedEdges().length
  const node = sourceDegree <= targetDegree ? endpoints.source : endpoints.target
  const pos = node.position()

  node.position({
    x: pos.x + nx * amount,
    y: pos.y + ny * amount,
  })
  return true
}

function resolveStraightEdgeOverlaps(cy) {
  const edges = cy.edges().toArray()

  for (let round = 0; round < 4; round++) {
    let moved = false

    for (let i = 0; i < edges.length; i++) {
      for (let j = i + 1; j < edges.length; j++) {
        const overlap = segmentOverlapAmount(edges[i], edges[j])
        if (overlap < 36) continue

        const edgeToMove = edges[i].id().localeCompare(edges[j].id()) > 0 ? edges[i] : edges[j]
        const reference = edgeToMove === edges[i] ? edges[j] : edges[i]
        moved = moveEdgeEndpointAway(edgeToMove, reference, LAYOUT.edgeEdgeGap) || moved
      }
    }

    if (!moved) break
    resolveSpatialCollisions(cy)
  }
}

export function focusGraph(cy, focusNodeId = null) {
  if (!cy || cy.nodes().length === 0) return

  const focused = focusNodeId ? cy.getElementById(focusNodeId) : null
  const coreNode = cy.nodes().filter((n) => n.data('isCore')).first()
  const target = focused?.length ? focused : (coreNode.length > 0 ? coreNode : cy.nodes().first())
  if (!target || target.length === 0) return

  const neighborhood = target.neighborhood().add(target)
  if (neighborhood.length >= 3) {
    cy.fit(neighborhood, 60)
  } else {
    cy.fit(undefined, 40)
  }
}
