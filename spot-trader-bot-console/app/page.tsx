import Operations from './components/Operations/operations'

export default function Home() {
  return (
    <main>
      <h1>Crear operaci&oacute;n</h1>
      <label htmlFor="moneda">Moneda</label>
      <select id="moneda" name="moneda">
        <option selected>Escoja una moneda</option>
        <option>BTCUSDT</option>
      </select>
      <label htmlFor="precios">Precios</label>
      <p>
      <input name="precio" type="number"></input>
      </p>
      <p>
      <input name="precio" type="number"></input>
      </p>
      <p>
      <input name="precio" type="number"></input>
      </p>
      <label htmlFor="Cantidad">Inversi&oacute;n por zona</label>
      <p>
      <input name="precio" type="number"></input>
      </p>
      <p>
        <button>Crear operaci&oacute;n</button>
      </p>
      <h1>Available Operations</h1>
      <Operations/>
    </main>
  )
}
