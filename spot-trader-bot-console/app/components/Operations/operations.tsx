'use client'

import { useEffect, useState } from 'react'

interface Operation {
  id: string
}

export default function Operations() {
  const [operations, setOperations] = useState<Array<Operation>>([])
  useEffect(() => {
    const operations = fetch("http://127.0.0.1:8080/operations")
      .then(response => response.json())
      .then(data => setOperations(data.operations))
  }, []);

  if (operations.length > 0) {
    return (
      <ul>
        {operations.map(op => (<li key={op.id}>Operation #{op.id}</li>))}
      </ul>
    )
  } else {
    return (
      <p>No hay operaciones activas en el momento</p>
    )
  }
}
