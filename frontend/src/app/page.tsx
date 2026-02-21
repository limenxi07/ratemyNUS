'use client'

import { useState } from 'react'

const API_URL = "http://localhost:8000/"

export default function Home() {
  const [message, setMessage] = useState('')
  
  const testAPI = async () => {
    let data = await fetch(API_URL)
    let response = await data.json()
    setMessage(response.message)
  }

  // homepage HTML
  return (
    <div>
      <h1> ratemyNUS </h1>
      <p> Lorum ipsum </p>
      <button onClick={testAPI}> Test API </button>{message && <p>API Response: {message}</p>}
    </div>
  );
}
