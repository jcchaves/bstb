'use client';

import TickersTypeahead from "../components/TickersTypeahead/tickersTypeahead"
import Message from "../components/Message/message"
import { PriceProps } from "../types/core/price"
import Price from "../components/Price/price"
import { MouseEvent, useState } from "react"
import { v4 as uuidv4 } from 'uuid'

export default function Operations() {
    const [error, setError] = useState<string>("");
    const [isErrorVisible, setIsErrorVisible] = useState<boolean>(false);

    const [tickerStep, setTickerStep] = useState<number>(1);
    const [prices, setPrices] = useState<Array<PriceProps>>([
        { id: uuidv4(), value: 0 }, { id: uuidv4(), value: 0 }
    ]);

    function showError(error: string) {
        setError(error)
        setIsErrorVisible(true)
        setTimeout(() => {
            setError("")
            setIsErrorVisible(false)
        }, 3000)
    }

    function hideError() {
        //TODO: Cancel timeout too
        setError("")
        setIsErrorVisible(false)
    }

    function onPriceChange(idx: number, event: React.ChangeEvent<HTMLInputElement>): void {
        const newPrice = parseFloat(event.target.value)
        prices[idx].value = newPrice
    }

    function addPrice(event: MouseEvent): void {
        event.preventDefault();
        setPrices([...prices, { id: uuidv4(), value: 0 }])
    }

    function removePrice(idx: number, event: MouseEvent): void {
        event.preventDefault();
        if (prices.length > 2) {
            const length = prices.length
            const left = prices.slice(0, idx)
            const right = prices.slice(idx + 1, length)
            setPrices([...left, ...right])
        } else {
            showError("You need to define at least 2 prices.")
        }
    }

    function createOperation(event: MouseEvent): void {
        event.preventDefault();
        console.log(prices);
    }

    return (
        <div className="container">
            <h1>Create Operation</h1>
            <div className="bg-secondary bg-opacity-10 border border-secondary rounded p-2">
                <form className="row g-2">
                    <div className="row g-2">
                        <div className="col">
                            <label htmlFor="tickersOptions" className="col-form-label"><h2>Ticker</h2></label>
                            <TickersTypeahead />
                            <span id="symbolHelpInline" className="form-text">
                                e.g. BTCUSDT, SHIBUSDT, etc
                            </span>
                        </div>
                        <div className="col">
                            <label htmlFor="amount" className="col-form-label"><h2>Amount</h2></label>
                            <input type="number" className="form-control" id="amount" aria-labelledby="amountHelpInline" />
                            <span id="amountHelpInline" className="form-text">
                                Amount to invest per zone
                            </span>
                        </div>
                        <div className="col">
                            <label htmlFor="amtSubZones" className="col-form-label"><h2>Amount of sub-zones</h2></label>
                            <input type="number" className="form-control" id="amtSubZones" aria-labelledby="amtSubZonesHelpInline" />
                            <span id="amtSubZonesHelpInline" className="form-text">
                                Amount of sub-zones within a major price zone
                            </span>
                        </div>
                    </div>
                    <div className="row g-2">
                        <h3>Prices</h3>
                    </div>
                    <div className="row gx-2">
                        {prices.map((price, i) => (
                            <div key={price.id} className="col-auto">
                                <div className="col-auto input-group gx-1 p-1 align-items-center bg-dark bg-opacity-10 border rounded">
                                    <Price value={price.value} step={tickerStep} onChange={(event) => onPriceChange(i, event)} />
                                    <button type="button" className="btn-close" aria-label="Close" onClick={(event) => removePrice(i, event)}></button>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="row gx-0">
                        <div className="col-auto">
                            <button type="submit" className="btn btn-primary" onClick={addPrice}>+</button>
                        </div>
                    </div>
                    <div className="row g-2 justify-content-center">
                        <div className="col-auto">
                            <button type="submit" className="btn btn-primary" onClick={createOperation}>Create</button>
                        </div>
                    </div>
                </form>
            </div>

            <table className="table">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Ticker</th>
                        <th scope="col">Amount (USDT)</th>
                        <th scope="col">Sub-Zones</th>
                        <th scope="col">Prices</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">1</th>
                        <td>BTCUSDT</td>
                        <td>$200</td>
                        <td>10</td>
                        <td>$27102.54, $27103.54, $27105.54, $27102.54, $27107.54</td>
                    </tr>
                </tbody>
            </table>
            <Message text={error} visible={isErrorVisible} onClose={hideError} />
        </div>
    );
}