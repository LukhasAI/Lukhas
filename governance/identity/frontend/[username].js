// 📂 FILE: [username].js
// 🧠 PURPOSE: Render public-facing symbolic LucasID profile page

import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

export default function PublicProfile() {
  const router = useRouter()
  const { username } = router.query
  const [user, setUser] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (username) {
      fetch(`/api/users/${username}`)
        .then(res => {
          if (!res.ok) throw new Error('User not found')
          return res.json()
        })
        .then(data => setUser(data))
        .catch(err => setError(err.message))
    }
  }, [username])

  if (error) return <div style={{ padding: "2em", color: "red" }}>⚠️ {error}</div>
  if (!user) return <div style={{ padding: "2em" }}>🔄 Loading symbolic identity...</div>

  return (
    <div style={{ padding: "2em", fontFamily: "sans-serif" }}>
      <h1>🌌 LucasID Profile</h1>
      <p><strong>Username:</strong> {user.username}</p>
      <p><strong>LucasID Code:</strong> <code>{user.lukhas_id_code}</code></p>
      <p><strong>Entity Type:</strong> {user.entity_type}</p>
      <p><strong>Tier:</strong> {user.tier}</p>
      <p><strong>QRGLYMPH:</strong></p>
      <img src={user.qrglyph_url} alt="QRGLYMPH" width="220" height="220" />
      <p style={{ fontSize: "0.9em", color: "#777" }}>Joined: {new Date(user.joined).toLocaleDateString()}</p>
    </div>
  )
}
