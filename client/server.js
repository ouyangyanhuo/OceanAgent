import { join, normalize, sep } from 'node:path'

const host = process.env.HOST || '0.0.0.0'
const port = Number.parseInt(process.env.PORT || '5173', 10)
const apiTarget = new URL(process.env.API_TARGET || 'http://backend:8000')
const distDirectory = join(import.meta.dir, 'dist')

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error(`Invalid PORT: ${process.env.PORT}`)
}

function isBackendRequest(pathname) {
  return pathname === '/api'
    || pathname.startsWith('/api/')
    || pathname === '/health'
}

async function proxyToBackend(request, requestUrl, server) {
  // The QA endpoint returns SSE and may remain idle while waiting for the LLM.
  if (requestUrl.pathname.endsWith('/qa/stream')) {
    server.timeout(request, 0)
  } else {
    server.timeout(request, 120)
  }

  const targetUrl = new URL(
    `${requestUrl.pathname}${requestUrl.search}`,
    apiTarget,
  )
  const headers = new Headers(request.headers)
  const clientIp = server.requestIP(request)?.address

  headers.delete('host')
  headers.delete('content-length')
  headers.delete('connection')
  headers.delete('keep-alive')
  headers.delete('proxy-authenticate')
  headers.delete('proxy-authorization')
  headers.delete('te')
  headers.delete('trailer')
  headers.delete('transfer-encoding')
  headers.delete('upgrade')
  headers.set('x-forwarded-host', requestUrl.host)
  headers.set('x-forwarded-proto', requestUrl.protocol.slice(0, -1))

  if (clientIp) {
    const forwardedFor = headers.get('x-forwarded-for')
    headers.set(
      'x-forwarded-for',
      forwardedFor ? `${forwardedFor}, ${clientIp}` : clientIp,
    )
    headers.set('x-real-ip', clientIp)
  }

  const init = {
    method: request.method,
    headers,
    redirect: 'manual',
    signal: request.signal,
  }

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = request.body
  }

  try {
    return await fetch(targetUrl, init)
  } catch (error) {
    console.error(`Backend request failed: ${targetUrl}`, error)
    return Response.json(
      { detail: 'Backend service is unavailable' },
      { status: 502 },
    )
  }
}

function safeAssetPath(pathname) {
  let decodedPath

  try {
    decodedPath = decodeURIComponent(pathname)
  } catch {
    return null
  }

  const relativePath = decodedPath.replace(/^\/+/, '') || 'index.html'
  const normalizedPath = normalize(relativePath)

  if (
    normalizedPath === '..'
    || normalizedPath.startsWith(`..${sep}`)
    || normalizedPath.includes('\0')
  ) {
    return null
  }

  return {
    file: Bun.file(join(distDirectory, normalizedPath)),
    relativePath: normalizedPath,
  }
}

function fileResponse(file, cacheControl) {
  const headers = new Headers({ 'Cache-Control': cacheControl })

  if (file.type) {
    headers.set('Content-Type', file.type)
  }

  return new Response(file, { headers })
}

async function serveFrontend(request, requestUrl) {
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    return new Response('Method Not Allowed', {
      status: 405,
      headers: { Allow: 'GET, HEAD' },
    })
  }

  const asset = safeAssetPath(requestUrl.pathname)

  if (!asset) {
    return new Response('Bad Request', { status: 400 })
  }

  if (await asset.file.exists()) {
    const cacheControl = asset.relativePath.startsWith(`assets${sep}`)
      ? 'public, max-age=31536000, immutable'
      : 'no-cache'
    return fileResponse(asset.file, cacheControl)
  }

  // Keep direct navigation working if the router later changes to history mode.
  const indexFile = Bun.file(join(distDirectory, 'index.html'))
  return fileResponse(indexFile, 'no-cache')
}

const server = Bun.serve({
  hostname: host,
  port,
  async fetch(request, serverInstance) {
    const requestUrl = new URL(request.url)

    if (isBackendRequest(requestUrl.pathname)) {
      return proxyToBackend(request, requestUrl, serverInstance)
    }

    return serveFrontend(request, requestUrl)
  },
  error(error) {
    console.error('Frontend server error:', error)
    return new Response('Internal Server Error', { status: 500 })
  },
})

console.log(`Frontend listening on ${server.url}`)
console.log(`Proxying /api and /health to ${apiTarget}`)
