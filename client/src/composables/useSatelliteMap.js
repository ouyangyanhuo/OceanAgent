import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const SATELLITE_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

export function useSatelliteMap() {
  const addSatelliteBaseLayer = (mapInstance) => {
    return L.tileLayer(SATELLITE_TILE_URL, { maxZoom: 18 }).addTo(mapInstance)
  }

  return { L, addSatelliteBaseLayer }
}
