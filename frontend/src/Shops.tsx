import { getUserId } from "./auth"
import { useEffect, useRef, useState } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import markerIcon from "leaflet/dist/images/marker-icon.png"
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png"
import markerShadow from "leaflet/dist/images/marker-shadow.png"

import { API_URL } from "./config"
L.Marker.prototype.options.icon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

type Shop = {
  address_id: string
  shop_name: string
  shop_address: string
  supermarket: string
  distance: number | null
  latitude: number
  longitude: number
}

type DistanceOption = "all" | "1" | "3" | "5" | "10" | "25" | "50" | "100"
type SupermarketOption = "all" | "morrisons" | "tesco" | "sainsburys"

const DISTANCE_OPTIONS: { value: DistanceOption; label: string }[] = [
  { value: "all", label: "All" },
  { value: "1", label: "1 mile" },
  { value: "3", label: "3 miles" },
  { value: "5", label: "5 miles" },
  { value: "10", label: "10 miles" },
  { value: "25", label: "25 miles" },
  { value: "50", label: "50 miles" },
  { value: "100", label: "100 miles" },
]

const SUPERMARKET_OPTIONS: { value: SupermarketOption; label: string }[] = [
  { value: "all", label: "All" },
  { value: "morrisons", label: "Morrisons" },
  { value: "tesco", label: "Tesco" },
  { value: "sainsburys", label: "Sainsbury's" },
]

function kmToMiles(km: number | null): number | null {
  if (km === null) return null
  return km * 0.621371
}

function Shops() {
  const [shops, setShops] = useState<Shop[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [distanceFilter, setDistanceFilter] = useState<DistanceOption>("all")
  const [supermarketFilter, setSupermarketFilter] = useState<SupermarketOption>("all")
  const [selectedShop, setSelectedShop] = useState<Shop | null>(null)
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<L.Map | null>(null)
  const markerLayer = useRef<L.LayerGroup | null>(null)

  useEffect(() => {
    const fetchShops = async () => {
      setLoading(true)
      try {
        const response = await fetch(`${API_URL}/api/shops?user_id=${getUserId()}`)
        if (!response.ok) {
          const data = await response.json()
          setError(data.detail || "Could not load shops.")
          setShops([])
        } else {
          const data = await response.json()
          setShops(data)
          setError("")
        }
      } catch {
        setError("Could not load shops.")
        setShops([])
      }
      setLoading(false)
    }

    fetchShops()
  }, [])

  const filteredShops = shops.filter((shop) => {
    const distanceMax = distanceFilter === "all" ? Infinity : parseFloat(distanceFilter)
    const miles = kmToMiles(shop.distance)

    if (miles !== null && miles > distanceMax) {
      return false
    }

    if (supermarketFilter !== "all" && shop.supermarket.toLowerCase() !== supermarketFilter) {
      return false
    }

    return true
  })

  useEffect(() => {
    if (!selectedShop || !mapContainer.current) return
    const pos: L.LatLngExpression = [selectedShop.latitude, selectedShop.longitude]

    try {
      if (!map.current) {
        map.current = L.map(mapContainer.current).setView(pos, 15)
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
          maxZoom: 19,
        }).addTo(map.current)
        markerLayer.current = L.layerGroup().addTo(map.current)
      } else {
        map.current.setView(pos, 15)
      }

      markerLayer.current?.clearLayers()
      const popup = document.createElement("strong")
      popup.textContent = selectedShop.shop_name
      L.marker(pos).addTo(markerLayer.current!).bindPopup(popup).openPopup()
      map.current.invalidateSize()
    } catch (err) {
      console.error("Map failed to render", err)
      setError("Could not display the map.")
    }
    mapContainer.current.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }, [selectedShop])

  useEffect(() => {
    if (selectedShop) return
    map.current?.remove()
    map.current = null
    markerLayer.current = null
  }, [selectedShop])

  const openMap = (shop: Shop) => setSelectedShop(shop)
  const closeMap = () => setSelectedShop(null)

  if (loading) {
    return <p className="muted">Loading nearby shops...</p>
  }

  if (error) {
    return <p className="error-message">{error}</p>
  }

  if (shops.length === 0) {
    return <p className="muted">No shops found nearby.</p>
  }

  const getEmptyMessage = () => {
    const hasDistanceFilter = distanceFilter !== "all"
    const hasSupermarketFilter = supermarketFilter !== "all"

    if (hasDistanceFilter && hasSupermarketFilter) {
      const supermarketName = SUPERMARKET_OPTIONS.find(
        (opt) => opt.value === supermarketFilter
      )?.label
      return `No ${supermarketName} supermarkets found within ${distanceFilter} miles.`
    }

    if (hasSupermarketFilter) {
      const supermarketName = SUPERMARKET_OPTIONS.find(
        (opt) => opt.value === supermarketFilter
      )?.label
      return `No ${supermarketName} supermarkets found.`
    }

    if (hasDistanceFilter) {
      return `No supermarkets found within ${distanceFilter} miles.`
    }

    return "No supermarkets found nearby."
  }

  return (
    <>
      <div className="panel shopping-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">STORES</p>
            <h3>Nearby shops</h3>
          </div>
        </div>

        <div className="shops-filters">
          <label className="filter-field">
            <span className="filter-label">Maximum distance</span>
            <select
              value={distanceFilter}
              onChange={(e) => setDistanceFilter(e.target.value as DistanceOption)}
              className="filter-select"
            >
              {DISTANCE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          <label className="filter-field">
            <span className="filter-label">Supermarket</span>
            <select
              value={supermarketFilter}
              onChange={(e) => setSupermarketFilter(e.target.value as SupermarketOption)}
              className="filter-select"
            >
              {SUPERMARKET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className={selectedShop ? "shops-body with-map" : "shops-body"}>
        {filteredShops.length === 0 ? (
          <p className="muted shops-empty">{getEmptyMessage()}</p>
        ) : (
          <ul className="shop-list">
            {filteredShops.map((shop) => {
              const miles = kmToMiles(shop.distance)
              const active =
                selectedShop?.address_id === shop.address_id &&
                selectedShop?.supermarket === shop.supermarket
              return (
                <li
                  key={`${shop.supermarket}-${shop.address_id}`}
                  className={active ? "shop-item active" : "shop-item"}
                >
                  <div className="shop-info">
                    <strong className="shop-name">{shop.shop_name}</strong>
                    <span className="shop-provider">{shop.supermarket.toUpperCase()}</span>
                    <span className="shop-address">{shop.shop_address}</span>
                  </div>
                  <span className="shop-distance">
                    {miles !== null ? `${miles.toFixed(1)} mi` : "Distance unknown"}
                  </span>
                  <button className="shop-map-button" onClick={() => openMap(shop)}>
                    Show on Map
                  </button>
                </li>
              )
            })}
          </ul>
        )}

        {selectedShop && (
          <div className="shops-map-panel">
            <div className="shops-map-header">
              <h4>{selectedShop.shop_name}</h4>
              <button className="shop-map-button" onClick={closeMap}>
                Close Map
              </button>
            </div>
            <div className="map-container" ref={mapContainer}></div>
          </div>
        )}
        </div>
      </div>
    </>
  )
}

export default Shops
