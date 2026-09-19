import { useState } from "react"



function App() {

  const [product, setProduct] = useState("")
  const [result, setResult] = useState<Product[]>([])

  type Product = {
    name: string,
    price: number
  }

  

  return (

    <div>
      <h1>Mealtrack</h1>
      
      <input 
      type="text" 
      placeholder="Search for a product..." 
      onChange={(e) => setProduct(e.target.value)}/>
      
      <button
      type="button"
      onClick={() => fetch(`http://localhost:8000/api/products?query=${product}`)
      .then(response => response.json())
      .then(data => setResult(data))}>Search</button>

    {result.map(item => (
          <div>
            <h3>{item.name}</h3>
            <p>{item.price} GBP</p>
          </div>
        ))}
    </div>
  )
}

export default App